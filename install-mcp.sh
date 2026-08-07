#!/usr/bin/env bash
# Copy the general MCP set into a target project (research/dev work).
set -euo pipefail
STACK="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${1:-$PWD}"
if [ -f "$TARGET/.mcp.json" ]; then echo "merge servers from $STACK/mcp/general.mcp.json into existing $TARGET/.mcp.json"; else cp "$STACK/mcp/general.mcp.json" "$TARGET/.mcp.json" && echo "copied general MCP set -> $TARGET"; fi
