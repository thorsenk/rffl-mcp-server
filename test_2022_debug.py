#!/usr/bin/env python3
"""
Debug script to investigate 2022 data fetching issues.
"""

import os
from espn_api.football import League

DEFAULT_LEAGUE_ID = int(os.getenv("ESPN_LEAGUE_ID", "323196"))

print("Testing 2022 data fetch with detailed error information...\n")

for year in [2022, 2021, 2020, 2019, 2018, 2017]:
    print(f"\n{'='*60}")
    print(f"Testing year: {year}")
    print(f"{'='*60}")

    try:
        league = League(league_id=DEFAULT_LEAGUE_ID, year=year, debug=True)

        print(f"✓ Successfully loaded league for {year}")
        print(f"  League ID: {league.league_id}")
        print(f"  Year: {league.year}")
        print(f"  Current Week: {getattr(league, 'current_week', 'N/A')}")
        print(f"  Team Count: {league.settings.team_count}")
        print(f"  Teams: {len(league.teams)}")

        # Try to get first team name
        if league.teams:
            print(f"  First team: {league.teams[0].team_name}")

    except Exception as e:
        print(f"✗ FAILED for {year}")
        print(f"  Error type: {type(e).__name__}")
        print(f"  Error message: {str(e)}")

        # Print full traceback for debugging
        import traceback
        print(f"\n  Full traceback:")
        traceback.print_exc()

print("\n" + "="*60)
print("Test complete")
print("="*60)
