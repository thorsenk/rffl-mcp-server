# Migration Guide: Adding ESPN Authentication Support

## Quick Summary

If your project uses the ESPN Fantasy Football API (`espn-api` Python library) and needs to access historical data (2018-2022), you need to add authentication support.

## What Changed?

ESPN's API now **requires authentication cookies** (`espn_s2` and `SWID`) to access league data from seasons 2018-2022, even for publicly accessible leagues.

## Migration Steps

### Step 1: Get Your ESPN Cookies

1. Log into [ESPN.com](https://espn.com) in your browser
2. Open Developer Tools (F12 or Right-click → Inspect)
3. Navigate to **Application** tab (Chrome) or **Storage** tab (Firefox)
4. Under **Cookies** → `https://espn.com`, find and copy:
   - `espn_s2` - Long alphanumeric string
   - `SWID` - Format: `{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}`

### Step 2: Add Environment Variables

Create or update your `.env` file:

```bash
# Required for historical data (2018-2022)
ESPN_S2=your_espn_s2_cookie_value_here
SWID={your_swid_cookie_value_here}

# Your existing config
ESPN_LEAGUE_ID=323196
ESPN_YEAR=2025
```

### Step 3: Update Your Code

**Before (without authentication):**

```python
from espn_api.football import League

league = League(league_id=323196, year=2022)
```

**After (with authentication):**

```python
import os
from espn_api.football import League

league = League(
    league_id=323196,
    year=2022,
    espn_s2=os.getenv("ESPN_S2"),
    swid=os.getenv("SWID")
)
```

### Step 4: Update .gitignore

Ensure your `.gitignore` includes:

```gitignore
# Environment variables and credentials
.env
*.env
!.env.example
```

### Step 5: Create .env.example

Provide a template for others:

```bash
# .env.example
ESPN_LEAGUE_ID=your_league_id
ESPN_YEAR=2025
ESPN_S2=get_from_espn_cookies
SWID={get_from_espn_cookies}
```

### Step 6: Update Documentation

Add a section explaining:
- Why authentication is needed
- How to get ESPN cookies
- Which years require authentication
- Cookie expiration and refresh process

## Testing Your Changes

```bash
# Test recent season (should work with or without auth)
ESPN_YEAR=2024 python your_script.py

# Test historical season (requires auth)
ESPN_YEAR=2022 python your_script.py

# Test older season (requires auth, limited data)
ESPN_YEAR=2018 python your_script.py
```

## Data Availability Reference

| Year Range | Auth Required? | Full Data? | Notes |
|------------|----------------|------------|-------|
| 2023-2025 | No (optional) | ✓ | Public leagues work without auth |
| 2018-2022 | **YES** | ✓ | Auth mandatory |
| 2017 and earlier | **YES** | Partial | Limited box score data |

## Common Issues

### Issue: AttributeError: 'NoneType' object has no attribute 'get'

**Cause**: Library bug when cookies are not provided
**Solution**: Always provide `espn_s2` and `swid` parameters, even if `None`

### Issue: 401 Unauthorized

**Cause**: Missing or expired cookies
**Solution**:
1. Check that `ESPN_S2` and `SWID` are set
2. Verify cookie values are correct
3. Get fresh cookies from ESPN.com

### Issue: "Can't use box score before 2019"

**Cause**: Library limitation, not API limitation
**Solution**: Use other endpoints (standings, teams, league info) for pre-2019 seasons

## FastMCP Cloud Deployment

If deploying to FastMCP Cloud:

1. Go to Project → Settings → Environment
2. Add these environment variables:
   ```
   ESPN_S2=your_cookie_value
   SWID={your_cookie_value}
   ```
3. Redeploy your project

## Security Notes

- **Never commit** `.env` files to version control
- **Rotate cookies** periodically for security
- **Use environment variables** in production, not hardcoded values
- **Limit access** to your `.env` file (permissions: 600)

```bash
chmod 600 .env  # Read/write for owner only
```

## Need Help?

See the comprehensive investigation document: `HISTORICAL_DATA_FIX.md`

## Checklist

- [ ] Get ESPN_S2 and SWID cookies
- [ ] Create .env file with credentials
- [ ] Update code to pass authentication parameters
- [ ] Ensure .env is in .gitignore
- [ ] Create .env.example template
- [ ] Update project documentation
- [ ] Test with historical years (2018-2022)
- [ ] Deploy updated environment variables to production
- [ ] Document cookie refresh process for your team

---

**Last Updated**: October 14, 2025
