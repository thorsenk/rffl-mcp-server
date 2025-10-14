
from __future__ import annotations

import json
import logging
import os
import time
from typing import Any, Dict, List, Optional, Tuple

from fastmcp import FastMCP
from espn_api.football import League

"""
rffl-mcp-server: ESPN Fantasy Football MCP server with authentication support.

- Supports both public and private leagues via ESPN cookies (espn_s2 and SWID)
- Authentication REQUIRED for historical data (2018-2022 seasons)
- Recent seasons (2023+) may be accessible without auth if league is public
- Defaults are set via env: ESPN_LEAGUE_ID (323196) and ESPN_YEAR (2025).
- Transport:
    - Default: stdio (for local dev)
    - HTTP/SSE: set MCP_TRANSPORT=http|sse (PORT, HOST supported)
"""

mcp = FastMCP(
    "rffl-mcp-server",
    "ESPN Fantasy Football MCP server with authentication support (via cwendt94/espn-api).",
)

# --- Config / defaults -------------------------------------------------------
DEFAULT_LEAGUE_ID = int(os.getenv("ESPN_LEAGUE_ID", "323196"))  # RFFL public league
DEFAULT_YEAR = int(os.getenv("ESPN_YEAR", "2025"))
DEBUG = os.getenv("ESPN_DEBUG", "0") == "1"
ENABLE_CACHE = os.getenv("ENABLE_CACHE", "true").lower() in ("true", "1", "yes")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# --- Authentication credentials -----------------------------------------------
# Optional: Provide ESPN_S2 and SWID for accessing private leagues or historical data
ESPN_S2 = os.getenv("ESPN_S2", None)
SWID = os.getenv("SWID", None)

# --- Structured Logging Setup ------------------------------------------------
class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging compatible with FastMCP Cloud."""
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        # Add extra fields if present
        if hasattr(record, "tool"):
            log_data["tool"] = record.tool
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
        if hasattr(record, "cache_hit"):
            log_data["cache_hit"] = record.cache_hit
        if hasattr(record, "league_id"):
            log_data["league_id"] = record.league_id
        if hasattr(record, "year"):
            log_data["year"] = record.year
        if hasattr(record, "week"):
            log_data["week"] = record.week
        if hasattr(record, "status"):
            log_data["status"] = record.status
        return json.dumps(log_data)

logger = logging.getLogger("rffl-mcp-server")
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

# --- Cache Management --------------------------------------------------------
# Simple cache so we reuse the same League object across tools
_LEAGUE_CACHE: Dict[Tuple[int, int], League] = {}
_CACHE_STATS = {"hits": 0, "misses": 0, "enabled": ENABLE_CACHE}


def _get_league(
    league_id: Optional[int],
    year: Optional[int],
) -> League:
    """Return a cached League instance with optional authentication."""
    lid = int(league_id or DEFAULT_LEAGUE_ID)
    yr = int(year or DEFAULT_YEAR)
    key = (lid, yr)

    # Check cache
    if ENABLE_CACHE and key in _LEAGUE_CACHE:
        _CACHE_STATS["hits"] += 1
        logger.debug(
            "Cache hit",
            extra={"cache_hit": True, "league_id": lid, "year": yr}
        )
        return _LEAGUE_CACHE[key]

    # Cache miss - fetch from ESPN
    _CACHE_STATS["misses"] += 1

    # Determine if we're using authentication
    using_auth = ESPN_S2 is not None or SWID is not None
    logger.info(
        "Fetching league from ESPN API",
        extra={
            "cache_hit": False,
            "league_id": lid,
            "year": yr,
            "authenticated": using_auth
        }
    )

    try:
        start_time = time.time()
        league = League(
            league_id=lid,
            year=yr,
            espn_s2=ESPN_S2,
            swid=SWID,
            debug=DEBUG,
        )
        duration_ms = int((time.time() - start_time) * 1000)
        logger.info(
            "Successfully loaded league from ESPN",
            extra={
                "league_id": lid,
                "year": yr,
                "duration_ms": duration_ms,
                "authenticated": using_auth,
                "status": "success"
            }
        )

        if ENABLE_CACHE:
            _LEAGUE_CACHE[key] = league

        return league
    except Exception as e:
        # If it fails here, it's likely a private league, auth issue, or historical data requires auth
        logger.error(
            "Failed to load league",
            extra={
                "league_id": lid,
                "year": yr,
                "authenticated": using_auth,
                "status": "error"
            }
        )

        # Provide helpful error messages based on context
        if not using_auth and yr < 2023:
            raise RuntimeError(
                f"Unable to load league {lid} ({yr}). Historical data (pre-2023) requires "
                "authentication. Set ESPN_S2 and SWID environment variables."
            ) from e
        elif not using_auth:
            raise RuntimeError(
                f"Unable to load league {lid} ({yr}). This may be a private league requiring "
                "authentication. Set ESPN_S2 and SWID environment variables if needed."
            ) from e
        else:
            raise RuntimeError(
                f"Unable to load league {lid} ({yr}) even with authentication. "
                "Check that your ESPN_S2 and SWID credentials are valid and you have access to this league."
            ) from e


def _team_dict(t) -> Dict[str, Any]:
    if t is None:
        return {}
    return {
        "id": getattr(t, "team_id", None),
        "abbrev": getattr(t, "team_abbrev", None),
        "name": getattr(t, "team_name", None),
        "division_id": getattr(t, "division_id", None),
        "division_name": getattr(t, "division_name", None),
        "wins": getattr(t, "wins", None),
        "losses": getattr(t, "losses", None),
        "ties": getattr(t, "ties", None),
        "points_for": getattr(t, "points_for", None),
        "points_against": getattr(t, "points_against", None),
        "waiver_rank": getattr(t, "waiver_rank", None),
        "streak_type": getattr(t, "streak_type", None),
        "streak_length": getattr(t, "streak_length", None),
        "standing": getattr(t, "standing", None),
        "final_standing": getattr(t, "final_standing", None),
        "logo_url": getattr(t, "logo_url", None),
    }


def _box_player_dict(bp) -> Dict[str, Any]:
    if bp is None:
        return {}
    return {
        "name": getattr(bp, "name", None),
        "slot": getattr(bp, "slot_position", None),
        "position": getattr(bp, "position", None),
        "points": getattr(bp, "points", None),
        "projected": getattr(bp, "projected_points", getattr(bp, "projected", None)),
        "pro_team": getattr(bp, "pro_team", None),
        "pro_opponent": getattr(bp, "pro_opponent", None),
        "pro_pos_rank": getattr(bp, "pro_pos_rank", None),
        "injury_status": getattr(bp, "injury_status", getattr(bp, "injuryStatus", None)),
    }


def _format_boxscore_markdown(week: int, matchups_data: List[Dict[str, Any]]) -> str:
    """Generate markdown formatted boxscore tables for enhanced display."""
    lines = [f"# Week {week} Enhanced Boxscores\n"]

    for idx, matchup in enumerate(matchups_data, 1):
        home_team = matchup["home_team"]
        home_score = matchup["home_score"]
        away_team = matchup["away_team"]
        away_score = matchup["away_score"]

        # Matchup header
        lines.append(f"## Matchup {idx}: {home_team} ({home_score:.2f}) vs {away_team} ({away_score:.2f})\n")

        # Home team lineup
        lines.append(f"### {home_team} Lineup\n")
        lines.append("| SLOT | PLAYER | POSITION | INJURY STATUS | PROJ PF | ACTUAL PF |")
        lines.append("|------|--------|----------|---------------|---------|-----------|")

        for player in matchup["home_lineup"]:
            slot = player.get("slot", "N/A")
            name = player.get("name", "Unknown")
            position = player.get("position", "N/A")
            injury = player.get("injury_status", "ACTIVE") or "ACTIVE"
            projected = player.get("projected", 0.0) or 0.0
            actual = player.get("points", 0.0) or 0.0

            lines.append(f"| {slot} | {name} | {position} | {injury} | {projected:.2f} | {actual:.2f} |")

        lines.append("")  # Blank line

        # Away team lineup
        lines.append(f"### {away_team} Lineup\n")
        lines.append("| SLOT | PLAYER | POSITION | INJURY STATUS | PROJ PF | ACTUAL PF |")
        lines.append("|------|--------|----------|---------------|---------|-----------|")

        for player in matchup["away_lineup"]:
            slot = player.get("slot", "N/A")
            name = player.get("name", "Unknown")
            position = player.get("position", "N/A")
            injury = player.get("injury_status", "ACTIVE") or "ACTIVE"
            projected = player.get("projected", 0.0) or 0.0
            actual = player.get("points", 0.0) or 0.0

            lines.append(f"| {slot} | {name} | {position} | {injury} | {projected:.2f} | {actual:.2f} |")

        lines.append("")  # Blank line between matchups

    return "\n".join(lines)


def _settings_dict(s) -> Dict[str, Any]:
    return {
        "team_count": getattr(s, "team_count", None),
        "reg_season_count": getattr(s, "reg_season_count", None),
        "veto_votes_required": getattr(s, "veto_votes_required", None),
        "playoff_team_count": getattr(s, "playoff_team_count", None),
        "tie_rule": getattr(s, "tie_rule", None),
        "scoring_type": getattr(s, "scoring_type", None),
    }


# --- Tools -------------------------------------------------------------------

@mcp.tool
def get_league(
    league_id: Optional[int] = None,
    year: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Get league meta, settings, and team list.
    Note: Historical seasons (pre-2023) require ESPN authentication.
    """
    league = _get_league(league_id, year)
    return {
        "league_id": league.league_id,
        "year": league.year,
        "current_week": getattr(league, "current_week", None),
        "nfl_week": getattr(league, "nfl_week", None),
        "settings": _settings_dict(league.settings),
        "teams": [_team_dict(t) for t in league.teams],
    }


@mcp.tool
def get_standings(
    league_id: Optional[int] = None,
    year: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Return teams ordered by standings.
    Note: Historical seasons (pre-2023) require ESPN authentication.
    """
    league = _get_league(league_id, year)
    teams = league.standings()
    return [
        {
            "rank": i + 1,
            **_team_dict(t),
        }
        for i, t in enumerate(teams)
    ]


@mcp.tool
def get_matchups(
    week: Optional[int] = None,
    league_id: Optional[int] = None,
    year: Optional[int] = None,
    include_lineups: bool = False,
) -> List[Dict[str, Any]]:
    """
    Weekly matchups via Box Scores (supports live scoring).
    Note: Historical seasons (pre-2023) require ESPN authentication.
    """
    start_time = time.time()
    league = _get_league(league_id, year)
    box_scores = league.box_scores(week=week)
    w = int(week or getattr(league, "current_week", 0))
    out: List[Dict[str, Any]] = []
    for bs in box_scores:
        item = {
            "week": w,
            "is_playoff": getattr(bs, "is_playoff", False),
            "matchup_type": getattr(bs, "matchup_type", "NONE"),
            "home": {
                **_team_dict(getattr(bs, "home_team", None)),
                "score": getattr(bs, "home_score", None),
                "projected": getattr(bs, "home_projected", None),
            },
            "away": {
                **_team_dict(getattr(bs, "away_team", None)),
                "score": getattr(bs, "away_score", None),
                "projected": getattr(bs, "away_projected", None),
            },
        }
        if include_lineups:
            item["lineups"] = {
                "home": [_box_player_dict(p) for p in getattr(bs, "home_lineup", [])],
                "away": [_box_player_dict(p) for p in getattr(bs, "away_lineup", [])],
            }
        out.append(item)

    duration_ms = int((time.time() - start_time) * 1000)
    logger.info(
        "get_matchups completed",
        extra={
            "tool": "get_matchups",
            "week": w,
            "duration_ms": duration_ms,
            "matchup_count": len(out),
            "status": "success"
        }
    )
    return out


@mcp.tool
def get_enhanced_boxscores(
    week: Optional[int] = None,
    league_id: Optional[int] = None,
    year: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Get enhanced box scores with formatted lineup tables.
    Returns both structured data and markdown-formatted text for clean display.
    Includes all roster spots (starters + bench).
    Note: Historical seasons (pre-2023) require ESPN authentication.
    Note: Box scores before 2019 may have limited data availability.
    """
    start_time = time.time()
    league = _get_league(league_id, year)
    box_scores = league.box_scores(week=week)
    w = int(week or getattr(league, "current_week", 0))

    matchups_data: List[Dict[str, Any]] = []

    for bs in box_scores:
        home_team = getattr(bs, "home_team", None)
        away_team = getattr(bs, "away_team", None)

        matchup = {
            "home_team": getattr(home_team, "team_name", "Unknown") if home_team else "Unknown",
            "home_score": getattr(bs, "home_score", 0.0),
            "away_team": getattr(away_team, "team_name", "Unknown") if away_team else "Unknown",
            "away_score": getattr(bs, "away_score", 0.0),
            "home_lineup": [_box_player_dict(p) for p in getattr(bs, "home_lineup", [])],
            "away_lineup": [_box_player_dict(p) for p in getattr(bs, "away_lineup", [])],
        }
        matchups_data.append(matchup)

    # Generate formatted markdown output
    formatted_output = _format_boxscore_markdown(w, matchups_data)

    duration_ms = int((time.time() - start_time) * 1000)
    logger.info(
        "get_enhanced_boxscores completed",
        extra={
            "tool": "get_enhanced_boxscores",
            "week": w,
            "duration_ms": duration_ms,
            "matchup_count": len(matchups_data),
            "status": "success"
        }
    )

    return {
        "week": w,
        "matchups": matchups_data,
        "formatted_output": formatted_output,
    }


@mcp.tool
def get_power_rankings(
    week: Optional[int] = None,
    league_id: Optional[int] = None,
    year: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Two-step-dominance style power rankings.
    Note: Historical seasons (pre-2023) require ESPN authentication.
    """
    league = _get_league(league_id, year)
    rankings = league.power_rankings(week=week)
    return [{"score": float(score), "team": _team_dict(team)} for score, team in rankings]


@mcp.tool
def get_teams(
    league_id: Optional[int] = None,
    year: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Raw teams array.
    Note: Historical seasons (pre-2023) require ESPN authentication.
    """
    league = _get_league(league_id, year)
    return [_team_dict(t) for t in league.teams]


@mcp.tool
def get_scoreboard(
    week: Optional[int] = None,
    league_id: Optional[int] = None,
    year: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Legacy scoreboard (useful for older seasons).
    Note: Historical seasons (pre-2023) require ESPN authentication.
    """
    league = _get_league(league_id, year)
    scoreboard = league.scoreboard(week=week)
    w = int(week or getattr(league, "current_week", 0))
    out: List[Dict[str, Any]] = []
    for m in scoreboard:
        out.append({
            "week": w,
            "home": {**_team_dict(getattr(m, "home_team", None)), "score": getattr(m, "home_score", None)},
            "away": {**_team_dict(getattr(m, "away_team", None)), "score": getattr(m, "away_score", None)},
        })
    return out


@mcp.tool
def get_player_info(
    name: Optional[str] = None,
    player_id: Optional[int] = None,
    league_id: Optional[int] = None,
    year: Optional[int] = None,
):
    """
    Player lookup by name or ID.
    Note: Historical seasons (pre-2023) require ESPN authentication.
    """
    league = _get_league(league_id, year)
    try:
        res = league.player_info(name=name, playerId=player_id)
    except Exception as e:
        raise RuntimeError("Player info unavailable without auth for this query.") from e

    def _pd(p):
        return {
            "name": getattr(p, "name", None),
            "playerId": getattr(p, "playerId", None),
            "position": getattr(p, "position", None),
            "proTeam": getattr(p, "proTeam", None),
            "injuryStatus": getattr(p, "injury_status", getattr(p, "injuryStatus", None)),
            "total_points": getattr(p, "total_points", None),
            "avg_points": getattr(p, "avg_points", None),
            "projected_total_points": getattr(p, "projected_total_points", None),
            "projected_avg_points": getattr(p, "projected_avg_points", None),
        }

    if res is None:
        return None
    if isinstance(res, list):
        return [_pd(p) for p in res]
    return _pd(res)


# Optional convenience tool for health checks
@mcp.tool
def ping() -> str:
    return "pong"


@mcp.tool
def get_cache_stats() -> Dict[str, Any]:
    """
    Get cache statistics for observability.
    Returns hits, misses, hit rate, and whether caching is enabled.
    """
    total = _CACHE_STATS["hits"] + _CACHE_STATS["misses"]
    hit_rate = (_CACHE_STATS["hits"] / total * 100) if total > 0 else 0.0

    return {
        "enabled": _CACHE_STATS["enabled"],
        "hits": _CACHE_STATS["hits"],
        "misses": _CACHE_STATS["misses"],
        "total_requests": total,
        "hit_rate_percent": round(hit_rate, 2),
        "cached_leagues": len(_LEAGUE_CACHE),
    }


@mcp.tool
def clear_cache() -> Dict[str, str]:
    """
    Clear the league cache to force fresh data from ESPN.
    Useful for testing or when you need guaranteed up-to-date data.
    """
    count = len(_LEAGUE_CACHE)
    _LEAGUE_CACHE.clear()
    logger.info("Cache cleared", extra={"cleared_entries": count})
    return {
        "status": "success",
        "message": f"Cleared {count} cached league(s)",
    }


if __name__ == "__main__":
    # Choose transport by env:
    #   MCP_TRANSPORT=stdio (default)
    #   MCP_TRANSPORT=http   (uses HOST and PORT)
    #   MCP_TRANSPORT=sse    (uses HOST and PORT)
    transport = os.getenv("MCP_TRANSPORT", "stdio").lower()
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8080"))
    if transport == "http":
        mcp.run(transport="http", host=host, port=port)
    elif transport == "sse":
        mcp.run(transport="sse", host=host, port=port)
    else:
        mcp.run()
