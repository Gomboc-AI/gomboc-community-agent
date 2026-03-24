#!/usr/bin/env python3
"""
Gomboc Security CLI Wrapper

Local CLI tool for scanning and fixing infrastructure code with Gomboc.
Wraps MCP server calls into a simple command-line interface.

Usage:
    gomboc-security scan [options]      Scan for security issues
    gomboc-security fix [options]       Generate fixes
    gomboc-security remediate [options] Apply fixes to code
    gomboc-security config [options]    Show/manage configuration
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
import urllib.request
import urllib.error

# Config defaults
DEFAULT_MCP_URL = "http://localhost:3100"
DEFAULT_POLICY = "default"
DEFAULT_FORMAT = "json"
CONFIG_FILE = Path.home() / ".gomboc" / "config.json"


def get_mcp_url() -> str:
    """Get MCP server URL from env or config."""
    return os.getenv("GOMBOC_MCP_URL", DEFAULT_MCP_URL)


def get_pat() -> str:
    """Get Personal Access Token from env."""
    pat = os.getenv("GOMBOC_PAT")
    if not pat:
        raise RuntimeError(
            "GOMBOC_PAT not set. Set environment variable or run: gomboc-security config --set-token"
        )
    return pat


def mcp_call(tool: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Make MCP call to Gomboc server."""
    url = get_mcp_url()
    
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": f"gomboc.{tool}",
            "arguments": params
        },
        "id": 1
    }
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read())
            if "result" in result:
                return result["result"]
            elif "error" in result:
                raise RuntimeError(f"MCP Error: {result['error']}")
            return result
    except urllib.error.URLError as e:
        raise RuntimeError(
            f"Failed to connect to MCP server at {url}. "
            f"Is it running? Start with: docker run -p 3100:3100 -e GOMBOC_PAT='...' gombocai/mcp:latest"
        ) from e


def scan(args: argparse.Namespace) -> int:
    """Scan infrastructure code for security issues."""
    print(f"🔍 Scanning {args.path} with Gomboc...")
    
    params = {
        "path": args.path,
        "format": args.format,
        "policy": args.policy
    }
    
    if args.exclude_path:
        params["exclude"] = args.exclude_path
    
    try:
        result = mcp_call("scan", params)
    except Exception as e:
        print(f"❌ Scan failed: {e}", file=sys.stderr)
        return 1
    
    issue_count = result.get("issue_count", 0)
    
    # Output results
    if args.format == "json":
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"✅ Results saved to {args.output}")
        else:
            print(json.dumps(result, indent=2))
    
    elif args.format == "markdown":
        output = format_markdown_report(result)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"✅ Report saved to {args.output}")
        else:
            print(output)
    
    else:
        print(json.dumps(result, indent=2))
    
    print(f"\n📊 Found {issue_count} issues")
    
    # Exit codes
    if args.fail_on_severity:
        for issue in result.get("issues", []):
            if severity_level(issue.get("severity")) >= severity_level(args.fail_on_severity):
                if args.exit_code:
                    return 1
    
    return 0


def fix(args: argparse.Namespace) -> int:
    """Generate fixes for identified issues."""
    # First, run scan
    print(f"🔍 Scanning {args.path}...")
    scan_params = {
        "path": args.path,
        "policy": args.policy,
        "format": "json"
    }
    
    try:
        scan_result = mcp_call("scan", scan_params)
    except Exception as e:
        print(f"❌ Scan failed: {e}", file=sys.stderr)
        return 1
    
    scan_id = scan_result.get("scan_id")
    issue_count = scan_result.get("issue_count", 0)
    
    if issue_count == 0:
        print("✅ No issues found")
        return 0
    
    print(f"🔧 Generating fixes for {issue_count} issues...")
    
    fix_params = {
        "scan_id": scan_id,
        "output_format": args.format,
        "auto_apply": args.apply
    }
    
    try:
        result = mcp_call("fix", fix_params)
    except Exception as e:
        print(f"❌ Fix generation failed: {e}", file=sys.stderr)
        return 1
    
    fixes = result.get("fixes", [])
    
    # Output
    if args.format == "json":
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"✅ Fixes saved to {args.output}")
        else:
            print(json.dumps(result, indent=2))
    
    elif args.format == "markdown":
        output = format_fixes_markdown(result)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"✅ Fixes saved to {args.output}")
        else:
            print(output)
    
    print(f"\n✅ Generated {len(fixes)} fixes")
    
    if result.get("pull_request"):
        pr = result["pull_request"]
        print(f"📦 Pull Request: {pr['url']}")
    
    return 0


def remediate(args: argparse.Namespace) -> int:
    """Apply fixes directly to code."""
    print(f"🔧 Remediating {args.path}...")
    
    params = {
        "path": args.path,
        "commit": args.commit,
        "push": args.push
    }
    
    if args.fixes:
        params["fixes"] = args.fixes.split(",")
    
    try:
        result = mcp_call("remediate", params)
    except Exception as e:
        print(f"❌ Remediation failed: {e}", file=sys.stderr)
        return 1
    
    print(f"✅ Applied {len(result.get('fixes', []))} fixes")
    
    if args.commit:
        print("📝 Changes committed")
    if args.push:
        print("🚀 Pushed to remote")
    
    return 0


def config(args: argparse.Namespace) -> int:
    """Manage configuration."""
    CONFIG_FILE.parent.mkdir(exist_ok=True)
    
    if args.set_token:
        config_data = {}
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE) as f:
                config_data = json.load(f)
        
        config_data["pat"] = args.set_token
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config_data, f, indent=2)
        print(f"✅ Token saved to {CONFIG_FILE}")
        return 0
    
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            config_data = json.load(f)
        print(json.dumps(config_data, indent=2))
    else:
        print("No configuration found")
    
    return 0


def format_markdown_report(scan_result: Dict[str, Any]) -> str:
    """Format scan results as Markdown."""
    output = []
    output.append("# 🔒 Gomboc Security Scan Results\n")
    
    issue_count = scan_result.get("issue_count", 0)
    output.append(f"**Total Issues:** {issue_count}\n")
    
    issues_by_severity = {}
    for issue in scan_result.get("issues", []):
        severity = issue.get("severity", "UNKNOWN")
        if severity not in issues_by_severity:
            issues_by_severity[severity] = []
        issues_by_severity[severity].append(issue)
    
    for severity in ["HIGH", "MEDIUM", "LOW", "INFO"]:
        if severity in issues_by_severity:
            output.append(f"\n## {severity} Severity\n")
            for issue in issues_by_severity[severity]:
                output.append(f"### {issue['title']}\n")
                output.append(f"- **File:** `{issue['file']}` (line {issue.get('line', '?')})\n")
                output.append(f"- **Description:** {issue['description']}\n")
                output.append(f"- **Remediation:** {issue.get('remediation', 'N/A')}\n")
    
    return "".join(output)


def format_fixes_markdown(fix_result: Dict[str, Any]) -> str:
    """Format fix results as Markdown."""
    output = []
    output.append("# 🔧 Gomboc Fixes\n")
    
    fixes = fix_result.get("fixes", [])
    output.append(f"**Generated {len(fixes)} fixes**\n")
    
    for fix in fixes:
        output.append(f"\n## {fix['title']}\n")
        output.append(f"- **Confidence:** {fix.get('confidence', 0)}%\n")
        output.append(f"- **File:** `{fix['file']}`\n")
        output.append(f"- **Status:** {fix.get('status', 'unknown')}\n")
        if fix.get('code'):
            output.append(f"\n```hcl\n{fix['code']}\n```\n")
    
    if fix_result.get("pull_request"):
        pr = fix_result["pull_request"]
        output.append(f"\n## Pull Request\n")
        output.append(f"- **Title:** {pr['title']}\n")
        output.append(f"- **URL:** {pr['url']}\n")
    
    return "".join(output)


def severity_level(severity: str) -> int:
    """Convert severity to numeric level for comparison."""
    levels = {"INFO": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
    return levels.get(severity, -1)


def main():
    parser = argparse.ArgumentParser(
        description="Gomboc Security Remediation CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  gomboc-security scan --path terraform/
  gomboc-security scan --path . --format markdown --output report.md
  gomboc-security fix --path terraform/ --apply
  gomboc-security config --set-token gpt_abc123...
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Scan for security issues")
    scan_parser.add_argument("--path", default=".", help="Path to scan")
    scan_parser.add_argument("--format", default=DEFAULT_FORMAT, 
                           choices=["json", "markdown", "sarif"],
                           help="Output format")
    scan_parser.add_argument("--policy", default=DEFAULT_POLICY,
                           help="Security policy to apply")
    scan_parser.add_argument("--exclude-path", help="Paths to exclude (glob)")
    scan_parser.add_argument("--output", help="Save output to file")
    scan_parser.add_argument("--fail-on-severity", 
                           choices=["INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"],
                           help="Exit with code 1 if issues of this severity found")
    scan_parser.add_argument("--exit-code", action="store_true",
                           help="Exit with non-zero if issues found")
    scan_parser.set_defaults(func=scan)
    
    # Fix command
    fix_parser = subparsers.add_parser("fix", help="Generate and apply fixes")
    fix_parser.add_argument("--path", default=".", help="Path to fix")
    fix_parser.add_argument("--policy", default=DEFAULT_POLICY,
                          help="Security policy to apply")
    fix_parser.add_argument("--format", default="pull_request",
                          choices=["pull_request", "patch", "json"],
                          help="Output format")
    fix_parser.add_argument("--apply", action="store_true",
                          help="Apply fixes automatically")
    fix_parser.add_argument("--output", help="Save output to file")
    fix_parser.set_defaults(func=fix)
    
    # Remediate command
    remediate_parser = subparsers.add_parser("remediate", help="Apply fixes to code")
    remediate_parser.add_argument("--path", default=".", help="Path to remediate")
    remediate_parser.add_argument("--fixes", help="Specific fix IDs to apply (comma-separated)")
    remediate_parser.add_argument("--commit", action="store_true",
                               help="Auto-commit after fixing")
    remediate_parser.add_argument("--push", action="store_true",
                               help="Push to remote after commit")
    remediate_parser.set_defaults(func=remediate)
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Manage configuration")
    config_parser.add_argument("--set-token", help="Set Personal Access Token")
    config_parser.set_defaults(func=config)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
