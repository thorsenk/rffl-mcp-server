# rffl-mcp-server

Public-only ESPN Fantasy Football MCP server for OpenAI Agent Builder with structured logging and cache observability.

## Features

- **Public ESPN leagues only** - no authentication or private league support
- **Structured JSON logging** - FastMCP Cloud dashboard-friendly
- **Configurable caching** - toggle cache and monitor performance
- **Multiple transports** - stdio (dev), HTTP, or SSE

## Quick start (local)

```bash
pip install -r requirements.txt
export ESPN_LEAGUE_ID=323196 ESPN_YEAR=2025
python rffl_mcp_server.py                 # stdio
MCP_TRANSPORT=http PORT=8080 python rffl_mcp_server.py  # HTTP
```

## Deploy to FastMCP Cloud

1. Push this repo to GitHub.
2. Sign in to [FastMCP Cloud](https://gofastmcp.com) with GitHub (free for personal servers).
3. Create a new project from this repo.
4. **Entrypoint:** `rffl_mcp_server.py:mcp`
5. **Environment variables** (Project → Settings → Environment):
   - `ESPN_LEAGUE_ID=323196` (your league ID)
   - `ESPN_YEAR=2025` (season year)
   - `ENABLE_CACHE=true` (optional, default: true)
   - `LOG_LEVEL=INFO` (optional, default: INFO)
6. Deploy. Your MCP endpoint will look like: `https://<project>.fastmcp.app/mcp`.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ESPN_LEAGUE_ID` | `323196` | ESPN fantasy football league ID |
| `ESPN_YEAR` | `2025` | Fantasy football season year |
| `ENABLE_CACHE` | `true` | Enable/disable league caching (true/false) |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `ESPN_DEBUG` | `0` | Enable ESPN API debug mode (0/1) |
| `MCP_TRANSPORT` | `stdio` | Transport mode (stdio/http/sse) |
| `HOST` | `0.0.0.0` | HTTP/SSE server host |
| `PORT` | `8080` | HTTP/SSE server port |

## Tools

### Core Fantasy Football Data

- `get_league(league_id?, year?)` - League metadata, settings, and teams
- `get_standings(league_id?, year?)` - Teams ordered by standings
- `get_matchups(week?, league_id?, year?, include_lineups=false)` - Weekly matchups with live scoring
- `get_power_rankings(week?, league_id?, year?)` - Two-step dominance power rankings
- `get_teams(league_id?, year?)` - Raw teams array
- `get_scoreboard(week?, league_id?, year?)` - Legacy scoreboard view
- `get_player_info(name?|player_id?, league_id?, year?)` - Player lookup by name or ID

### Observability & Cache Management

- `get_cache_stats()` - Cache hit/miss statistics and status
- `clear_cache()` - Force clear cache for fresh data
- `ping()` - Health check endpoint

## Structured Logging

The server outputs JSON-formatted logs suitable for FastMCP Cloud's observability dashboard:

```json
{"timestamp": "2025-10-09 18:45:23", "level": "INFO", "message": "Fetching league from ESPN API", "cache_hit": false, "league_id": 323196, "year": 2025}
{"timestamp": "2025-10-09 18:45:24", "level": "INFO", "message": "Successfully loaded league from ESPN", "league_id": 323196, "year": 2025, "duration_ms": 856, "status": "success"}
{"timestamp": "2025-10-09 18:45:25", "level": "INFO", "message": "get_matchups completed", "tool": "get_matchups", "week": 5, "duration_ms": 1243, "matchup_count": 6, "status": "success"}
```

## Cache Behavior

- **Cache enabled** (default): League objects are cached in memory across tool calls
- **Cache disabled** (`ENABLE_CACHE=false`): Every request fetches fresh data from ESPN
- **Cache statistics**: Use `get_cache_stats()` to monitor hit rate and performance
- **Cache clearing**: Use `clear_cache()` to force fresh data when needed

## Important Notes

- **PUBLIC LEAGUES ONLY**: This server does not support private leagues or cookie-based authentication (SWID/ESPN_S2)
- **No authentication**: All ESPN API calls use public endpoints only
- Default league (323196) is the RFFL public league
- For load testing or guaranteed fresh data, disable caching with `ENABLE_CACHE=false`

## Example Usage

```python
# Get current week matchups
get_matchups(week=5)

# Get league standings
get_standings()

# Check cache performance
get_cache_stats()
# Returns: {"enabled": true, "hits": 12, "misses": 3, "total_requests": 15, "hit_rate_percent": 80.0, "cached_leagues": 1}

# Force fresh data
clear_cache()
```

## Testing Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run with stdio transport
python rffl_mcp_server.py

# Run with HTTP transport
MCP_TRANSPORT=http PORT=8080 python rffl_mcp_server.py

# Test with caching disabled
ENABLE_CACHE=false python rffl_mcp_server.py

# Test with debug logging
LOG_LEVEL=DEBUG python rffl_mcp_server.py
```

## Architecture

Built with:
- [FastMCP](https://gofastmcp.com) - Model Context Protocol server framework
- [espn-api](https://github.com/cwendt94/espn-api) - ESPN fantasy football API wrapper
- Python 3.8+ compatible

## License

MIT
