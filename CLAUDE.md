# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an ESPN Fantasy Football MCP (Model Context Protocol) server built with FastMCP. It provides AI agents with tools to access ESPN Fantasy Football data, including league info, standings, matchups, and player information. The server supports both public leagues and private/historical leagues via ESPN authentication cookies.

## Key Architecture

### Core Server (rffl_mcp_server.py)

Single-file MCP server with these architectural components:

1. **League Cache System** (`_LEAGUE_CACHE`, `_CACHE_STATS`)
   - In-memory cache for `League` objects keyed by `(league_id, year)` tuple
   - Configurable via `ENABLE_CACHE` environment variable
   - Tracks hits/misses for observability
   - Cache can be cleared programmatically via `clear_cache()` tool

2. **Authentication Layer** (`_get_league()` function)
   - Handles both authenticated and unauthenticated ESPN API access
   - Required for historical data (2018-2022) and private leagues
   - Uses `ESPN_S2` and `SWID` cookies from ESPN.com
   - Provides contextual error messages based on auth state and year

3. **Structured Logging** (`JSONFormatter` class)
   - All logs output as JSON for FastMCP Cloud dashboard compatibility
   - Includes contextual fields: `tool`, `duration_ms`, `cache_hit`, `league_id`, `year`, `week`, `status`
   - Configurable via `LOG_LEVEL` environment variable

4. **MCP Tools** (11 total)
   - Core fantasy data: `get_league`, `get_standings`, `get_matchups`, `get_enhanced_boxscores`, `get_power_rankings`, `get_teams`, `get_scoreboard`, `get_player_info`
   - Observability: `get_cache_stats`, `clear_cache`, `ping`

### Data Transformation Helpers

- `_team_dict()`: Extracts team attributes into consistent dict format
- `_box_player_dict()`: Transforms box score player objects
- `_format_boxscore_markdown()`: Generates formatted markdown tables for boxscores
- `_settings_dict()`: Extracts league settings

## Environment Variables

**Core Configuration:**
- `ESPN_LEAGUE_ID` (default: 323196) - Target league ID
- `ESPN_YEAR` (default: 2025) - Season year

**Authentication (REQUIRED for historical data 2018-2022):**
- `ESPN_S2=AEARRpE9BJOR4sGFEHsKl/dwwNNveoi/dFkaRsLtMPW+fbH8ufyTijZMqvRa7YaHaX/eeutkeJwvRb+9Os6Z79dDXj9FJXBotB0ZkAvXeSUcYHD7qZkUTHJF31vnQWwZmTDM3jEqivQfrLNXP6w/NIDpl7l+4jtZ7TO2lR/Z8dSNr7/eQHpxh7EnwSEsRtAELbJrT5sk0WHCc1I7Q+tNJuAx4yDVnPtBnaxbHeK+kvomG1uihGsH6sbxIcL4sFPNFCGVWGCySAViax0MEB5Z+qMSuxv5gUc+2bTPvJjdtwRv+g==` - ESPN authentication cookie for RFFL league
- `SWID={C3FCDEE0-434E-498F-9793-E68E81750B9B}` - ESPN session cookie for RFFL league

**Observability & Performance:**
- `ENABLE_CACHE` (default: true) - Toggle league caching
- `LOG_LEVEL` (default: INFO) - Logging verbosity
- `ESPN_DEBUG` (default: 0) - Enable ESPN API debug mode

**Transport (local dev only):**
- `MCP_TRANSPORT` (default: stdio) - Options: stdio, http, sse
- `HOST` (default: 0.0.0.0) - HTTP/SSE host
- `PORT` (default: 8080) - HTTP/SSE port

## Development Commands

### Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run with stdio transport (default)
python rffl_mcp_server.py

# Run with HTTP transport
MCP_TRANSPORT=http PORT=8080 python rffl_mcp_server.py

# Test historical data access (requires ESPN_S2 and SWID in .env)
ESPN_YEAR=2022 python rffl_mcp_server.py

# Test with caching disabled
ENABLE_CACHE=false python rffl_mcp_server.py

# Test with debug logging
LOG_LEVEL=DEBUG python rffl_mcp_server.py
```

### Syntax Validation

```bash
# Check Python syntax
python3 -m py_compile rffl_mcp_server.py

# Verify MCP object can be imported (requires dependencies)
python3 -c "from rffl_mcp_server import mcp; print(f'Server: {mcp.name}'); print(f'Tools: {len(mcp._tools)}')"
```

### Git Operations

```bash
# Check repository status
git status

# View recent commits
git log --oneline -5

# Push to remote
git push origin main
```

## Testing

The repository includes multiple test scripts:

- `test_historical_data.py` - Comprehensive historical data testing (2018-2022)
- `test_direct_api.py` - Direct ESPN API testing without MCP layer
- `test_with_auth.py` - Authentication flow testing
- `test_with_full_auth.py` - Full authentication scenario testing
- `test_2022_debug.py` - Debugging 2022 season access

These are **diagnostic scripts** for development, not automated test suites.

## Authentication Notes

### Getting ESPN Cookies

1. Log into ESPN.com in browser
2. Open Developer Tools (F12)
3. Navigate to Application/Storage tab → Cookies → `https://espn.com`
4. Copy `espn_s2` and `SWID` values
5. Add to `.env` file (use `.env.example` as template)

### Data Availability by Year

- **2023-2025**: Public leagues work without auth, historical data needs auth
- **2018-2022**: **REQUIRES** ESPN_S2 and SWID cookies
- **2017 and earlier**: Requires auth, limited box score availability

### Common Auth Errors

- **401/403**: Missing or expired cookies
- **"Unable to load league"**: Private league or historical data without auth
- **Empty data**: Wrong year or league ID

## FastMCP Cloud Deployment

**Entrypoint:** `rffl_mcp_server.py:mcp`

**Required Environment Variables:**
```
ESPN_LEAGUE_ID=323196
ESPN_YEAR=2025
ESPN_S2=<cookie>
SWID=<cookie>
ENABLE_CACHE=true
LOG_LEVEL=INFO
```

**Deployment endpoint format:** `https://<project>.fastmcp.app/mcp`

See `DEPLOYMENT.md` for full deployment checklist and `TEST_PLAN.md` for testing strategy.

## Cache Behavior

- **Enabled** (default): League objects cached in memory across tool calls
- **Disabled** (`ENABLE_CACHE=false`): Every request fetches fresh data from ESPN
- Cache is scoped per `(league_id, year)` tuple
- Use `get_cache_stats()` to monitor hit rate and performance
- Use `clear_cache()` to force fresh data when needed
- Target: 70%+ hit rate in production usage

## Important Implementation Details

1. **All tools accept optional `league_id` and `year` parameters** - defaults come from environment variables
2. **Week numbers**: If not provided, tools use `league.current_week`
3. **Enhanced boxscores**: Returns both structured data and formatted markdown via `formatted_output` field
4. **Error messages**: Contextual based on auth state and year (helpful for debugging)
5. **Logging**: Every tool logs completion with `duration_ms` and `status` fields
6. **Transport selection**: Determined by `MCP_TRANSPORT` env var at startup (stdio/http/sse)

## File Structure

```
rffl-mcp-server/
├── rffl_mcp_server.py        # Main server (single file, ~560 lines)
├── requirements.txt           # FastMCP + espn_api dependencies
├── .env.example              # Environment variable template
├── README.md                 # User documentation
├── DEPLOYMENT.md             # FastMCP Cloud deployment guide
├── TEST_PLAN.md              # Comprehensive test strategy
├── HISTORICAL_DATA_FIX.md    # Historical data troubleshooting
├── MIGRATION_GUIDE.md        # Version migration notes
└── test_*.py                 # Diagnostic test scripts
```

## Common Tasks

### Adding a New Tool

1. Define function with `@mcp.tool` decorator
2. Add optional `league_id` and `year` parameters with defaults
3. Call `_get_league(league_id, year)` to get cached league object
4. Use helper functions (`_team_dict`, etc.) for consistent data formatting
5. Add structured logging with `logger.info()` including `extra` fields
6. Return JSON-serializable data structures

### Modifying Cache Behavior

Cache logic is in `_get_league()` function (lines 80-166). Key considerations:
- Cache key is `(league_id, year)` tuple
- Stats tracked: hits, misses, enabled status
- Cache miss triggers ESPN API call with auth credentials
- Error handling provides contextual messages based on auth + year

### Debugging ESPN API Issues

1. Enable debug mode: `ESPN_DEBUG=1`
2. Check structured logs for `duration_ms` and `status` fields
3. Verify auth cookies are valid (test at ESPN.com)
4. Check year range (historical data needs auth)
5. Use diagnostic test scripts to isolate issues

### Updating for New NFL Season

1. Update `ESPN_YEAR` environment variable
2. Verify current week detection works (`league.current_week`)
3. Test matchups and boxscores for active weeks
4. No code changes needed - year is parameterized

## Git Commit Guidelines

**IMPORTANT: Only commit when explicitly requested by the user.**

### Commit Process

1. **Run in parallel before committing:**
   - `git status` - See all untracked files
   - `git diff` - See staged and unstaged changes
   - `git log --oneline -5` - Review recent commit style

2. **Analyze changes and draft commit message:**
   - Summarize nature of changes (feature, enhancement, bug fix, refactoring, test, docs)
   - Focus on "why" rather than "what"
   - Keep message concise (1-2 sentences for summary)
   - DO NOT commit files with secrets (.env, credentials.json, etc.)

3. **Create commit with standard footer:**
   ```bash
   git commit -m "$(cat <<'EOF'
   Commit message summary here.

   Optional detailed explanation of changes and reasoning.

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Claude <noreply@anthropic.com>
   EOF
   )"
   ```

4. **After commit:** Run `git status` to verify success

### Git Safety Rules

**NEVER:**
- Update git config
- Run destructive commands (push --force, hard reset) unless explicitly requested
- Skip hooks (--no-verify, --no-gpg-sign) unless explicitly requested
- Force push to main/master (warn user if requested)
- Use `git commit --amend` unless: (1) user explicitly requests OR (2) fixing pre-commit hook changes
- Push to remote unless user explicitly asks

**Before amending:** Always check authorship with `git log -1 --format='%an %ae'`

### Typical Commit Flow

```bash
# Stage relevant files
git add file1.py file2.md

# Create commit
git commit -m "message with footer"

# Only push if user requests
git push origin main
```
