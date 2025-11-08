# RFFL MCP Server - API Reference

Complete reference for all 11 MCP tools available in the RFFL MCP Server.

## Overview

The RFFL MCP Server provides tools to access ESPN Fantasy Football data, including league information, standings, matchups, player data, and observability tools. All tools support optional `league_id` and `year` parameters that default to environment variables (`ESPN_LEAGUE_ID` and `ESPN_YEAR`).

## Authentication

**Historical Data (2018-2022):** Requires ESPN authentication cookies (`ESPN_S2` and `SWID`).
**Recent Seasons (2023+):** Public leagues work without authentication.

See [README.md](README.md) for instructions on obtaining ESPN cookies.

## Core Fantasy Football Data Tools

### `get_league`

Get league metadata, settings, and team list for any season.

**Parameters:**
- `league_id` (Optional[int]): ESPN league ID (defaults to `ESPN_LEAGUE_ID` env var)
- `year` (Optional[int]): Season year like 2016, 2022, 2025 (defaults to `ESPN_YEAR` env var)

**Returns:**
```json
{
  "league_id": 323196,
  "year": 2025,
  "current_week": 5,
  "nfl_week": 5,
  "settings": {
    "team_count": 12,
    "reg_season_count": 14,
    "playoff_team_count": 6,
    "scoring_type": "STANDARD"
  },
  "teams": [...]
}
```

**Examples:**
- `get_league()` → Uses env var defaults
- `get_league(year=2016)` → Get 2016 season data
- `get_league(year=2022, league_id=323196)` → Explicit parameters

**Note:** Historical seasons (2018-2022) require ESPN_S2 and SWID authentication.

---

### `get_standings`

Get final season standings for any year, ranked by wins/losses.

**Parameters:**
- `league_id` (Optional[int]): ESPN league ID (defaults to `ESPN_LEAGUE_ID` env var)
- `year` (Optional[int]): Season year like 2016, 2022, 2025 (defaults to `ESPN_YEAR` env var)

**Returns:**
```json
[
  {
    "rank": 1,
    "id": 1,
    "name": "Team Name",
    "wins": 10,
    "losses": 4,
    "points_for": 1450.5,
    "points_against": 1320.2
  },
  ...
]
```

**Examples:**
- `get_standings()` → Current season standings (uses env vars)
- `get_standings(year=2016)` → 2016 season final standings
- `get_standings(year=2022, league_id=323196)` → Specific league/year

**Note:** Historical seasons (2018-2022) require ESPN_S2 and SWID authentication.

---

### `get_matchups`

Get weekly matchups with scores and optional lineup details for any season/week.

**Parameters:**
- `week` (Optional[int]): NFL week number 1-18 (defaults to current week)
- `league_id` (Optional[int]): ESPN league ID (defaults to `ESPN_LEAGUE_ID` env var)
- `year` (Optional[int]): Season year like 2016, 2022, 2025 (defaults to `ESPN_YEAR` env var)
- `include_lineups` (bool): Include full rosters (default: False)

**Returns:**
```json
[
  {
    "week": 5,
    "is_playoff": false,
    "matchup_type": "NONE",
    "home": {
      "id": 1,
      "name": "Home Team",
      "score": 125.5,
      "projected": 130.2
    },
    "away": {
      "id": 2,
      "name": "Away Team",
      "score": 118.3,
      "projected": 115.8
    },
    "lineups": {...}  // Only if include_lineups=True
  },
  ...
]
```

**Examples:**
- `get_matchups()` → Current week matchups (simple, works all years 2011-2025)
- `get_matchups(week=5)` → Week 5 of current season (simple)
- `get_matchups(week=1, year=2016)` → Week 1 of 2016 season (simple, works!)
- `get_matchups(week=10, year=2022, include_lineups=True)` → With rosters (enhanced, requires 2019+)

**Note:**
- Historical seasons (2018-2022) require ESPN_S2 and SWID authentication.
- Enhanced boxscores (`include_lineups=True`) only available for seasons 2019+ (rolling ~7 year window).
- Simple matchups (default) work for ALL years 2011-2025.

---

### `get_enhanced_boxscores`

Get detailed box scores with formatted lineup tables (starters + bench) for any week.

**Parameters:**
- `week` (Optional[int]): NFL week number 1-18 (defaults to current week)
- `league_id` (Optional[int]): ESPN league ID (defaults to `ESPN_LEAGUE_ID` env var)
- `year` (Optional[int]): Season year like 2016, 2022, 2025 (defaults to `ESPN_YEAR` env var)

**Returns:**
```json
{
  "week": 5,
  "matchups": [
    {
      "home_team": "Home Team",
      "home_score": 125.5,
      "away_team": "Away Team",
      "away_score": 118.3,
      "home_lineup": [
        {
          "name": "Player Name",
          "slot": "QB",
          "position": "QB",
          "points": 25.5,
          "projected": 22.3,
          "pro_team": "KC",
          "injury_status": "ACTIVE"
        },
        ...
      ],
      "away_lineup": [...]
    },
    ...
  ],
  "formatted_output": "# Week 5 Enhanced Boxscores\n\n## Matchup 1: ..."
}
```

**Examples:**
- `get_enhanced_boxscores()` → Current week boxscores
- `get_enhanced_boxscores(week=5)` → Week 5 of current season
- `get_enhanced_boxscores(week=1, year=2022)` → Week 1 of 2022 season

**Note:**
- Historical seasons (2018-2022) require ESPN_S2 and SWID authentication.
- Box scores availability is limited for seasons before 2019 (rolling ~7 year window).

---

### `get_power_rankings`

Get two-step dominance power rankings for any week/season.

**Parameters:**
- `week` (Optional[int]): NFL week number 1-18 (defaults to current week)
- `league_id` (Optional[int]): ESPN league ID (defaults to `ESPN_LEAGUE_ID` env var)
- `year` (Optional[int]): Season year like 2016, 2022, 2025 (defaults to `ESPN_YEAR` env var)

**Returns:**
```json
[
  {
    "score": 95.5,
    "team": {
      "id": 1,
      "name": "Team Name",
      "wins": 10,
      "losses": 4
    }
  },
  ...
]
```

**Examples:**
- `get_power_rankings()` → Current week rankings
- `get_power_rankings(week=10)` → Week 10 of current season
- `get_power_rankings(week=5, year=2022)` → Week 5 of 2022 season

**Note:** Historical seasons (2018-2022) require ESPN_S2 and SWID authentication.

---

### `get_teams`

Get raw list of all teams in the league for any season.

**Parameters:**
- `league_id` (Optional[int]): ESPN league ID (defaults to `ESPN_LEAGUE_ID` env var)
- `year` (Optional[int]): Season year like 2016, 2022, 2025 (defaults to `ESPN_YEAR` env var)

**Returns:**
```json
[
  {
    "id": 1,
    "name": "Team Name",
    "abbrev": "TEA",
    "wins": 10,
    "losses": 4,
    "points_for": 1450.5
  },
  ...
]
```

**Examples:**
- `get_teams()` → All teams in current season
- `get_teams(year=2016)` → All teams from 2016 season

**Note:** Historical seasons (2018-2022) require ESPN_S2 and SWID authentication.

---

### `get_scoreboard`

Get simple scoreboard view (lighter than box scores) for any week.

**Parameters:**
- `week` (Optional[int]): NFL week number 1-18 (defaults to current week)
- `league_id` (Optional[int]): ESPN league ID (defaults to `ESPN_LEAGUE_ID` env var)
- `year` (Optional[int]): Season year like 2016, 2022, 2025 (defaults to `ESPN_YEAR` env var)

**Returns:**
```json
[
  {
    "week": 5,
    "home": {
      "id": 1,
      "name": "Home Team",
      "score": 125.5
    },
    "away": {
      "id": 2,
      "name": "Away Team",
      "score": 118.3
    }
  },
  ...
]
```

**Examples:**
- `get_scoreboard()` → Current week scores
- `get_scoreboard(week=5)` → Week 5 of current season
- `get_scoreboard(week=1, year=2022)` → Week 1 of 2022 season

**Note:** Historical seasons (2018-2022) require ESPN_S2 and SWID authentication.

---

### `get_player_info`

Look up player information by name or ESPN player ID for any season.

**Parameters:**
- `name` (Optional[str]): Player name like "Patrick Mahomes" (optional, searches league roster)
- `player_id` (Optional[int]): ESPN player ID (optional, direct lookup)
- `league_id` (Optional[int]): ESPN league ID (defaults to `ESPN_LEAGUE_ID` env var)
- `year` (Optional[int]): Season year like 2016, 2022, 2025 (defaults to `ESPN_YEAR` env var)

**Returns:**
```json
{
  "name": "Patrick Mahomes",
  "playerId": 3127416,
  "position": "QB",
  "proTeam": "KC",
  "total_points": 245.5,
  "avg_points": 20.5,
  "projected_total_points": 350.0
}
```

**Examples:**
- `get_player_info(name="Patrick Mahomes")` → Search current season
- `get_player_info(name="Tom Brady", year=2022)` → 2022 season player
- `get_player_info(player_id=12345)` → Direct lookup by ID

**Note:** Must provide either `name` or `player_id`. Historical seasons (2018-2022) require ESPN_S2 and SWID authentication.

---

## Observability & Cache Management Tools

### `ping`

Health check endpoint to verify server is running.

**Parameters:** None

**Returns:**
```json
"pong"
```

**Example:**
- `ping()` → "pong"

---

### `get_cache_stats`

Get cache performance statistics for monitoring and observability.

**Parameters:** None

**Returns:**
```json
{
  "enabled": true,
  "hits": 25,
  "misses": 5,
  "total_requests": 30,
  "hit_rate_percent": 83.33,
  "cached_leagues": 1
}
```

**Example:**
- `get_cache_stats()` → Cache metrics

**Note:** Cache can be toggled via `ENABLE_CACHE` environment variable.

---

### `clear_cache`

Clear all cached league data to force fresh API calls to ESPN.

**Parameters:** None

**Returns:**
```json
{
  "status": "success",
  "message": "Cleared 1 cached league(s)"
}
```

**Example:**
- `clear_cache()` → Confirmation message

**Use cases:**
- Testing changes or debugging
- Forcing fresh data after trades/roster moves
- Resetting performance metrics

---

## Data Availability by Year

| Year Range | Authentication | Simple Matchups | Enhanced Boxscores | Notes |
|------------|---------------|----------------|-------------------|-------|
| 2023-2025 | Optional (public leagues) | ✅ | ✅ | Full access |
| 2019-2022 | **Required** | ✅ | ✅ | ESPN API requires auth |
| 2011-2018 | **Required** | ✅ | Limited | ESPN API limitation for enhanced data |
| 2010 and earlier | **Required** | Limited | Limited | Historical data availability varies |

**Key Insight:** Use `get_matchups()` (default) or `get_scoreboard()` for simple matchup data - works for ALL years 2011-2025. Use `get_matchups(include_lineups=True)` or `get_enhanced_boxscores()` for detailed player lineups - only works for recent years (currently 2019-2025, rolling ~7 year window).

## Error Handling

All tools provide contextual error messages based on:
- Authentication state (whether ESPN_S2 and SWID are provided)
- Year requested (historical vs recent)
- League access permissions

Common errors:
- **401/403**: Missing or expired cookies
- **"Unable to load league"**: Private league or historical data without auth
- **Empty data**: Wrong year or league ID

## Performance

- **Cache enabled (default):** 700-800x speedup on cached requests
- **Cache disabled:** Every request fetches fresh data from ESPN
- **Target hit rate:** 70%+ in production usage

See `get_cache_stats()` to monitor cache performance.

## Related Documentation

- [README.md](README.md) - User guide and quick start
- [CLAUDE.md](CLAUDE.md) - Developer guidance and architecture
- [DEPLOYMENT.md](DEPLOYMENT.md) - FastMCP Cloud deployment guide
- [TEST_PLAN.md](TEST_PLAN.md) - Testing strategy

