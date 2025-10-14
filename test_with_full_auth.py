#!/usr/bin/env python3
"""
Test ESPN API with full authentication (espn_s2 + SWID).
"""

from espn_api.football import League

LEAGUE_ID = 323196
ESPN_S2 = "AEARRpE9BJOR4sGFEHsKl/dwwNNveoi/dFkaRsLtMPW+fbH8ufyTijZMqvRa7YaHaX/eeutkeJwvRb+9Os6Z79dDXj9FJXBotB0ZkAvXeSUcYHD7qZkUTHJF31vnQWwZmTDM3jEqivQfrLNXP6w/NIDpl7l+4jtZ7TO2lR/Z8dSNr7/eQHpxh7EnwSEsRtAELbJrT5sk0WHCc1I7Q+tNJuAx4yDVnPtBnaxbHeK+kvomG1uihGsH6sbxIcL4sFPNFCGVWGCySAViax0MEB5Z+qMSuxv5gUc+2bTPvJjdtwRv+g=="
SWID = "{C3FCDEE0-434E-498F-9793-E68E81750B9B}"

print("Testing historical data access with FULL authentication (espn_s2 + SWID)...\n")

test_years = [2022, 2021, 2020, 2019, 2018, 2017]
results = []

for year in test_years:
    print(f"\n{'='*60}")
    print(f"Testing year: {year}")
    print(f"{'='*60}")

    try:
        # Create league with full authentication
        league = League(
            league_id=LEAGUE_ID,
            year=year,
            espn_s2=ESPN_S2,
            swid=SWID
        )

        print(f"✓ Successfully loaded league for {year}")
        print(f"  League ID: {league.league_id}")
        print(f"  Year: {league.year}")
        print(f"  Current Week: {getattr(league, 'current_week', 'N/A')}")
        print(f"  Team Count: {league.settings.team_count}")
        print(f"  Teams: {len(league.teams)}")

        if league.teams:
            print(f"  First team: {league.teams[0].team_name}")
            print(f"  Last team: {league.teams[-1].team_name}")

        # Try to get matchups for week 5
        try:
            matchups = league.box_scores(week=5)
            print(f"  Week 5 matchups: {len(matchups)}")
            if matchups:
                first = matchups[0]
                print(f"    Sample: {first.home_team.team_name} ({first.home_score:.2f}) vs {first.away_team.team_name} ({first.away_score:.2f})")
        except Exception as e:
            print(f"  Week 5 matchups: Error - {str(e)}")

        results.append((year, True))

    except Exception as e:
        print(f"✗ FAILED for {year}")
        print(f"  Error type: {type(e).__name__}")
        print(f"  Error: {str(e)}")

        # Show more detail for debugging
        import traceback
        print(f"  Traceback:")
        traceback.print_exc()

        results.append((year, False))

print(f"\n{'='*60}")
print("SUMMARY")
print(f"{'='*60}")

passed = sum(1 for _, success in results if success)
total = len(results)

print(f"\nTests passed: {passed}/{total}")
print(f"Success rate: {(passed/total)*100:.1f}%\n")

for year, success in results:
    status = "✓" if success else "✗"
    print(f"{status} {year}")
