#!/usr/bin/env python3
"""
Test script to verify get_matchups() fix for simple vs enhanced boxscores.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the server
from rffl_mcp_server import _get_league

def test_simple_matchups_2018():
    """Test simple matchups for 2018 - should work now!"""
    print("\n" + "="*60)
    print("TEST 1: Simple matchups for 2018 (scoreboard)")
    print("="*60)
    try:
        league = _get_league(None, 2018)
        # Using scoreboard directly (what get_matchups now uses when include_lineups=False)
        matchups = league.scoreboard(week=5)
        print(f"✓ SUCCESS: Retrieved {len(matchups)} matchups for 2018 week 5")
        if matchups:
            first = matchups[0]
            print(f"  Sample: {first.home_team.team_name} ({first.home_score}) vs {first.away_team.team_name} ({first.away_score})")
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False


def test_simple_matchups_2022():
    """Test simple matchups for 2022 - should work"""
    print("\n" + "="*60)
    print("TEST 2: Simple matchups for 2022 (scoreboard)")
    print("="*60)
    try:
        league = _get_league(None, 2022)
        matchups = league.scoreboard(week=5)
        print(f"✓ SUCCESS: Retrieved {len(matchups)} matchups for 2022 week 5")
        if matchups:
            first = matchups[0]
            print(f"  Sample: {first.home_team.team_name} ({first.home_score}) vs {first.away_team.team_name} ({first.away_score})")
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False


def test_enhanced_matchups_2022():
    """Test enhanced matchups for 2022 - should work"""
    print("\n" + "="*60)
    print("TEST 3: Enhanced matchups for 2022 (box_scores)")
    print("="*60)
    try:
        league = _get_league(None, 2022)
        matchups = league.box_scores(week=5)
        print(f"✓ SUCCESS: Retrieved {len(matchups)} enhanced matchups for 2022 week 5")
        if matchups:
            first = matchups[0]
            home_lineup = getattr(first, 'home_lineup', [])
            away_lineup = getattr(first, 'away_lineup', [])
            print(f"  Sample: {first.home_team.team_name} ({first.home_score}) vs {first.away_team.team_name} ({first.away_score})")
            print(f"  Lineup data: Home={len(home_lineup)} players, Away={len(away_lineup)} players")
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False


def test_enhanced_matchups_2018():
    """Test enhanced matchups for 2018 - should fail with library error"""
    print("\n" + "="*60)
    print("TEST 4: Enhanced matchups for 2018 (box_scores) - EXPECTED TO FAIL")
    print("="*60)
    try:
        league = _get_league(None, 2018)
        matchups = league.box_scores(week=5)
        print(f"✗ UNEXPECTED: Got {len(matchups)} matchups (should have failed)")
        return False
    except Exception as e:
        error_msg = str(e)
        if "before 2019" in error_msg:
            print(f"✓ SUCCESS: Correctly rejected with expected error")
            print(f"  Error: {error_msg}")
            return True
        else:
            print(f"✗ FAILED: Wrong error message: {error_msg}")
            return False


def main():
    """Run all tests."""
    print("="*60)
    print("Testing get_matchups() Fix")
    print("="*60)
    print(f"League ID: {os.getenv('ESPN_LEAGUE_ID', '323196')}")
    print(f"Has Auth: {os.getenv('ESPN_S2') is not None}")

    results = []
    results.append(("Simple 2018", test_simple_matchups_2018()))
    results.append(("Simple 2022", test_simple_matchups_2022()))
    results.append(("Enhanced 2022", test_enhanced_matchups_2022()))
    results.append(("Enhanced 2018 (expected fail)", test_enhanced_matchups_2018()))

    print("\n" + "="*60)
    print("RESULTS SUMMARY")
    print("="*60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
