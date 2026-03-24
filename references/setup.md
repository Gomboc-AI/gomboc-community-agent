# Setup Guide: Gomboc Community Edition

Complete step-by-step setup for using Gomboc with OpenClaw agents.

## 1. Create Gomboc Account

Visit [app.gomboc.ai](https://app.gomboc.ai) and sign up:

- **Email signup:** Enter email, name, organization
- **GitHub SSO:** Click "GitHub" and authorize `Gomboc-AI`

Free forever — no credit card required.

## 2. Generate Personal Access Token (PAT)

Once logged in:

1. Navigate to **Settings** → **Access Tokens**
2. Click **Create New Token**
3. Give it a name: `OpenClaw Agent`
4. Copy the token (you'll only see it once)
5. Save securely

Your token looks like: `gpt_abc123def456...`

## 3. Store Token Securely

### Option A: Environment Variable (Development)

```bash
# Add to your shell profile (.bashrc, .zshrc, etc.)
export GOMBOC_PAT="your-token-here"

# Verify
echo $GOMBOC_PAT
```

### Option B: GitHub Secrets (CI/CD)

For GitHub Actions workflows:

1. Go to your repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `GOMBOC_PAT`
4. Paste your token
5. Click **Add secret**

Reference in workflows:
```yaml
env:
  GOMBOC_PAT: ${{ secrets.GOMBOC_PAT }}
```

### Option C: 1Password / Vault (Production)

For teams, store in your secret manager:

```bash
# Example: 1Password
op read "op://vault/Gomboc/PAT"
export GOMBOC_PAT=$(op read "op://vault/Gomboc/PAT")
```

## 4. Install Docker (Required for MCP Server)

Gomboc's ORL engine runs in Docker. Install:

- **Mac:** [Docker Desktop](https://www.docker.com/products/docker-desktop)
- **Linux:** `sudo apt-get install docker.io` or `brew install docker`
- **Windows:** [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)

Verify:
```bash
docker --version
docker ps  # Should show running containers (even if empty)
```

## 5. Run Your First Scan

### Via CLI Wrapper (Local)

```bash
cd your-terraform-repo
python /path/to/gomboc-security-skill/scripts/cli-wrapper.py scan --path .
```

**Example output:**
```
🔍 Scanning terraform/ for security issues...
Found 5 issues:

[HIGH] S3 bucket missing encryption
  File: terraform/s3.tf:12
  Fix: Add server_side_encryption_configuration

[MEDIUM] Security group too permissive
  File: terraform/security.tf:8
  Fix: Restrict CIDR blocks to 10.0.0.0/8

...

✅ Scan complete
```

### Via MCP Server (Interactive)

```bash
# Terminal 1: Start the server
docker run -p 3100:3100 \
  -e GOMBOC_PAT='your-token' \
  gombocai/mcp:latest

# Terminal 2: Query from your agent
curl http://localhost:3100/api/scan \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"path": "./terraform", "format": "json"}'
```

## 6. Verify Setup

Run the verification script:

```bash
bash scripts/verify-setup.sh
```

Expected output:
```
✅ GOMBOC_PAT is set
✅ Docker is running
✅ Gomboc image is available (gombocai/mcp:latest)
✅ MCP server port 3100 is available
✅ All checks passed!
```

## 7. Integrate with Your Workflow

### For GitHub Actions:

Add to `.github/workflows/security.yml`:

```yaml
name: Security Remediation
on: [pull_request]

jobs:
  gomboc:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Scan with Gomboc
        env:
          GOMBOC_PAT: ${{ secrets.GOMBOC_PAT }}
        run: |
          python scripts/cli-wrapper.py scan --path terraform/
```

### For Agent Workflows:

See [mcp-integration.md](mcp-integration.md) for agent-specific setup.

## Troubleshooting

### "GOMBOC_PAT: command not found"

**Problem:** Environment variable not set

**Solution:**
```bash
export GOMBOC_PAT="your-token-here"
# OR
source ~/.bashrc  # Reload shell profile
```

### "Docker: command not found"

**Problem:** Docker not installed

**Solution:**
```bash
# Mac
brew install docker

# Linux
sudo apt-get install docker.io

# Windows
Download Docker Desktop from docker.com
```

### "Permission denied while trying to connect to Docker daemon"

**Problem:** Docker requires sudo or user needs to be in docker group

**Solution:**
```bash
# Add current user to docker group (Linux)
sudo usermod -aG docker $USER
newgrp docker  # Activate group

# Mac
Open Docker Desktop
```

### "Image gombocai/mcp:latest not found"

**Problem:** Docker image hasn't been pulled

**Solution:**
```bash
docker pull gombocai/mcp:latest
```

### "Port 3100 already in use"

**Problem:** Another service is using port 3100

**Solution:**
```bash
# Find process using port 3100
lsof -i :3100

# Kill it or use a different port
docker run -p 3101:3100 -e GOMBOC_PAT='token' gombocai/mcp:latest
```

## Next Steps

1. **Explore the CLI:**
   ```bash
   python scripts/cli-wrapper.py --help
   ```

2. **Read the MCP Integration Guide:**
   See [mcp-integration.md](mcp-integration.md)

3. **Setup GitHub Actions:**
   See [github-action.md](github-action.md)

4. **Check Gomboc Docs:**
   https://docs.gomboc.ai/getting-started-ce

---

**Need help?** Check [Gomboc's GitHub Discussions](https://github.com/Gomboc-AI/gomboc-ai-feedback/discussions) or create an issue in this skill's repo.
