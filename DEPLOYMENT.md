# FastMCP Cloud Deployment Checklist

## Pre-Deployment Verification

- [x] Files organized at repository root
- [x] `rffl_mcp_server.py` - main server code
- [x] `requirements.txt` - dependencies (fastmcp, espn_api)
- [x] `README.md` - comprehensive documentation
- [x] `.gitignore` - ignore temporary/sensitive files
- [x] Cache toggle implemented (ENABLE_CACHE env var)
- [x] Structured JSON logging implemented
- [x] 11 tools total (9 core + 2 observability)

## Tools Available

1. `get_league()` - League metadata
2. `get_standings()` - Team standings
3. `get_matchups()` - Weekly matchups with live scoring
4. `get_enhanced_boxscores()` - Enhanced boxscores with formatted tables ⭐ NEW
5. `get_power_rankings()` - Power rankings
6. `get_teams()` - Team list
7. `get_scoreboard()` - Scoreboard view
8. `get_player_info()` - Player lookup
9. `ping()` - Health check
10. `get_cache_stats()` - Cache observability
11. `clear_cache()` - Force fresh data

## Deployment Steps

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit: RFFL MCP server with observability"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/rffl-mcp-server.git
git push -u origin main
```

### 2. FastMCP Cloud Setup

1. Visit [gofastmcp.com](https://gofastmcp.com)
2. Sign in with GitHub
3. Create new project
4. Select your `rffl-mcp-server` repository

### 3. Configure Project

**Entrypoint:**
```
rffl_mcp_server.py:mcp
```

**Environment Variables** (Project → Settings → Environment):

**Required for all deployments:**
```
ESPN_LEAGUE_ID=323196
ESPN_YEAR=2025
ENABLE_CACHE=true
LOG_LEVEL=INFO
```

**Required for historical data (2018-2022) and private leagues:**
```
ESPN_S2=your_espn_s2_cookie_from_browser
SWID={your_swid_cookie_from_browser}
```

See "Getting ESPN Cookies" section in README.md for instructions.

### 4. Deploy

Click "Deploy" - FastMCP Cloud will:
- Clone your repo
- Install dependencies from `requirements.txt`
- Start the MCP server
- Generate endpoint: `https://<project>.fastmcp.app/mcp`

### 5. Test Deployment

Use the endpoint in any MCP-compatible client:

**Example smoke tests:**
```
# Health check
ping()

# Get league data
get_league()

# Get current week matchups
get_matchups(week=5)

# Get enhanced boxscores with formatted tables
get_enhanced_boxscores(week=5)

# Check cache performance
get_cache_stats()

# Get standings
get_standings()

# Get power rankings
get_power_rankings()
```

### 6. Create Installation Link (Optional)

To create a one-click installation link for Cursor users:

1. Your deployed endpoint: `https://<project>.fastmcp.app/mcp`
2. Create base64 encoded config:
   ```bash
   echo -n '{"url":"https://<project>.fastmcp.app/mcp"}' | base64
   ```
3. Build the deep link:
   ```
   cursor://anysphere.cursor-deeplink/mcp/install?name=<server-name>&config=<base64-config>
   ```

**Example:**
```
cursor://anysphere.cursor-deeplink/mcp/install?name=rffl-mcp-server&config=eyJ1cmwiOiJodHRwczovL3JmZmwtbWNwLXNlcnZlci5mYXN0bWNwLmFwcC9tY3AifQ%3D%3D
```

Add this link to your README for easy user onboarding!

## Monitoring & Observability

### Structured Logs

FastMCP Cloud dashboard shows JSON logs:
- Tool execution times
- Cache hit/miss rates
- ESPN API call durations
- Error tracking

### Cache Statistics

Monitor cache performance:
```
get_cache_stats()
```

Returns:
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

## Troubleshooting

### Authentication Errors

If you see:
```
"Unable to load league XXX (YYYY) without auth..."
```

**Causes:**
- Private league or historical data (2018-2022) requires ESPN_S2 and SWID cookies
- Missing or expired authentication cookies

**Solutions:**
1. Add `ESPN_S2` and `SWID` environment variables (see README.md for instructions)
2. Verify cookies are still valid (log into ESPN.com and get fresh values)
3. Redeploy after adding environment variables

### Cache Issues

If data seems stale:
```
clear_cache()
```

Or disable caching entirely:
```
ENABLE_CACHE=false
```

### Performance Issues

1. Check cache stats: `get_cache_stats()`
2. Enable debug logging: `LOG_LEVEL=DEBUG`
3. Monitor FastMCP Cloud logs dashboard
4. Consider disabling cache for testing: `ENABLE_CACHE=false`

## Production Configuration

**Recommended settings (public leagues, recent seasons):**
```
ESPN_LEAGUE_ID=<your_league_id>
ESPN_YEAR=2025
ENABLE_CACHE=true        # Better performance
LOG_LEVEL=INFO           # Balance detail vs noise
```

**With authentication (private leagues or historical data):**
```
ESPN_LEAGUE_ID=<your_league_id>
ESPN_YEAR=2025
ESPN_S2=<your_espn_s2_cookie>
SWID={your_swid_cookie}
ENABLE_CACHE=true
LOG_LEVEL=INFO
```

**Load testing settings:**
```
ENABLE_CACHE=false       # Test worst-case performance
LOG_LEVEL=DEBUG          # Maximum observability
```

## Important Notes

- ✅ **Supports both public and private leagues** (with ESPN authentication)
- ✅ **Historical data access** (2018-2022 requires ESPN_S2 and SWID cookies)
- ✅ **FastMCP Cloud handles** SSL, scaling, and logging dashboard
- ✅ **Free tier** suitable for personal use
- ✅ **Structured logs** for easy debugging
- ✅ **ChatMCP included** - test your tools directly in the browser

## Next Steps After Deployment

1. Test all tools with your league ID
2. Monitor cache hit rate (aim for 70%+ in production)
3. Review logs in FastMCP Cloud dashboard
4. Integrate with your AI agent/application
5. Set up any additional environment variables as needed

## Support

- FastMCP Docs: [gofastmcp.com](https://gofastmcp.com/getting-started/quickstart)
- ESPN API Wrapper: [github.com/cwendt94/espn-api](https://github.com/cwendt94/espn-api)
- MCP Protocol: [modelcontextprotocol.io](https://modelcontextprotocol.io)

