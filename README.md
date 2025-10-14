# rffl-mcp-server

ESPN Fantasy Football MCP server with authentication support for historical data access, structured logging, and cache observability.

## Features

- **Authentication support** - Access private leagues and historical data (2018-2022) with ESPN cookies
- **Public league support** - Recent seasons (2023+) work without authentication for public leagues
- **Structured JSON logging** - FastMCP Cloud dashboard-friendly
- **Configurable caching** - toggle cache and monitor performance
- **Multiple transports** - stdio (dev), HTTP, or SSE
- **Historical data** - Access league data back to 2017 with proper authentication

## Quick Install (Cursor)

Click to install the deployed MCP server in Cursor:

**[Install rffl-mcp-server](cursor://anysphere.cursor-deeplink/mcp/install?name=rffl-mcp-server&config=eyJ1cmwiOiJodHRwczovL3JmZmwtbWNwLXNlcnZlci5mYXN0bWNwLmFwcC9tY3AifQ%3D%3D)**

This installs the live server at `https://rffl-mcp-server.fastmcp.app/mcp` with access to all fantasy football tools.

## Quick start (local)

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# Edit .env to add your ESPN_S2 and SWID cookies (required for historical data)

# Run the server
python rffl_mcp_server.py                 # stdio
MCP_TRANSPORT=http PORT=8080 python rffl_mcp_server.py  # HTTP
```

## Getting ESPN Authentication Cookies

**REQUIRED for accessing historical data (2018-2022 seasons)**

1. Log into [ESPN.com](https://espn.com) in your browser
2. Open Developer Tools (F12 or right-click → Inspect)
3. Go to the **Application** tab (Chrome) or **Storage** tab (Firefox)
4. Under **Cookies** → `https://espn.com`, find:
   - `espn_s2` - Long alphanumeric string
   - `SWID` - Format: `{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}`
5. Copy these values into your `.env` file

## Deploy to FastMCP Cloud

1. Push this repo to GitHub.
2. Sign in to [FastMCP Cloud](https://gofastmcp.com) with GitHub (free for personal servers).
3. Create a new project from this repo.
4. **Entrypoint:** `rffl_mcp_server.py:mcp`
5. **Environment variables** (Project → Settings → Environment):
   - `ESPN_LEAGUE_ID=323196` (your league ID)
   - `ESPN_YEAR=2025` (season year)
   - `ESPN_S2=your_espn_s2_cookie` (for historical data)
   - `SWID={your_swid_cookie}` (for historical data)
   - `ENABLE_CACHE=true` (optional, default: true)
   - `LOG_LEVEL=INFO` (optional, default: INFO)
6. Deploy. Your MCP endpoint will look like: `https://<project>.fastmcp.app/mcp`.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ESPN_LEAGUE_ID` | `323196` | ESPN fantasy football league ID |
| `ESPN_YEAR` | `2025` | Fantasy football season year |
| `ESPN_S2` | None | **ESPN authentication cookie (REQUIRED for historical data 2018-2022)** |
| `SWID` | None | **ESPN authentication cookie (REQUIRED for historical data 2018-2022)** |
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
- `get_enhanced_boxscores(week?, league_id?, year?)` - Enhanced boxscores with formatted lineup tables (starters + bench)
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

### Authentication Requirements

- **Recent seasons (2023+)**: Public leagues work without authentication
- **Historical seasons (2018-2022)**: **REQUIRES** ESPN_S2 and SWID cookies
- **Pre-2018 seasons (2017 and earlier)**: Accessible with authentication, but limited data
- **Box scores**: Available for 2019+, limited availability for 2018 and earlier

### Data Availability by Year

| Year Range | Authentication | League Data | Box Scores | Notes |
|------------|---------------|-------------|------------|-------|
| 2023-2025 | Optional (public leagues) | ✓ | ✓ | Full access |
| 2018-2022 | **Required** | ✓ | ✓ | ESPN API requires auth |
| 2017 and earlier | **Required** | ✓ | Limited | Historical data availability varies |

### Other Notes

- Default league (323196) is the RFFL public league
- For load testing or guaranteed fresh data, disable caching with `ENABLE_CACHE=false`
- Cookies expire periodically - if you get auth errors, refresh your ESPN_S2 and SWID values

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

# Set up authentication (copy .env.example to .env and fill in your cookies)
cp .env.example .env

# Run with stdio transport
python rffl_mcp_server.py

# Run with HTTP transport
MCP_TRANSPORT=http PORT=8080 python rffl_mcp_server.py

# Test historical data access (2022)
ESPN_YEAR=2022 python rffl_mcp_server.py

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
