
from __future__ import annotations

import json
import logging
import os
import time
from typing import Any, Dict, List, Optional, Tuple

from fastmcp import FastMCP
from espn_api.football import League

"""
rffl-mcp-server: Public-only ESPN Fantasy Football MCP server.

- No cookies. No private leagues.
- If a league requires auth, calls will raise a clear error.
- Defaults are set via env: ESPN_LEAGUE_ID (323196) and ESPN_YEAR (2025).
- Transport:
    - Default: stdio (for local dev)
    - HTTP/SSE: set MCP_TRANSPORT=http|sse (PORT, HOST supported)
"""

mcp = FastMCP(
    "rffl-mcp-server",
    "Public-only ESPN Fantasy Football MCP server (via cwendt94/espn-api).",
)

# --- Config / defaults -------------------------------------------------------
DEFAULT_LEAGUE_ID = int(os.getenv("ESPN_LEAGUE_ID", "323196"))  # RFFL public league
DEFAULT_YEAR = int(os.getenv("ESPN_YEAR", "2025"))
DEBUG = os.getenv("ESPN_DEBUG", "0") == "1"
ENABLE_CACHE = os.getenv("ENABLE_CACHE", "true").lower() in ("true", "1", "yes")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

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
    """Return a cached League instance (public leagues only)."""
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
    logger.info(
        "Fetching league from ESPN API",
        extra={"cache_hit": False, "league_id": lid, "year": yr}
    )

    try:
        start_time = time.time()
        league = League(
            league_id=lid,
            year=yr,
            debug=DEBUG,
        )
        duration_ms = int((time.time() - start_time) * 1000)
        logger.info(
            "Successfully loaded league from ESPN",
            extra={"league_id": lid, "year": yr, "duration_ms": duration_ms, "status": "success"}
        )

        if ENABLE_CACHE:
            _LEAGUE_CACHE[key] = league

        return league
    except Exception as e:
        # If it fails here, it's likely a private league or an ESPN-side issue
        logger.error(
            "Failed to load league",
            extra={"league_id": lid, "year": yr, "status": "error"}
        )
        raise RuntimeError(
            f"Unable to load league {lid} ({yr}) without auth. "
            "This build is PUBLIC-ONLY and does not support private leagues."
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
    Get league meta, settings, and team list. PUBLIC leagues only.
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
    Return teams ordered by standings. PUBLIC leagues only.
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
    Weekly matchups via Box Scores (supports live scoring). PUBLIC leagues only.
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
def get_power_rankings(
    week: Optional[int] = None,
    league_id: Optional[int] = None,
    year: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Two-step-dominance style power rankings. PUBLIC leagues only.
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
    Raw teams array. PUBLIC leagues only.
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
    Legacy scoreboard (useful for older seasons). PUBLIC leagues only.
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
    Player lookup by name or ID. PUBLIC endpoints only; returns limited info if ESPN restricts details.
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
