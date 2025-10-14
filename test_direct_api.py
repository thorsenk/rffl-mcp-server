#!/usr/bin/env python3
"""
Test ESPN API endpoints directly to see what's really happening.
"""

import requests
import json

LEAGUE_ID = 323196

def test_year(year):
    """Test direct API access for a given year."""
    print(f"\n{'='*60}")
    print(f"Testing year: {year}")
    print(f"{'='*60}")

    # Try the modern endpoint (2018+)
    url_modern = f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{LEAGUE_ID}"

    # Try the historical endpoint (pre-2018)
    url_historical = f"https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/leagueHistory/{LEAGUE_ID}?seasonId={year}"

    print(f"Modern endpoint: {url_modern}")
    try:
        r = requests.get(url_modern, params={"view": "mSettings"})
        print(f"  Status code: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"  ✓ SUCCESS - Got data!")
            print(f"  League ID: {data.get('id')}")
            print(f"  Season: {data.get('seasonId')}")
            return True
        else:
            print(f"  Response: {r.text[:200]}")
    except Exception as e:
        print(f"  Error: {e}")

    print(f"\nHistorical endpoint: {url_historical}")
    try:
        r = requests.get(url_historical, params={"view": "mSettings"})
        print(f"  Status code: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"  ✓ SUCCESS - Got data!")
            if isinstance(data, list) and len(data) > 0:
                print(f"  League ID: {data[0].get('id')}")
                print(f"  Season: {data[0].get('seasonId')}")
            return True
        else:
            print(f"  Response: {r.text[:200]}")
    except Exception as e:
        print(f"  Error: {e}")

    return False

# Test years
years = [2024, 2023, 2022, 2021, 2020, 2019, 2018, 2017, 2016, 2015]

results = []
for year in years:
    success = test_year(year)
    results.append((year, success))

print(f"\n{'='*60}")
print("SUMMARY")
print(f"{'='*60}")
for year, success in results:
    status = "✓" if success else "✗"
    print(f"{status} {year}")
