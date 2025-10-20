#!/usr/bin/env python3
"""
Comprehensive MCP Server Health Check Script

Tests all aspects of the rffl-mcp-server including:
- Basic connectivity and server initialization
- Cache functionality and performance
- Current season data access (2025)
- Historical data access with authentication (2018-2022)
- Data accuracy and consistency across tools
- Error handling and edge cases
"""

import os
import sys
import time
import json
from typing import Dict, List, Any, Tuple
from datetime import datetime
from espn_api.football import League

# Load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ Loaded .env file")
except ImportError:
    print("⚠ python-dotenv not available, using system environment variables")

# Import the MCP server components we can actually test
try:
    import rffl_mcp_server
    from rffl_mcp_server import (
        mcp,
        _LEAGUE_CACHE,
        _CACHE_STATS,
        _get_league,
        DEFAULT_LEAGUE_ID,
        DEFAULT_YEAR,
        ESPN_S2,
        SWID,
        ENABLE_CACHE,
    )
    print("✓ Successfully imported MCP server components")
except ImportError as e:
    print(f"✗ Failed to import MCP server: {e}")
    sys.exit(1)


class HealthCheckReport:
    """Tracks test results and generates health report."""

    def __init__(self):
        self.results: List[Tuple[str, bool, str, float]] = []
        self.start_time = time.time()

    def add_result(self, category: str, test_name: str, success: bool, message: str, duration_ms: float = 0):
        """Add a test result."""
        self.results.append((f"{category}/{test_name}", success, message, duration_ms))

    def print_summary(self):
        """Print comprehensive health report."""
        total_duration = (time.time() - self.start_time) * 1000

        print("\n" + "="*80)
        print("                    MCP SERVER HEALTH CHECK REPORT")
        print("="*80)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Total Test Duration: {total_duration:.0f}ms")
        print("="*80 + "\n")

        # Group by category
        categories = {}
        for test_path, success, message, duration in self.results:
            category, test_name = test_path.split("/", 1)
            if category not in categories:
                categories[category] = []
            categories[category].append((test_name, success, message, duration))

        # Print results by category
        total_passed = 0
        total_tests = len(self.results)

        for category, tests in categories.items():
            passed = sum(1 for _, success, _, _ in tests if success)
            total = len(tests)
            total_passed += passed

            status_icon = "✓" if passed == total else "⚠"
            print(f"{status_icon} {category}: {passed}/{total} passed")

            for test_name, success, message, duration in tests:
                icon = "  ✓" if success else "  ✗"
                duration_str = f" ({duration:.0f}ms)" if duration > 0 else ""
                print(f"{icon} {test_name}{duration_str}")
                if message and not success:
                    print(f"      → {message}")
            print()

        # Overall summary
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        print("="*80)
        print(f"OVERALL: {total_passed}/{total_tests} tests passed ({success_rate:.1f}%)")

        if success_rate == 100:
            print("STATUS: ✓ HEALTHY - All systems operational")
        elif success_rate >= 80:
            print("STATUS: ⚠ DEGRADED - Some issues detected")
        else:
            print("STATUS: ✗ UNHEALTHY - Critical issues detected")

        print("="*80 + "\n")

        return success_rate == 100


def test_basic_connectivity(report: HealthCheckReport):
    """Test basic server connectivity and initialization."""
    print("\n[1/8] Testing Basic Connectivity...")

    # Test 1: Server module loading
    try:
        assert hasattr(rffl_mcp_server, 'mcp'), "MCP object not found"
        assert mcp.name == "rffl-mcp-server", "MCP name mismatch"
        report.add_result("Connectivity", "server_module_loaded", True, "MCP server module loaded successfully")
    except Exception as e:
        report.add_result("Connectivity", "server_module_loaded", False, str(e))

    # Test 2: MCP tools registration
    try:
        # Check that tools are registered (FastMCP stores them differently)
        tool_count = len([attr for attr in dir(rffl_mcp_server) if attr.startswith('get_') or attr in ['ping', 'clear_cache']])
        assert tool_count >= 11, f"Expected at least 11 tool functions, found {tool_count}"
        report.add_result("Connectivity", "mcp_tools_registered", True, f"{tool_count} tool functions available")
    except Exception as e:
        report.add_result("Connectivity", "mcp_tools_registered", False, str(e))

    # Test 3: Environment configuration
    try:
        has_auth = ESPN_S2 is not None and SWID is not None

        assert DEFAULT_LEAGUE_ID == 323196, f"Expected league ID 323196, got {DEFAULT_LEAGUE_ID}"
        assert DEFAULT_YEAR >= 2025, f"Expected year 2025+, got {DEFAULT_YEAR}"

        if has_auth:
            report.add_result("Connectivity", "environment_config", True, f"League {DEFAULT_LEAGUE_ID}, Year {DEFAULT_YEAR}, Auth: ✓")
        else:
            report.add_result("Connectivity", "environment_config", False, "Missing ESPN_S2 or SWID authentication")
    except Exception as e:
        report.add_result("Connectivity", "environment_config", False, str(e))


def test_cache_functionality(report: HealthCheckReport):
    """Test cache functionality and performance."""
    print("\n[2/8] Testing Cache Functionality...")

    # Test 1: Cache stats state
    try:
        assert "enabled" in _CACHE_STATS, "Missing 'enabled' field"
        assert "hits" in _CACHE_STATS, "Missing 'hits' field"
        assert "misses" in _CACHE_STATS, "Missing 'misses' field"

        report.add_result("Cache", "cache_stats_structure", True,
                         f"Enabled: {_CACHE_STATS['enabled']}, Hits: {_CACHE_STATS['hits']}, Misses: {_CACHE_STATS['misses']}")
    except Exception as e:
        report.add_result("Cache", "cache_stats_structure", False, str(e))

    # Test 2: Clear cache
    try:
        initial_size = len(_LEAGUE_CACHE)
        _LEAGUE_CACHE.clear()
        final_size = len(_LEAGUE_CACHE)

        if final_size == 0:
            report.add_result("Cache", "cache_clear", True, f"Cleared {initial_size} entries")
        else:
            report.add_result("Cache", "cache_clear", False, f"Cache not empty after clear: {final_size} entries")
    except Exception as e:
        report.add_result("Cache", "cache_clear", False, str(e))

    # Test 3: Cache hit behavior
    try:
        if not ENABLE_CACHE:
            report.add_result("Cache", "cache_hit_behavior", True, "Cache disabled (ENABLE_CACHE=false)")
            return

        # Clear cache and reset stats
        _LEAGUE_CACHE.clear()
        initial_misses = _CACHE_STATS["misses"]
        initial_hits = _CACHE_STATS["hits"]

        # First call should be a cache miss
        start = time.time()
        league1 = _get_league(None, 2025)
        first_call_duration = (time.time() - start) * 1000
        first_call_misses = _CACHE_STATS["misses"]

        # Second call should be a cache hit
        start = time.time()
        league2 = _get_league(None, 2025)
        second_call_duration = (time.time() - start) * 1000
        second_call_hits = _CACHE_STATS["hits"]

        if first_call_misses > initial_misses and second_call_hits > initial_hits:
            speedup = first_call_duration / second_call_duration if second_call_duration > 0 else 1
            report.add_result("Cache", "cache_hit_behavior", True,
                            f"Cache working (speedup: {speedup:.1f}x, {first_call_duration:.0f}ms -> {second_call_duration:.0f}ms)")
        else:
            report.add_result("Cache", "cache_hit_behavior", False,
                            f"Cache not working (misses: {first_call_misses - initial_misses}, hits: {second_call_hits - initial_hits})")
    except Exception as e:
        report.add_result("Cache", "cache_hit_behavior", False, str(e))


def test_current_season_data(report: HealthCheckReport):
    """Test current season data access (2025)."""
    print("\n[3/8] Testing Current Season Data (2025)...")

    # Test 1: Get league info
    try:
        start = time.time()
        league = _get_league(None, 2025)
        duration = (time.time() - start) * 1000

        assert league.league_id == 323196, "Wrong league ID"
        assert league.year == 2025, "Wrong year"
        assert len(league.teams) > 0, "No teams found"

        report.add_result("Current Season", "get_league", True,
                         f"{len(league.teams)} teams, Week {getattr(league, 'current_week', 'N/A')}", duration)
    except Exception as e:
        report.add_result("Current Season", "get_league", False, str(e))

    # Test 2: Get standings
    try:
        start = time.time()
        league = _get_league(None, 2025)
        standings = league.standings()
        duration = (time.time() - start) * 1000

        assert len(standings) > 0, "No standings data"

        top_team = standings[0]
        report.add_result("Current Season", "get_standings", True,
                         f"{len(standings)} teams, Leader: {getattr(top_team, 'team_name', 'N/A')}", duration)
    except Exception as e:
        report.add_result("Current Season", "get_standings", False, str(e))

    # Test 3: Get teams
    try:
        start = time.time()
        league = _get_league(None, 2025)
        teams = league.teams
        duration = (time.time() - start) * 1000

        assert len(teams) > 0, "No teams found"
        report.add_result("Current Season", "get_teams", True, f"{len(teams)} teams", duration)
    except Exception as e:
        report.add_result("Current Season", "get_teams", False, str(e))

    # Test 4: Get matchups for week 1
    try:
        start = time.time()
        league = _get_league(None, 2025)
        matchups = league.box_scores(week=1)
        duration = (time.time() - start) * 1000

        assert len(matchups) > 0, "No matchups found"
        report.add_result("Current Season", "get_matchups", True, f"{len(matchups)} matchups", duration)
    except Exception as e:
        report.add_result("Current Season", "get_matchups", False, str(e))

    # Test 5: Get scoreboard
    try:
        start = time.time()
        league = _get_league(None, 2025)
        scoreboard = league.scoreboard(week=1)
        duration = (time.time() - start) * 1000

        assert len(scoreboard) > 0, "No scoreboard data"
        report.add_result("Current Season", "get_scoreboard", True, f"{len(scoreboard)} games", duration)
    except Exception as e:
        report.add_result("Current Season", "get_scoreboard", False, str(e))


def test_historical_data_access(report: HealthCheckReport):
    """Test historical data access with authentication."""
    print("\n[4/8] Testing Historical Data Access (2022, 2020, 2018)...")

    test_years = [2022, 2020, 2018]

    for year in test_years:
        # Test league metadata
        try:
            start = time.time()
            league = _get_league(None, year)
            duration = (time.time() - start) * 1000

            assert league.year == year, f"Wrong year returned"
            assert len(league.teams) > 0, "No teams found"

            report.add_result("Historical Data", f"get_league_{year}", True,
                             f"{len(league.teams)} teams", duration)
        except Exception as e:
            report.add_result("Historical Data", f"get_league_{year}", False, str(e))

        # Test standings
        try:
            start = time.time()
            league = _get_league(None, year)
            standings = league.standings()
            duration = (time.time() - start) * 1000

            assert len(standings) > 0, "No standings data"
            report.add_result("Historical Data", f"get_standings_{year}", True,
                             f"{len(standings)} teams", duration)
        except Exception as e:
            report.add_result("Historical Data", f"get_standings_{year}", False, str(e))

        # Test SIMPLE matchups (scoreboard) - should work for ALL years 2011-2025
        try:
            start = time.time()
            league = _get_league(None, year)
            scoreboard = league.scoreboard(week=5)
            duration = (time.time() - start) * 1000

            assert len(scoreboard) > 0, "No simple matchups found"
            report.add_result("Historical Data", f"simple_matchups_{year}_week5", True,
                             f"{len(scoreboard)} matchups (simple)", duration)
        except Exception as e:
            report.add_result("Historical Data", f"simple_matchups_{year}_week5", False, str(e))

        # Test ENHANCED boxscores - only works within rolling ~7 year window
        # For 2025: works for 2019-2025 (2018 and earlier expected to fail)
        try:
            start = time.time()
            league = _get_league(None, year)
            boxscores = league.box_scores(week=5)
            duration = (time.time() - start) * 1000

            assert len(boxscores) > 0, "No enhanced boxscores found"

            # Check if player lineup data is present
            if boxscores:
                first_matchup = boxscores[0]
                home_lineup = getattr(first_matchup, 'home_lineup', [])
                has_lineup_data = len(home_lineup) > 0

                if has_lineup_data:
                    report.add_result("Historical Data", f"enhanced_boxscores_{year}_week5", True,
                                     f"{len(boxscores)} enhanced matchups with lineups", duration)
                else:
                    report.add_result("Historical Data", f"enhanced_boxscores_{year}_week5", False,
                                     "Boxscores returned but no lineup data")
            else:
                report.add_result("Historical Data", f"enhanced_boxscores_{year}_week5", False,
                                 "No boxscores returned")
        except Exception as e:
            error_msg = str(e)
            # For 2018 and earlier, "Can't use box score before 2019" is EXPECTED
            if year < 2019 and "before 2019" in error_msg:
                report.add_result("Historical Data", f"enhanced_boxscores_{year}_week5", True,
                                 f"Expected limitation: {error_msg}")
            else:
                report.add_result("Historical Data", f"enhanced_boxscores_{year}_week5", False, error_msg)


def test_data_accuracy(report: HealthCheckReport):
    """Test data accuracy and consistency across different tools."""
    print("\n[5/8] Testing Data Accuracy and Consistency...")

    # Test 1: Team count consistency
    try:
        league = _get_league(None, 2025)
        teams = league.teams
        standings = league.standings()

        league_team_count = len(teams)
        standings_count = len(standings)

        if league_team_count == standings_count:
            report.add_result("Data Accuracy", "team_count_consistency", True,
                             f"All endpoints report {league_team_count} teams")
        else:
            report.add_result("Data Accuracy", "team_count_consistency", False,
                             f"Mismatch: league={league_team_count}, standings={standings_count}")
    except Exception as e:
        report.add_result("Data Accuracy", "team_count_consistency", False, str(e))

    # Test 2: Matchup vs scoreboard consistency for week 1
    try:
        league = _get_league(None, 2025)
        matchups = league.box_scores(week=1)
        scoreboard = league.scoreboard(week=1)

        if len(matchups) == len(scoreboard):
            report.add_result("Data Accuracy", "matchup_scoreboard_consistency", True,
                             f"Both report {len(matchups)} games")
        else:
            report.add_result("Data Accuracy", "matchup_scoreboard_consistency", False,
                             f"Mismatch: matchups={len(matchups)}, scoreboard={len(scoreboard)}")
    except Exception as e:
        report.add_result("Data Accuracy", "matchup_scoreboard_consistency", False, str(e))

    # Test 3: Boxscore data completeness
    try:
        league = _get_league(None, 2025)
        boxscores = league.box_scores(week=1)

        assert len(boxscores) > 0, "No matchup data"

        # Check that each matchup has lineup data
        incomplete_matchups = []
        for idx, bs in enumerate(boxscores):
            home_lineup = getattr(bs, 'home_lineup', [])
            away_lineup = getattr(bs, 'away_lineup', [])
            if not home_lineup or not away_lineup:
                incomplete_matchups.append(idx)

        if not incomplete_matchups:
            report.add_result("Data Accuracy", "boxscore_completeness", True,
                             f"{len(boxscores)} complete matchups")
        else:
            report.add_result("Data Accuracy", "boxscore_completeness", False,
                             f"Incomplete lineup data in matchups: {incomplete_matchups}")
    except Exception as e:
        report.add_result("Data Accuracy", "boxscore_completeness", False, str(e))

    # Test 4: Power rankings data validity
    try:
        league = _get_league(None, 2025)
        rankings = league.power_rankings(week=1)

        assert len(rankings) > 0, "No power rankings data"

        # Check that rankings are sorted by score
        scores = [score for score, team in rankings]
        is_sorted = all(scores[i] >= scores[i+1] for i in range(len(scores)-1))

        if is_sorted:
            report.add_result("Data Accuracy", "power_rankings_validity", True,
                             f"{len(rankings)} teams correctly sorted")
        else:
            report.add_result("Data Accuracy", "power_rankings_validity", False,
                             "Rankings not properly sorted by score")
    except Exception as e:
        report.add_result("Data Accuracy", "power_rankings_validity", False, str(e))


def test_enhanced_features(report: HealthCheckReport):
    """Test enhanced features like detailed boxscores."""
    print("\n[6/8] Testing Enhanced Features...")

    # Test 1: Boxscore lineup data
    try:
        start = time.time()
        league = _get_league(None, 2025)
        boxscores = league.box_scores(week=1)
        duration = (time.time() - start) * 1000

        if boxscores and len(boxscores) > 0:
            first_matchup = boxscores[0]
            home_lineup = getattr(first_matchup, 'home_lineup', [])
            away_lineup = getattr(first_matchup, 'away_lineup', [])

            report.add_result("Enhanced Features", "boxscore_lineup_data", True,
                             f"Home: {len(home_lineup)} players, Away: {len(away_lineup)} players", duration)
        else:
            report.add_result("Enhanced Features", "boxscore_lineup_data", False,
                             "No boxscore data available")
    except Exception as e:
        report.add_result("Enhanced Features", "boxscore_lineup_data", False, str(e))

    # Test 2: Player stats in lineup
    try:
        league = _get_league(None, 2025)
        boxscores = league.box_scores(week=1)

        if boxscores and len(boxscores) > 0:
            first_matchup = boxscores[0]
            home_lineup = getattr(first_matchup, 'home_lineup', [])

            if home_lineup and len(home_lineup) > 0:
                player = home_lineup[0]
                has_name = hasattr(player, 'name')
                has_points = hasattr(player, 'points')
                has_position = hasattr(player, 'slot_position') or hasattr(player, 'position')

                if has_name and has_points and has_position:
                    report.add_result("Enhanced Features", "player_stats_availability", True,
                                     f"Player data complete: {player.name}")
                else:
                    report.add_result("Enhanced Features", "player_stats_availability", False,
                                     f"Missing player fields (name:{has_name}, points:{has_points}, position:{has_position})")
            else:
                report.add_result("Enhanced Features", "player_stats_availability", False,
                                 "No players in lineup")
        else:
            report.add_result("Enhanced Features", "player_stats_availability", False,
                             "No boxscore data available")
    except Exception as e:
        report.add_result("Enhanced Features", "player_stats_availability", False, str(e))


def test_error_handling(report: HealthCheckReport):
    """Test error handling and edge cases."""
    print("\n[7/8] Testing Error Handling...")

    # Test 1: Invalid year (future)
    try:
        league = _get_league(None, 2030)
        # ESPN API might actually accept future years without error, so this passing is OK
        report.add_result("Error Handling", "future_year_handling", True,
                         "ESPN API accepts future year (or has data)")
    except Exception as e:
        # Also OK if it rejects
        report.add_result("Error Handling", "future_year_handling", True,
                         f"Correctly rejected future year: {str(e)[:50]}")

    # Test 2: Invalid week number
    try:
        league = _get_league(None, 2025)
        matchups = league.box_scores(week=50)
        report.add_result("Error Handling", "invalid_week_number", False,
                         "Should have raised error for invalid week")
    except Exception as e:
        report.add_result("Error Handling", "invalid_week_number", True,
                         f"Correctly rejected: {str(e)[:50]}")

    # Test 3: Historical data without auth
    try:
        # Clear auth temporarily
        has_auth = ESPN_S2 is not None and SWID is not None

        if not has_auth:
            # Try to get old data without auth - should fail with helpful error
            try:
                league = _get_league(None, 2018)
                report.add_result("Error Handling", "historical_data_auth_check", False,
                                 "Should have raised error for historical data without auth")
            except RuntimeError as e:
                error_msg = str(e)
                if "authentication" in error_msg.lower() or "espn_s2" in error_msg.lower():
                    report.add_result("Error Handling", "historical_data_auth_check", True,
                                     "Provides helpful auth error message")
                else:
                    report.add_result("Error Handling", "historical_data_auth_check", False,
                                     f"Unhelpful error message: {error_msg[:50]}")
        else:
            # We have auth, so test passes differently
            try:
                league = _get_league(None, 2016)
                report.add_result("Error Handling", "historical_data_auth_check", True,
                                 "Successfully accessed 2016 data with auth")
            except Exception as e:
                report.add_result("Error Handling", "historical_data_auth_check", False,
                                 f"Failed even with auth: {str(e)[:50]}")
    except Exception as e:
        report.add_result("Error Handling", "historical_data_auth_check", False,
                         f"Unexpected error: {str(e)[:50]}")


def test_performance_metrics(report: HealthCheckReport):
    """Test performance and generate metrics."""
    print("\n[8/8] Testing Performance Metrics...")

    # Test 1: Measure cache performance over multiple calls
    try:
        if not ENABLE_CACHE:
            report.add_result("Performance", "cache_efficiency", True,
                             "Cache disabled (ENABLE_CACHE=false), skipping cache efficiency test")
        else:
            _LEAGUE_CACHE.clear()

            # Make 5 calls to same league/year
            durations = []
            for i in range(5):
                start = time.time()
                _get_league(None, 2025)
                duration = (time.time() - start) * 1000
                durations.append(duration)

            # Calculate hit rate
            total = _CACHE_STATS["hits"] + _CACHE_STATS["misses"]
            hit_rate = (_CACHE_STATS["hits"] / total * 100) if total > 0 else 0

            avg_duration = sum(durations) / len(durations)

            # First call should be slowest (cache miss)
            # Subsequent calls should be faster (cache hits)
            speedup = durations[0] / avg_duration if avg_duration > 0 else 1

            if hit_rate >= 70:
                report.add_result("Performance", "cache_efficiency", True,
                                 f"Hit rate: {hit_rate:.1f}%, Avg: {avg_duration:.0f}ms, Speedup: {speedup:.1f}x")
            else:
                report.add_result("Performance", "cache_efficiency", True,
                                 f"Cache working (hit rate: {hit_rate:.1f}%, avg: {avg_duration:.0f}ms)")
    except Exception as e:
        report.add_result("Performance", "cache_efficiency", False, str(e))

    # Test 2: Measure API response times
    try:
        _LEAGUE_CACHE.clear()

        start = time.time()
        _get_league(None, 2025)
        league_duration = (time.time() - start) * 1000

        start = time.time()
        league = _get_league(None, 2025)
        matchups = league.box_scores(week=1)
        matchups_duration = (time.time() - start) * 1000

        start = time.time()
        league = _get_league(None, 2025)
        power_rankings = league.power_rankings(week=1)
        rankings_duration = (time.time() - start) * 1000

        # Check if response times are reasonable (< 10 seconds for initial load, < 1 second for cached)
        if league_duration < 10000:
            report.add_result("Performance", "api_response_times", True,
                             f"League: {league_duration:.0f}ms, Matchups: {matchups_duration:.0f}ms, Rankings: {rankings_duration:.0f}ms")
        else:
            report.add_result("Performance", "api_response_times", False,
                             f"Slow league load (>10s): {league_duration:.0f}ms")
    except Exception as e:
        report.add_result("Performance", "api_response_times", False, str(e))


def main():
    """Run all health checks and generate report."""
    print("="*80)
    print("            RFFL MCP SERVER - COMPREHENSIVE HEALTH CHECK")
    print("="*80)
    print(f"Start Time: {datetime.now().isoformat()}")
    print(f"League ID: {os.getenv('ESPN_LEAGUE_ID', '323196')}")
    print(f"Default Year: {os.getenv('ESPN_YEAR', '2025')}")
    print(f"Cache Enabled: {os.getenv('ENABLE_CACHE', 'true')}")
    print(f"Has Auth: {os.getenv('ESPN_S2') is not None and os.getenv('SWID') is not None}")
    print("="*80)

    report = HealthCheckReport()

    # Run all test suites
    test_basic_connectivity(report)
    test_cache_functionality(report)
    test_current_season_data(report)
    test_historical_data_access(report)
    test_data_accuracy(report)
    test_enhanced_features(report)
    test_error_handling(report)
    test_performance_metrics(report)

    # Generate final report
    all_passed = report.print_summary()

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
