# Gomboc Security Skill — Integration Guide for Agents

**Purpose:** Show agents (like yourself) how to use this skill to automate security scanning and remediation.

---

## What You Get

A production-ready **ClawHub skill** that wraps Gomboc.ai Community Edition into agent workflows.

**In the Box:**
- ✅ Full MCP server integration (scan, fix, remediate)
- ✅ CLI tool for local use
- ✅ GitHub Actions workflows
- ✅ Docker Compose stack
- ✅ Comprehensive documentation
- ✅ Example vulnerable code + test cases

**What It Does:**
1. **Scan** infrastructure code (Terraform, CloudFormation, IaC)
2. **Generate** deterministic, merge-ready security fixes
3. **Apply** fixes via PR, patch, or direct code updates
4. **Report** findings in multiple formats (JSON, Markdown, SARIF)

---

## Quick Setup (5 minutes)

### 1. Get a Gomboc Token

```bash
# Visit app.gomboc.ai and sign up (free forever, no CC needed)
# Generate a Personal Access Token
# Copy it and set:
export GOMBOC_PAT="gpt_your_token_here"
```

### 2. Start the MCP Server

```bash
# Option A: Docker directly
docker run -p 3100:3100 \
  -e GOMBOC_PAT='$GOMBOC_PAT' \
  gombocai/mcp:latest

# Option B: Docker Compose (easier)
cd scripts
docker-compose up -d
```

### 3. Verify It's Running

```bash
curl http://localhost:3100/health
# Response: {"status": "ok"}
```

### 4. Test the CLI

```bash
python scripts/cli-wrapper.py scan --path examples/ --format markdown
# Should show 5+ security issues found
```

---

## Three Ways to Use This Skill

### Option 1: CLI (Local Scanning)

**Best for:** Quick scans, pre-commit checks, developers

```bash
# Scan Terraform
python scripts/cli-wrapper.py scan --path ./terraform --format markdown

# Generate fixes
python scripts/cli-wrapper.py fix --path ./terraform

# Apply fixes
python scripts/cli-wrapper.py fix --path ./terraform --apply
```

**Output:** JSON, Markdown, or SARIF reports

---

### Option 2: MCP (Interactive Agents)

**Best for:** AI agents, continuous remediation, workflows

```python
# Pseudocode: How agents use this skill

# 1. Load the skill
agent.load_skill("gomboc-security")

# 2. Scan infrastructure
scan_result = agent.use_mcp_tool("gomboc", "scan", {
    "path": "./infrastructure",
    "policy": "aws-cis",
    "format": "json"
})

# 3. Check results
if scan_result.issue_count > 0:
    print(f"Found {scan_result.issue_count} security issues")
    
    # 4. Generate fixes
    fixes = agent.use_mcp_tool("gomboc", "fix", {
        "scan_id": scan_result.id,
        "output_format": "pull_request",
        "auto_apply": False  # Don't apply yet
    })
    
    # 5. Request human approval
    agent.request_approval({
        "type": "security_fix_approval",
        "pr_url": fixes.pull_request.url,
        "fixes_count": len(fixes.fixes),
        "message": f"Generated {len(fixes.fixes)} security fixes"
    })
    
    # 6. On approval, merge the PR
    if agent.get_approval():
        agent.merge_pull_request(fixes.pull_request.url)
```

**Available MCP Tools:**

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| `gomboc.scan` | Identify issues | path, policy, format | scan_id, issues, issue_count |
| `gomboc.fix` | Generate fixes | scan_id, output_format, auto_apply | fixes, pull_request |
| `gomboc.remediate` | Apply fixes | path, fixes, commit, push | applied_fixes |

---

### Option 3: CI/CD (GitHub Actions)

**Best for:** Automated PR reviews, continuous scanning

```yaml
# .github/workflows/security-scan.yml
name: Gomboc Security Scan

on:
  pull_request:
    paths:
      - 'terraform/**'
      - 'cloudformation/**'

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Scan with Gomboc
        env:
          GOMBOC_PAT: ${{ secrets.GOMBOC_PAT }}
        run: |
          python scripts/cli-wrapper.py scan \
            --path terraform/ \
            --format markdown \
            --output scan-report.md \
            --fail-on-severity HIGH
      
      - name: Comment on PR
        if: always()
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const report = fs.readFileSync('scan-report.md', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '## 🔒 Security Scan\n\n' + report
            });
```

---

## Agent Integration Patterns

### Pattern 1: Pre-Commit Hook

Block commits if security issues found:

```python
# On pre-commit event
def on_pre_commit(files):
    scan = agent.use_mcp_tool("gomboc", "scan", {"path": "."})
    
    if scan.issue_count > 0:
        agent.block_commit({
            "message": f"Found {scan.issue_count} security issues. Run: gomboc-security fix --path . --apply"
        })
        return False
    
    agent.allow_commit()
    return True
```

### Pattern 2: Continuous Remediation

Auto-fix issues on schedule:

```python
# Runs hourly
def remediate_periodically():
    while True:
        scan = agent.use_mcp_tool("gomboc", "scan", {"path": "./infrastructure"})
        
        if scan.issue_count > 0:
            # Auto-fix
            agent.use_mcp_tool("gomboc", "remediate", {
                "path": "./infrastructure",
                "commit": True,
                "push": True
            })
            
            agent.notify_slack(f"Fixed {scan.issue_count} security issues in infrastructure")
        
        sleep(3600)  # Run hourly
```

### Pattern 3: Pull Request Review

Scan PRs and comment with findings:

```python
# On PR created
def on_pull_request_created(pr):
    # Get changed files
    changed_files = pr.get_changed_files()
    iac_files = [f for f in changed_files if is_iac(f)]
    
    if not iac_files:
        return  # Skip if no IaC changes
    
    # Scan
    scan = agent.use_mcp_tool("gomboc", "scan", {
        "path": ".",
        "policy": "default"
    })
    
    # Report
    if scan.issue_count > 0:
        pr.create_comment(format_scan_report(scan))
        
        # Create fix PR if requested
        if pr.labels.contains("auto-fix"):
            fixes = agent.use_mcp_tool("gomboc", "fix", {
                "scan_id": scan.id,
                "output_format": "pull_request"
            })
            pr.create_comment(f"Fixes available: {fixes.pull_request.url}")
```

---

## Configuration

### Via Environment Variables

```bash
export GOMBOC_PAT="your-token"
export GOMBOC_MCP_URL="http://localhost:3100"
export GOMBOC_POLICY="aws-cis"
export GOMBOC_AUTO_FIX="false"
```

### Via Config File

Create `.gomboc-agent.yml` in your repo:

```yaml
mcp:
  url: "http://localhost:3100"
  timeout: 30

gomboc:
  pat: "${GOMBOC_PAT}"  # From environment
  policy: "aws-cis"
  auto_fix: false

scan:
  paths:
    - "terraform/**"
    - "cloudformation/**"
  exclude:
    - "vendor/**"
    - ".terraform/**"

fix:
  output_format: "pull_request"
  create_branch: true
  branch_prefix: "gomboc/fix/"
```

---

## Common Use Cases

### Use Case 1: Security Team

**Goal:** Enforce security standards across all IaC repos

**Implementation:**
1. Deploy MCP server to VPC
2. Configure GitHub App for automated scanning
3. Set PR branch protection: require "gomboc-security-scan" to pass
4. Auto-remediate on schedule or manually

**Result:** Zero unreviewed security issues in production code

### Use Case 2: Platform Engineering

**Goal:** Automatically fix misconfigurations as they're detected

**Implementation:**
1. Run agent with continuous remediation loop
2. Scan every 6 hours
3. Auto-fix issues automatically
4. Push fixes and notify Slack
5. Create metrics dashboard

**Result:** MTTR reduced from weeks to minutes

### Use Case 3: Compliance

**Goal:** Maintain CIS AWS Foundations Benchmark compliance

**Implementation:**
1. Set policy to "aws-cis"
2. Daily scan of all infrastructure
3. Auto-generate compliance reports
4. Alert on policy violations

**Result:** Auditable trail of compliance checks and fixes

### Use Case 4: Developer Workflow

**Goal:** Shift security left — catch issues before PR

**Implementation:**
1. Install CLI locally or in IDE
2. Run `gomboc-security scan --path .` before committing
3. Apply fixes with one command
4. Push with confidence

**Result:** Developers catch & fix issues immediately

---

## API Reference

### MCP Tool: `gomboc.scan`

**Input:**
```json
{
  "path": "./terraform",           // Required: Path to scan
  "format": "json",                // Optional: json|markdown|sarif
  "policy": "default",             // Optional: default|aws-cis|etc
  "exclude": ["vendor/**"]         // Optional: Glob patterns to exclude
}
```

**Output:**
```json
{
  "scan_id": "scan_abc123",
  "path": "./terraform",
  "issues": [
    {
      "id": "issue_1",
      "severity": "HIGH",
      "title": "S3 Bucket Missing Encryption",
      "file": "s3.tf",
      "line": 12,
      "description": "...",
      "remediation": "..."
    }
  ],
  "issue_count": 5,
  "confidence": 0.94
}
```

### MCP Tool: `gomboc.fix`

**Input:**
```json
{
  "scan_id": "scan_abc123",           // Required: From scan result
  "output_format": "pull_request",    // Optional: pull_request|patch|code
  "auto_apply": false                 // Optional: Apply immediately?
}
```

**Output:**
```json
{
  "fixes": [
    {
      "id": "fix_1",
      "issue_id": "issue_1",
      "title": "Enable S3 Encryption at Rest",
      "file": "s3.tf",
      "code": "resource \"aws_s3_bucket_server_side_encryption_configuration\" { ... }",
      "confidence": 0.96,
      "status": "ready_to_review"
    }
  ],
  "pull_request": {
    "url": "https://github.com/org/repo/pull/123",
    "title": "Security: Auto-remediate infrastructure issues",
    "description": "5 security fixes generated by Gomboc ORL Engine"
  }
}
```

### MCP Tool: `gomboc.remediate`

**Input:**
```json
{
  "path": "./terraform",     // Required: Path to fix
  "fixes": ["fix_1", "fix_2"],  // Optional: Specific fix IDs
  "commit": true,            // Optional: Auto-commit?
  "push": false              // Optional: Push to remote?
}
```

**Output:**
```json
{
  "fixes": [
    {
      "id": "fix_1",
      "status": "applied",
      "file": "s3.tf"
    }
  ],
  "commit": "abc123def",
  "branch": "main"
}
```

---

## Error Handling

### Common Errors & Solutions

```python
# Error: "GOMBOC_PAT not set"
try:
    scan = agent.use_mcp_tool("gomboc", "scan", {"path": "."})
except RuntimeError as e:
    if "GOMBOC_PAT" in str(e):
        agent.log("Set GOMBOC_PAT environment variable")
        agent.request_human_input("Enter your Gomboc PAT")

# Error: "MCP server not responding"
try:
    scan = agent.use_mcp_tool("gomboc", "scan", {"path": "."})
except ConnectionError:
    agent.log("Gomboc MCP server not available")
    agent.fallback_to_local_cli()

# Error: "No issues found"
scan = agent.use_mcp_tool("gomboc", "scan", {"path": "."})
if scan.issue_count == 0:
    agent.log("All checks passed ✅")
else:
    agent.log(f"Found {scan.issue_count} issues")
```

---

## Performance Tips

1. **Batch Scans** — Scan entire directory, not individual files
2. **Reuse Results** — Don't rescan; use scan_id for multiple fixes
3. **Cache Results** — Store results for 1+ hour to avoid redundant scans
4. **Parallelize** — Run multi-environment scans in parallel

---

## Next Steps

1. **Read SKILL.md** for complete documentation
2. **Follow setup.md** for authentication
3. **Test with examples/** directory
4. **Integrate into your workflow** (CLI, MCP, or GitHub Actions)
5. **Report feedback** via GitHub Issues

---

## Support

- **Gomboc Documentation:** https://docs.gomboc.ai
- **This Skill:** See SKILL.md and references/
- **GitHub Issues:** Report bugs and feature requests
- **Gomboc Discussions:** https://github.com/Gomboc-AI/gomboc-ai-feedback/discussions

---

**Happy scanning! 🔒**

Built with ❤️ by OpenClaw | Powered by Gomboc.ai Community Edition
