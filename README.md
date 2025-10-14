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

## Advanced FastMCP Cloud Features

Beyond the basic tools, FastMCP Cloud provides three powerful capabilities to extend your server: **Resources**, **Resource Templates**, and **Prompts**.

### Resources

**What they are:** Resources expose static or dynamic data/content that MCP clients can access for context. Think of them as "readable assets" your server makes available.

**Use cases for rffl-mcp-server:**

1. **League Documentation**
   - Expose `league-rules.md` as `resource://league/rules`
   - Scoring system explanations
   - Historical league notes

2. **Schema Definitions**
   - Team structure schemas
   - Player stat definitions
   - API response formats

3. **Cached Reports**
   - Pre-generated season summaries
   - Historical comparisons
   - League analytics dashboards

**How to implement:**

```python
from fastmcp import FastMCP

mcp = FastMCP("rffl-mcp-server")

@mcp.resource("league://rules")
def get_league_rules():
    """Expose league rules as a resource"""
    return {
        "uri": "league://rules",
        "name": "RFFL League Rules",
        "mimeType": "text/markdown",
        "text": "# League Rules\n\n## Scoring System\n..."
    }

@mcp.resource("league://history/{year}")
def get_season_summary(year: int):
    """Dynamic resource for season summaries"""
    # Fetch data for that year
    league = League(league_id=323196, year=year, espn_s2=ESPN_S2, swid=SWID)
    summary = f"# {year} Season Summary\n\nChampion: {league.standings()[0].team_name}..."
    return {
        "uri": f"league://history/{year}",
        "name": f"{year} Season Summary",
        "mimeType": "text/markdown",
        "text": summary
    }
```

**In FastMCP dashboard:** Resources appear automatically from your manifest after deployment.

---

### Resource Templates

**What they are:** Parameterized resources that generate content dynamically based on URI patterns. Like resources, but with variable paths.

**Use cases for rffl-mcp-server:**

1. **Dynamic Player Cards**
   - `player://stats/{player_id}` - Generate player stat cards on-demand
   - `player://history/{player_id}/{year}` - Historical player data

2. **Team Dashboards**
   - `team://overview/{team_id}` - Real-time team dashboard
   - `team://matchup/{team_id}/{week}` - Specific matchup analysis

3. **Week-by-Week Reports**
   - `week://summary/{year}/{week}` - Auto-generated week summaries
   - `week://boxscore/{year}/{week}/{matchup_id}` - Detailed boxscores

**How to implement:**

```python
@mcp.resource_template("player://stats/{player_id}")
def player_stats_card(player_id: int):
    """Generate player stat card on-demand"""
    league = _get_league()
    player = league.player_info(playerId=player_id)
    
    card = f"""
# {player.name} - {player.position}

**Team:** {player.proTeam}
**Total Points:** {player.total_points}
**Average:** {player.avg_points}
**Projected:** {player.projected_total_points}
"""
    return {
        "uri": f"player://stats/{player_id}",
        "name": f"{player.name} Stats",
        "mimeType": "text/markdown",
        "text": card
    }
```

**In FastMCP dashboard:** Templates appear with their URI pattern (e.g., `player://stats/{player_id}`).

---

### Prompts

**What they are:** Pre-configured AI instructions that guide how MCP clients (like ChatMCP) interact with your tools. They improve natural language understanding and tool calling accuracy.

**Use cases for rffl-mcp-server:**

1. **Improve Tool Discovery**
   - Teach AI when to use each tool
   - Explain parameter meanings
   - Provide usage examples

2. **Handle Natural Language**
   - "Show me 2016 standings" → `get_standings(year=2016)`
   - "Week 5 matchups" → `get_matchups(week=5)`
   - "Last year's champion" → `get_standings(year=2024)` + extract winner

3. **Add Fantasy Football Context**
   - Scoring system explanations
   - Common abbreviations (RB, WR, PPR, etc.)
   - League-specific rules

**How to implement:**

```python
@mcp.prompt("fantasy-expert")
def fantasy_football_assistant():
    """Prompt to guide AI behavior"""
    return {
        "name": "fantasy-expert",
        "description": "Fantasy football expert assistant for RFFL",
        "arguments": [],
        "prompt": """
You are a fantasy football expert assistant for the RFFL league (ID: 323196).

TOOL USAGE GUIDELINES:
- When user mentions a year (e.g., "2016", "last year"), extract it and pass as year parameter
- When user mentions a week (e.g., "week 5", "this week"), pass as week parameter
- Default to current season (2025) if no year specified
- Historical data (2018-2022) requires authentication

NATURAL LANGUAGE MAPPING:
- "standings" / "rankings" → get_standings(year=X)
- "matchups" / "games" / "scores" → get_matchups(week=X, year=Y)
- "boxscores" / "detailed scores" → get_enhanced_boxscores(week=X, year=Y)
- "power rankings" → get_power_rankings(week=X, year=Y)
- "player stats" / "lookup [player]" → get_player_info(name="player", year=Y)

COMMON ABBREVIATIONS:
- QB=Quarterback, RB=Running Back, WR=Wide Receiver, TE=Tight End
- PPR=Points Per Reception, FLEX=Flexible position slot
- IR=Injured Reserve, BYE=Team bye week

EXAMPLES:
User: "Show me 2016 standings"
→ Call: get_standings(year=2016)

User: "Week 5 matchups for 2022"
→ Call: get_matchups(week=5, year=2022)

User: "Who won last year?"
→ Call: get_standings(year=2024) → Extract rank 1 team

Always be helpful, concise, and fantasy-football savvy!
"""
    }

@mcp.prompt("historical-analysis")
def historical_data_prompt():
    """Prompt for historical data queries"""
    return {
        "name": "historical-analysis", 
        "description": "Analyze historical RFFL data across multiple seasons",
        "arguments": [
            {"name": "start_year", "description": "First year to analyze", "required": True},
            {"name": "end_year", "description": "Last year to analyze", "required": True}
        ],
        "prompt": """
Analyze RFFL historical data from {start_year} to {end_year}.

STEPS:
1. For each year in range, call get_standings(year=YEAR)
2. Extract champion, runner-up, top scorer
3. Identify trends (repeat champions, scoring increases, etc.)
4. Summarize findings in a markdown table

Use get_matchups() and get_power_rankings() for deeper insights if needed.
"""
    }
```

**In FastMCP dashboard:** Prompts appear with name, description, and can be invoked by AI clients.

---

### Implementation Priority

**Start with Prompts** (Highest Impact):
1. Create `fantasy-expert` prompt to improve ChatMCP interactions
2. Test natural language queries immediately
3. Iterate based on what ChatMCP still struggles with

**Then Resources** (Medium Effort, High Value):
1. Add league rules/documentation as static resources
2. Create season summary resources for each year
3. Helps AI understand league context better

**Finally Resource Templates** (Advanced):
1. Dynamic player cards
2. On-demand team dashboards
3. Best for power users who want deep integrations

---

### Example: Adding Your First Prompt

**1. Update `rffl_mcp_server.py`:**

```python
@mcp.prompt("fantasy-expert")
def fantasy_football_assistant():
    return {
        "name": "fantasy-expert",
        "description": "Fantasy football expert for RFFL with smart tool calling",
        "arguments": [],
        "prompt": """
You are an expert RFFL fantasy football assistant. 

When users mention years (2016, 2022, "last year"), extract and use as year parameter.
When users mention weeks (week 5, "this week"), extract and use as week parameter.

Tool mapping:
- "standings"/"rankings" → get_standings(year=X)
- "matchups"/"games" → get_matchups(week=X, year=Y)  
- "boxscores" → get_enhanced_boxscores(week=X, year=Y)

Always include year in responses to avoid confusion.
"""
    }
```

**2. Commit and push:**
```bash
git add rffl_mcp_server.py
git commit -m "Add fantasy-expert prompt for improved natural language"
git push origin main
```

**3. FastMCP auto-deploys** → Prompt appears in dashboard → ChatMCP uses it automatically!

---

## Architecture

Built with:
- [FastMCP](https://gofastmcp.com) - Model Context Protocol server framework
- [espn-api](https://github.com/cwendt94/espn-api) - ESPN fantasy football API wrapper
- Python 3.8+ compatible

## License

MIT
