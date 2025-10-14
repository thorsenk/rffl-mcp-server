#!/usr/bin/env python3
"""
Test script to validate historical data fetching from ESPN Fantasy Football.
Tests multiple years and various data endpoints.
"""

import os
import sys
import time
from espn_api.football import League

# Test configuration
DEFAULT_LEAGUE_ID = int(os.getenv("ESPN_LEAGUE_ID", "323196"))
TEST_YEARS = [2024, 2023, 2022]  # Test recent years
TEST_WEEK = 5  # Mid-season week for testing


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_league_metadata(league_id, year):
    """Test fetching league metadata for a given year."""
    print(f"Testing league metadata for {year}...")
    try:
        start = time.time()
        league = League(league_id=league_id, year=year)
        duration = (time.time() - start) * 1000

        print(f"✓ League ID: {league.league_id}")
        print(f"✓ Year: {league.year}")
        print(f"✓ Current Week: {getattr(league, 'current_week', 'N/A')}")
        print(f"✓ Team Count: {league.settings.team_count}")
        print(f"✓ Teams loaded: {len(league.teams)}")
        print(f"✓ Fetch time: {duration:.0f}ms")
        return True, league
    except Exception as e:
        print(f"✗ Failed to fetch league for {year}: {e}")
        return False, None


def test_standings(league, year):
    """Test fetching standings for a given year."""
    print(f"\nTesting standings for {year}...")
    try:
        standings = league.standings()
        print(f"✓ Standings loaded: {len(standings)} teams")
        if standings:
            top_team = standings[0]
            print(f"✓ Top team: {top_team.team_name} ({top_team.wins}-{top_team.losses})")
        return True
    except Exception as e:
        print(f"✗ Failed to fetch standings for {year}: {e}")
        return False


def test_matchups(league, year, week):
    """Test fetching matchups for a given year and week."""
    print(f"\nTesting matchups for {year} Week {week}...")
    try:
        start = time.time()
        box_scores = league.box_scores(week=week)
        duration = (time.time() - start) * 1000

        print(f"✓ Matchups loaded: {len(box_scores)}")
        print(f"✓ Fetch time: {duration:.0f}ms")

        if box_scores:
            first_matchup = box_scores[0]
            home = first_matchup.home_team
            away = first_matchup.away_team
            print(f"✓ Sample: {home.team_name} ({first_matchup.home_score:.2f}) vs {away.team_name} ({first_matchup.away_score:.2f})")
        return True
    except Exception as e:
        print(f"✗ Failed to fetch matchups for {year} Week {week}: {e}")
        return False


def test_boxscore_details(league, year, week):
    """Test fetching detailed boxscore data including lineups."""
    print(f"\nTesting boxscore details for {year} Week {week}...")
    try:
        box_scores = league.box_scores(week=week)

        if box_scores:
            first_matchup = box_scores[0]
            home_lineup = getattr(first_matchup, 'home_lineup', [])
            away_lineup = getattr(first_matchup, 'away_lineup', [])

            print(f"✓ Home lineup size: {len(home_lineup)} players")
            print(f"✓ Away lineup size: {len(away_lineup)} players")

            if home_lineup:
                sample_player = home_lineup[0]
                print(f"✓ Sample player: {sample_player.name} ({sample_player.slot_position}) - {sample_player.points:.2f} pts")

        return True
    except Exception as e:
        print(f"✗ Failed to fetch boxscore details for {year} Week {week}: {e}")
        return False


def test_power_rankings(league, year, week):
    """Test fetching power rankings for a given year and week."""
    print(f"\nTesting power rankings for {year} Week {week}...")
    try:
        rankings = league.power_rankings(week=week)
        print(f"✓ Power rankings loaded: {len(rankings)} teams")
        if rankings:
            score, top_team = rankings[0]
            print(f"✓ Top ranked: {top_team.team_name} (score: {score:.2f})")
        return True
    except Exception as e:
        print(f"✗ Failed to fetch power rankings for {year} Week {week}: {e}")
        return False


def test_year_comprehensive(league_id, year):
    """Run comprehensive tests for a single year."""
    print_section(f"Testing Year {year}")

    results = []

    # Test league metadata and get league object
    success, league = test_league_metadata(league_id, year)
    results.append(("League Metadata", success))

    if not league:
        print(f"\n⚠ Skipping remaining tests for {year} due to league fetch failure")
        return results

    # Run remaining tests with the league object
    results.append(("Standings", test_standings(league, year)))
    results.append(("Matchups", test_matchups(league, year, TEST_WEEK)))
    results.append(("Boxscore Details", test_boxscore_details(league, year, TEST_WEEK)))
    results.append(("Power Rankings", test_power_rankings(league, year, TEST_WEEK)))

    return results


def main():
    """Run all historical data tests."""
    print_section("ESPN Fantasy Football Historical Data Test")
    print(f"Testing League ID: {DEFAULT_LEAGUE_ID}")
    print(f"Test Years: {', '.join(map(str, TEST_YEARS))}")
    print(f"Test Week: {TEST_WEEK}")

    all_results = []

    # Test each year
    for year in TEST_YEARS:
        year_results = test_year_comprehensive(DEFAULT_LEAGUE_ID, year)
        all_results.extend([(test_name, year, result) for test_name, result in year_results])

    # Summary
    print_section("Test Summary")
    passed = sum(1 for _, _, result in all_results if result)
    total = len(all_results)

    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {(passed/total)*100:.1f}%\n")

    # Detailed results by year
    print("Detailed Results by Year:")
    for year in TEST_YEARS:
        year_results = [(name, result) for name, y, result in all_results if y == year]
        year_passed = sum(1 for _, result in year_results if result)
        year_total = len(year_results)
        print(f"\n  {year}: {year_passed}/{year_total} passed")
        for test_name, result in year_results:
            status = "✓" if result else "✗"
            print(f"    {status} {test_name}")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
