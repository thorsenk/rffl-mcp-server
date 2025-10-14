#!/bin/bash
# Prevents committing .env files with secrets
# Used as pre-Bash hook for git add/commit commands

set -e

# Check if this is a git add or git commit command
if [[ "$COMMAND" =~ "git add" ]] || [[ "$COMMAND" =~ "git commit" ]]; then
    # Check if any .env files are staged
    if git diff --cached --name-only 2>/dev/null | grep -q "\.env$"; then
        echo "❌ Error: Attempting to commit .env file with secrets"
        echo "   Please remove .env from staging area"
        afplay /System/Library/Sounds/Basso.aiff &
        exit 1
    fi

    # Check if command is trying to add .env files
    if [[ "$COMMAND" =~ "\.env" ]]; then
        echo "⚠️  Warning: Attempting to stage .env file"
        echo "   .env files should not be committed to version control"
        afplay /System/Library/Sounds/Basso.aiff &
        exit 1
    fi
fi

exit 0
