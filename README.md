# Gomboc Security Remediation Skill

**Deterministic, merge-ready security fixes for infrastructure code — powered by Gomboc.ai Community Edition.**

[![ClawHub](https://img.shields.io/badge/clawhub-skill-blue)](https://clawhub.com)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Status](https://img.shields.io/badge/status-beta-orange)](./CHANGELOG.md)

## Quick Start

```bash
# 1. Sign up at app.gomboc.ai and generate a token
export GOMBOC_PAT="your-token-here"

# 2. Start the MCP server
docker run -p 3100:3100 -e GOMBOC_PAT='$GOMBOC_PAT' gombocai/mcp:latest

# 3. Scan your infrastructure
python scripts/cli-wrapper.py scan --path ./terraform --format markdown

# 4. Generate fixes
python scripts/cli-wrapper.py fix --path ./terraform
```

## What Is This?

This is an **AgentSkill** for [OpenClaw](https://openclaw.ai) that wraps **Gomboc.ai Community Edition** — a free, deterministic AI code security remediation platform.

**Gomboc features:**
- ✅ **Deterministic Fixes** — No hallucinations, same fix every time
- ✅ **94%+ Acceptance Rate** — Merge-ready pull requests
- ✅ **IaC Focused** — Terraform, CloudFormation, Kubernetes
- ✅ **Free Forever** — Community Edition has no cost
- ✅ **ORL Engine** — Industry's most accurate infrastructure fixes

## Use Cases

### 1. **Agent-Driven Development**
Let AI agents scan and remediate code continuously:
```python
agent.scan_with_gomboc("./terraform")
agent.generate_pr_with_fixes()
```

### 2. **CI/CD Pipeline**
Automate security scanning on every PR:
```yaml
- uses: gomboc-ai/gomboc-action@v1
  with:
    gomboc-pat: ${{ secrets.GOMBOC_PAT }}
    auto-fix: true
```

### 3. **Developer Workflow**
Quick local scans before committing:
```bash
gomboc-security scan --path . --fail-on-severity HIGH
```

## Installation

### Option 1: Via ClawHub (Recommended)

```bash
clawhub install clawhub-gomboc-security
```

### Option 2: Manual Setup

1. Clone the repo
2. Set `GOMBOC_PAT` environment variable
3. Start the MCP server (see Quick Start above)
4. Use the CLI tool or integrate with your workflow

## File Structure

```
.
├── SKILL.md                           # Main documentation
├── README.md                          # This file
├── references/
│   ├── setup.md                       # Account setup & auth
│   ├── mcp-integration.md             # Agent integration guide
│   ├── github-action.md               # CI/CD workflow examples
├── scripts/
│   ├── cli-wrapper.py                 # CLI tool for scanning/fixing
│   ├── docker-compose.yml             # Docker Compose stack
│   ├── verify-setup.sh                # Verification script
├── examples/
│   ├── vulnerable.tf                  # Example Terraform with issues
└── LICENSE
```

## Key Documentation

- **[SKILL.md](SKILL.md)** — Full skill documentation, features, and examples
- **[references/setup.md](references/setup.md)** — Account creation, token generation
- **[references/mcp-integration.md](references/mcp-integration.md)** — Agent integration patterns
- **[references/github-action.md](references/github-action.md)** — GitHub Actions workflows

## Quick Examples

### Scan Infrastructure
```bash
# Scan and save results
python scripts/cli-wrapper.py scan --path terraform/ --output results.json

# Generate markdown report
python scripts/cli-wrapper.py scan --path terraform/ --format markdown --output report.md

# Fail on HIGH severity issues
python scripts/cli-wrapper.py scan --path terraform/ --fail-on-severity HIGH --exit-code
```

### Generate Fixes
```bash
# Generate fixes without applying
python scripts/cli-wrapper.py fix --path terraform/ --format pull_request

# Apply fixes directly
python scripts/cli-wrapper.py fix --path terraform/ --apply
```

### Interactive (Agent)
```python
from gomboc_mcp_client import GombocClient

client = GombocClient(mcp_url="http://localhost:3100")
scan = client.scan("./terraform")
print(f"Found {scan.issue_count} issues")

fixes = client.fix(scan.id)
for fix in fixes:
    print(f"✓ {fix.title} ({fix.confidence}% confidence)")
```

## Testing

Try it with the example vulnerable Terraform:

```bash
python scripts/cli-wrapper.py scan --path examples/ --format markdown

# Expected: 5+ security issues found
```

## Troubleshooting

### "Docker not running"
```bash
docker ps  # Verify Docker is running
# Start Docker Desktop or: sudo systemctl start docker
```

### "GOMBOC_PAT not found"
```bash
export GOMBOC_PAT="your-token-from-app.gomboc.ai"
```

### "Port 3100 already in use"
```bash
# Use a different port
docker run -p 3101:3100 -e GOMBOC_PAT='$GOMBOC_PAT' gombocai/mcp:latest

# Then update MCP_URL
export GOMBOC_MCP_URL="http://localhost:3101"
```

See **[references/setup.md](references/setup.md)** for more troubleshooting.

## Authentication

Gomboc uses Personal Access Tokens (PAT):

1. Sign up at [app.gomboc.ai](https://app.gomboc.ai) (free, no credit card)
2. Generate a PAT in account settings
3. Set as environment variable: `export GOMBOC_PAT="..."`

Details: [setup.md](references/setup.md)

## Supported Languages

- **Terraform** (primary support)
- **CloudFormation** (AWS)
- **Kubernetes** (limited)
- **Generic IaC** (JSON, YAML)

More added regularly. Check [Gomboc docs](https://docs.gomboc.ai) for latest.

## Integration Examples

### GitHub Actions
```yaml
on: [pull_request]
jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Scan with Gomboc
        env:
          GOMBOC_PAT: ${{ secrets.GOMBOC_PAT }}
        run: |
          python scripts/cli-wrapper.py scan --path terraform/ --fail-on-severity HIGH
```

### OpenClaw Agent
```python
agent.load_skill("gomboc-security")
scan_result = agent.use_mcp_tool("gomboc", "scan", {"path": "./terraform"})
```

See [references/github-action.md](references/github-action.md) for more examples.

## Performance

- **Scan speed:** ~1-5 seconds per 100 Terraform files (depends on complexity)
- **Fix generation:** ~2-10 seconds per scan
- **Docker overhead:** ~500MB RAM, requires Docker installed

## License

This skill wraps Gomboc Community Edition, which is **free forever** under their community license.

- Gomboc Terms: https://www.gomboc.ai/terms
- This skill: MIT License (see LICENSE file)

## Contributing

Found a bug? Have a feature request?

1. Check [Gomboc GitHub Discussions](https://github.com/Gomboc-AI/gomboc-ai-feedback/discussions)
2. File an issue in this repo
3. Submit a PR with improvements

## Support

- **Gomboc Docs:** https://docs.gomboc.ai
- **Community Edition:** https://docs.gomboc.ai/getting-started-ce
- **GitHub Discussions:** https://github.com/Gomboc-AI/gomboc-ai-feedback/discussions
- **OpenClaw Docs:** https://docs.openclaw.ai

## Roadmap

- [ ] GitHub App integration for auto-remediation
- [ ] VS Code extension wrapper
- [ ] Slack notifications for findings
- [ ] Cost estimation for fixes
- [ ] Multi-cloud policy templates (AWS, GCP, Azure)
- [ ] Custom policy editor

## Credits

Built with:
- [Gomboc.ai](https://www.gomboc.ai) — AI Code Security
- [OpenClaw](https://openclaw.ai) — Agent Infrastructure
- [Model Context Protocol](https://modelcontextprotocol.io) — MCP Standard

---

**Status:** Beta | **Last Updated:** 2026-03-24 | **Maintainer:** OpenClaw Community
