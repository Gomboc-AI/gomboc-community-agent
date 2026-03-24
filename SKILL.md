# Gomboc Security Remediation Skill

**Deterministic, merge-ready security fixes for your infrastructure code.**

Gomboc.ai Community Edition automatically scans and fixes security misconfigurations in Terraform, CloudFormation, and IaC using deterministic AI (no hallucinations). This skill wraps Gomboc's power into agent workflows, CI/CD pipelines, and interactive coding sessions.

## What It Does

- **Scan** infrastructure code for security issues (IaC, Terraform, CloudFormation)
- **Generate** deterministic, merge-ready pull requests with fixes
- **Remediate** continuously via GitHub Actions or interactive MCP
- **Trust** 94%+ fix acceptance rate with zero hallucinations (ORL Engine)

## Quick Start

### 1. **Setup Gomboc Account & Token**

```bash
# Visit app.gomboc.ai to sign up (free forever, no credit card)
# Generate a Personal Access Token (PAT)
# Save it as GOMBOC_PAT environment variable
export GOMBOC_PAT="your-personal-token-here"
```

See [setup.md](references/setup.md) for detailed instructions.

### 2. **Choose Your Integration Path**

#### **Interactive (AI Agents)**
Use the Gomboc MCP Server to interact with security scanning in your agent workflows:

```bash
# Start the MCP server locally
docker run -p 3100:3100 \
  -e GOMBOC_PAT='$GOMBOC_PAT' \
  gombocai/mcp:latest
```

See [mcp-integration.md](references/mcp-integration.md) for agent usage patterns.

#### **CI/CD (Automated)**
Add Gomboc scanning to your GitHub Actions pipeline:

```yaml
# Add to your GitHub Actions workflow
- uses: gomboc-ai/gomboc-action@v1
  with:
    gomboc-pat: ${{ secrets.GOMBOC_PAT }}
    paths: 'terraform/**'
```

See [github-action.md](references/github-action.md) for full workflow setup.

#### **Local CLI**
Scan and fix files locally before committing:

```bash
python scripts/cli-wrapper.py scan --path ./terraform
python scripts/cli-wrapper.py fix --path ./terraform --apply
```

See [cli-wrapper.py](scripts/cli-wrapper.py) for all options.

## How It Works

```
Infrastructure Code
       ↓
    [SCAN] - Identify security issues via ORL
       ↓
   [ANALYZE] - Determine correct fixes with full context
       ↓
  [GENERATE] - Create deterministic, standards-aligned code
       ↓
 [DELIVER] - Merge-ready PRs or local fixes
```

## Key Features

| Feature | Benefit |
|---------|---------|
| **Deterministic AI (ORL Engine)** | No hallucinations, same fix every time for the same issue |
| **94%+ Acceptance Rate** | Fixes are merge-ready; engineers trust them |
| **Continuous Remediation** | Integrates into CI/CD for ongoing security |
| **Context-Aware** | Understands your entire architecture, not just single files |
| **Standards-Aligned** | Fixes follow security best practices (CIS, NIST) |
| **Free Community Edition** | No cost for individual developers & small teams |

## Supported Languages & Frameworks

- **Terraform** (primary)
- **CloudFormation** (AWS)
- **Kubernetes YAML** (limited)
- **General IaC** (configuration files)

> More languages and frameworks added regularly. Check [Gomboc docs](https://docs.gomboc.ai) for latest support.

## Use Cases

### 1. **Developer Workflow**
Run local scans before committing:
```bash
# Scan your current branch
python scripts/cli-wrapper.py scan --path . --format json

# Apply recommended fixes
python scripts/cli-wrapper.py fix --path . --apply
```

### 2. **CI/CD Pipeline**
Add automated remediation to pull requests:
```yaml
# .github/workflows/security.yml
name: Security Remediation
on: [pull_request]
jobs:
  gomboc:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: gomboc-ai/gomboc-action@v1
        with:
          gomboc-pat: ${{ secrets.GOMBOC_PAT }}
```

### 3. **Agent-Driven Development**
Let AI agents scan and remediate code interactively:
```python
# Agents interact with Gomboc via MCP
agent.use_mcp_tool("gomboc", "scan", {
    "path": "./infrastructure/main.tf",
    "policy": "default"
})

agent.use_mcp_tool("gomboc", "fix", {
    "scan_id": "scan_123",
    "output_format": "pull_request"
})
```

## Files & References

- **[setup.md](references/setup.md)** — Account setup, authentication, first scan
- **[mcp-integration.md](references/mcp-integration.md)** — MCP server config, agent usage patterns
- **[github-action.md](references/github-action.md)** — GitHub Actions workflow templates
- **[cli-wrapper.py](scripts/cli-wrapper.py)** — Python CLI tool for local scanning & fixing
- **[docker-compose.yml](scripts/docker-compose.yml)** — Docker Compose stack (MCP + local engine)

## Examples

### Example 1: Scan Vulnerable Terraform

```hcl
# main.tf - has security issues
resource "aws_s3_bucket" "my_bucket" {
  bucket = "my-insecure-bucket"
  # Missing: acl, versioning, encryption
}

resource "aws_security_group" "web" {
  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # ⚠️ Too permissive
  }
}
```

**Run scan:**
```bash
python scripts/cli-wrapper.py scan --path main.tf
```

**Output:**
```
[ISSUE] S3 bucket missing encryption at rest
[FIX]   Add server_side_encryption_configuration block
[ISSUE] Security group allows all inbound traffic
[FIX]   Restrict CIDR blocks to known IPs
```

### Example 2: Interactive Agent Session

```python
from gomboc_mcp_client import GombocClient

# Initialize agent with Gomboc MCP
client = GombocClient(
    mcp_url="http://localhost:3100",
    gomboc_pat=os.getenv("GOMBOC_PAT")
)

# Scan infrastructure
scan = client.scan("./terraform/prod/main.tf")
print(f"Found {scan.issue_count} issues")

# Generate fixes
fixes = client.fix(scan.id, auto_apply=False)
for fix in fixes:
    print(f"✓ {fix.title}: {fix.description}")
    print(f"  Confidence: {fix.confidence}%")
```

### Example 3: GitHub Actions Auto-Remediation

```yaml
name: Auto-Remediate IaC
on:
  pull_request:
    paths:
      - 'terraform/**'
      - 'cloudformation/**'

jobs:
  remediate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Scan with Gomboc
        uses: gomboc-ai/gomboc-action@v1
        with:
          gomboc-pat: ${{ secrets.GOMBOC_PAT }}
          paths: 'terraform/**'
          auto-fix: true
          
      - name: Push fixes
        if: steps.remediate.outputs.fixed == 'true'
        run: |
          git config user.name "Gomboc Bot"
          git config user.email "bot@gomboc.ai"
          git add terraform/
          git commit -m "Security: Auto-remediate IaC issues"
          git push
```

## Authentication

Gomboc uses Personal Access Tokens (PAT) for authentication:

1. Sign up at [app.gomboc.ai](https://app.gomboc.ai)
2. Generate a PAT in your account settings
3. Store securely (GitHub Secrets, env var, 1Password, etc.)
4. Reference as `GOMBOC_PAT` in your environment

See [setup.md](references/setup.md) for step-by-step guide.

## Configuration

Gomboc respects a `.gomboc.yml` config file in your repo:

```yaml
# .gomboc.yml
version: "1.0"

scan:
  # Paths to scan (glob patterns)
  paths:
    - "terraform/**/*.tf"
    - "!terraform/modules/vendor/**"
  
  # Exclude specific checks
  exclude_checks:
    - "encryption-disabled"
  
  # Security policies to apply
  policies:
    - "default"
    - "aws-cis"

fix:
  # Auto-apply fixes (use with caution)
  auto_apply: false
  
  # Output format: pull_request, patch, json
  output_format: "pull_request"
  
  # Branch for fix PRs
  branch_prefix: "gomboc/fix/"
```

## Troubleshooting

### "Docker not running" (VS Code Extension)
**Error:** MCP server won't start without Docker

**Fix:** Start Docker Desktop or Docker Engine before scanning
```bash
docker ps  # Verify Docker is running
```

### "GOMBOC_PAT invalid"
**Error:** Authentication fails

**Fix:** Regenerate PAT at [app.gomboc.ai](https://app.gomboc.ai/settings/tokens)
```bash
export GOMBOC_PAT="your-new-token"
docker run -p 3100:3100 -e GOMBOC_PAT='$GOMBOC_PAT' gombocai/mcp:latest
```

### "No issues found" (but you know there are)
**Reason:** Gomboc scans specific file types (`.tf`, `.json` for IaC)

**Fix:** Ensure your files have correct extensions and are in scanned paths
```bash
# Check your .gomboc.yml paths
python scripts/cli-wrapper.py scan --path . --verbose
```

## Contributing & Feedback

Found a bug? Have a feature request? Check out [Gomboc's GitHub Discussions](https://github.com/Gomboc-AI/gomboc-ai-feedback/discussions).

## License

This skill wraps Gomboc Community Edition, which is **free forever** under their community license. See [Gomboc Terms](https://www.gomboc.ai/terms) for details.

## Support & Resources

- **Gomboc Docs:** https://docs.gomboc.ai
- **Community Edition Setup:** https://docs.gomboc.ai/getting-started-ce
- **MCP Server Docs:** https://docs.gomboc.ai/integrations/mcp-server
- **GitHub Discussions:** https://github.com/Gomboc-AI/gomboc-ai-feedback/discussions
- **OpenClaw Docs:** https://docs.openclaw.ai

---

**Built by:** Gomboc Team + OpenClaw Community  
**Last Updated:** 2026-03-24  
**Status:** Beta (Community Edition)
