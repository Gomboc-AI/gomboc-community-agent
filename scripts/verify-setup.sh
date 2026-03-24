#!/bin/bash

# Gomboc Setup Verification Script
# Checks prerequisites and configuration for using Gomboc

set -e

PASS="✅"
FAIL="❌"
WARN="⚠️"

echo "🔍 Verifying Gomboc setup..."
echo ""

# Check GOMBOC_PAT
if [ -z "$GOMBOC_PAT" ]; then
    echo "$FAIL GOMBOC_PAT is not set"
    echo "   Set it with: export GOMBOC_PAT='your-token-here'"
else
    echo "$PASS GOMBOC_PAT is set"
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "$FAIL Docker is not installed"
    echo "   Install from: https://www.docker.com/products/docker-desktop"
else
    echo "$PASS Docker is installed"
    
    # Check if Docker daemon is running
    if ! docker ps &> /dev/null; then
        echo "$FAIL Docker daemon is not running"
        echo "   Start Docker Desktop or Docker Engine"
    else
        echo "$PASS Docker daemon is running"
    fi
    
    # Check if Gomboc image is available
    if docker image inspect gombocai/mcp:latest &> /dev/null; then
        echo "$PASS Gomboc MCP image is available locally"
    else
        echo "$WARN Gomboc MCP image not found locally"
        echo "   It will be pulled automatically on first run"
    fi
fi

# Check port 3100 availability
if command -v lsof &> /dev/null; then
    if ! lsof -i :3100 &> /dev/null; then
        echo "$PASS Port 3100 is available"
    else
        echo "$WARN Port 3100 is already in use"
        echo "   Use a different port or stop the existing service"
    fi
else
    echo "$WARN lsof not found, skipping port check"
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "$FAIL Python 3 is not installed"
else
    echo "$PASS Python 3 is installed"
    
    # Check required packages
    if python3 -c "import urllib.request" 2>/dev/null; then
        echo "$PASS Required Python modules are available"
    else
        echo "$WARN Some Python modules may be missing"
    fi
fi

# Check CLI script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [ -f "$SCRIPT_DIR/cli-wrapper.py" ]; then
    echo "$PASS CLI wrapper script found"
    
    if [ -x "$SCRIPT_DIR/cli-wrapper.py" ]; then
        echo "$PASS CLI wrapper is executable"
    else
        echo "$WARN CLI wrapper is not executable"
        echo "   Make it executable with: chmod +x $SCRIPT_DIR/cli-wrapper.py"
    fi
else
    echo "$FAIL CLI wrapper script not found"
fi

echo ""
echo "✅ Setup verification complete"
echo ""
echo "Next steps:"
echo "1. Start the MCP server: docker-compose up -d"
echo "2. Verify server is running: curl http://localhost:3100/health"
echo "3. Run a scan: python3 scripts/cli-wrapper.py scan --path ."
