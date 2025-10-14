#!/bin/bash
# Validates Python syntax for rffl_mcp_server.py
# Used as pre-commit hook to catch syntax errors

set -e

echo "🔍 Validating Python syntax..."

if python3 -m py_compile rffl_mcp_server.py 2>&1; then
    echo "✅ Python syntax valid"
    afplay /System/Library/Sounds/Hero.aiff &
    exit 0
else
    echo "❌ Python syntax error detected in rffl_mcp_server.py"
    afplay /System/Library/Sounds/Basso.aiff &
    exit 1
fi
