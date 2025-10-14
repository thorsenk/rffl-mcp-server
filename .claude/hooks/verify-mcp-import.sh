#!/bin/bash
# Verifies that the MCP server can be imported successfully
# Used as post-Edit/Write hook to ensure server remains functional

set -e

# Only run if rffl_mcp_server.py was modified
if [[ "$FILE_PATH" == *"rffl_mcp_server.py"* ]]; then
    echo "🔍 Verifying MCP import..."

    if output=$(python3 -c "from rffl_mcp_server import mcp; print(f'✅ Server validated: {len(mcp._tools)} tools')" 2>&1); then
        echo "$output"
        afplay /System/Library/Sounds/Ping.aiff &
        exit 0
    else
        echo "❌ MCP import failed:"
        echo "$output"
        afplay /System/Library/Sounds/Basso.aiff &
        exit 1
    fi
fi

exit 0
