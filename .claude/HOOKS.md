# Claude Code Hooks Configuration

This directory contains hook scripts that automate validation and protection tasks during development with audio feedback.

## Installed Hooks

### 1. Python Syntax Validation
**Hook:** `validate-python-syntax.sh`
**Trigger:** After Write/Edit operations
**Purpose:** Validates Python syntax to catch errors immediately after file changes
**Sound:** Hero (success) / Basso (error)

**What it does:**
- Runs `python3 -m py_compile rffl_mcp_server.py`
- Prevents syntax errors from being committed
- Provides immediate feedback on code correctness
- Plays success sound (Hero) when syntax is valid
- Plays error sound (Basso) when syntax errors detected

### 2. Environment File Protection
**Hook:** `protect-env-files.sh`
**Trigger:** Before Bash (git add/commit commands)
**Purpose:** Prevents accidentally committing .env files with secrets
**Sound:** Basso (error)

**What it does:**
- Checks if .env files are in staging area
- Blocks git commands that would commit sensitive files
- Protects against credential leaks
- Plays error sound (Basso) when .env files detected

### 3. MCP Import Verification
**Hook:** `verify-mcp-import.sh`
**Trigger:** After Write/Edit operations on rffl_mcp_server.py
**Purpose:** Ensures the MCP server remains importable and functional
**Sound:** Ping (success) / Basso (error)

**What it does:**
- Imports the MCP object to verify no import errors
- Counts available tools to confirm server structure
- Catches breaking changes before they're committed
- Plays success sound (Ping) when import succeeds
- Plays error sound (Basso) when import fails

### 4. Session Start Welcome
**Hook:** `play-success-sound.sh`
**Trigger:** When Claude Code session starts
**Purpose:** Audio confirmation that development environment is ready
**Sound:** Hero (welcome)

**What it does:**
- Plays welcome sound when you start a Claude Code session
- Confirms hooks are active and ready

## Configuration

Hooks are configured in `.claude/hooks-config.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/protect-env-files.sh",
            "description": "Prevent committing .env files (with error sound)"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/validate-python-syntax.sh",
            "description": "Validate Python syntax (with success/error sounds)"
          },
          {
            "type": "command",
            "command": ".claude/hooks/verify-mcp-import.sh",
            "description": "Verify MCP server can be imported (with success/error sounds)"
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/play-success-sound.sh",
            "description": "Play welcome sound when session starts"
          }
        ]
      }
    ]
  }
}
```

## How to Use

### Enabling Hooks in Claude Code

1. Open Claude Code settings
2. Navigate to the hooks configuration section
3. Point to `.claude/hooks-config.json` in this repository
4. Hooks will automatically execute during development

### Testing Hooks Manually

```bash
# Test syntax validation (with sound)
.claude/hooks/validate-python-syntax.sh

# Test MCP import (set FILE_PATH for context, with sound)
FILE_PATH=rffl_mcp_server.py .claude/hooks/verify-mcp-import.sh

# Test env protection (set COMMAND for context, with error sound)
COMMAND="git add .env" .claude/hooks/protect-env-files.sh

# Test success sound
.claude/hooks/play-success-sound.sh

# Test error sound
.claude/hooks/play-error-sound.sh
```

## Hook Execution Flow

### When Starting a Session

1. Claude Code session starts
2. **SessionStart Hook:** Welcome sound plays (Hero)
3. Development environment ready

### When Writing/Editing Python Files

1. File change completed
2. **Post-Write Hook:** Syntax validation runs
   - Success: Hero sound plays
   - Error: Basso sound plays
3. **Post-Write Hook:** MCP import verification runs (if rffl_mcp_server.py changed)
   - Success: Ping sound plays
   - Error: Basso sound plays
4. If any hook fails, error is displayed to user

### When Running Git Commands

1. Git command requested
2. **Pre-Bash Hook:** Environment file protection checks command
3. If .env file detected:
   - Basso error sound plays
   - Command is blocked
4. Otherwise, command proceeds

## Security Considerations

- Hooks execute shell commands automatically
- All hook scripts are reviewed and version controlled
- Environment variables are available to hook scripts
- Hooks can block operations to prevent errors

## Troubleshooting

### Hook Not Running

- Verify `.claude/hooks-config.json` is configured correctly
- Check that hook scripts have execute permissions (`chmod +x`)
- Ensure hook script paths are correct relative to project root

### Hook Failing Unexpectedly

- Run the hook script manually to see detailed output
- Check that required dependencies (python3) are available
- Verify environment variables are set correctly

### Disabling Hooks Temporarily

Remove or comment out the hooks section in `.claude/hooks-config.json`, or rename the config file temporarily.

## Sound Reference

All hooks use macOS system sounds via `afplay`:

| Sound | Usage | Character |
|-------|-------|-----------|
| **Hero** | Success/Welcome | Triumphant, positive |
| **Ping** | Import verification success | Quick, subtle confirmation |
| **Basso** | Errors/Blocked operations | Classic error sound |

### Available macOS Sounds

You can customize sounds by editing the hook scripts. Available sounds in `/System/Library/Sounds/`:
- Basso, Blow, Bottle, Frog, Funk, Glass, Hero, Morse, Ping, Pop, Purr, Sosumi, Submarine, Tink

### Customizing Sounds

Edit the `.sh` files and change the sound path:
```bash
afplay /System/Library/Sounds/YourSound.aiff &
```

### Disabling Sounds

To disable sounds while keeping validation:
1. Comment out or remove `afplay` lines in hook scripts
2. Keep the validation logic intact

## Additional Hook Ideas

Other useful hooks you could add (with sounds):

- **Post-commit reminder** for FastMCP Cloud deployment (Sosumi notification)
- **Pre-test hook** to verify ESPN credentials are set (Purr if set, Basso if missing)
- **Documentation sync reminder** when new tools are added (Submarine alert)
- **Deployment validation** before pushing to main branch (Funk celebration)
- **Long-running command completion** notification (Glass chime)

See `CLAUDE.md` for the complete list of suggested hooks.
