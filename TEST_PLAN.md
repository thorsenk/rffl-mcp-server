# RFFL MCP Server - Test Plan

## Overview
Comprehensive testing strategy to verify the MCP server works locally and on FastMCP Cloud deployment.

## Pre-Deployment Tests (Local)

### 1. Python Syntax & Import Validation

**Test:** Verify the code is syntactically correct and imports work
```bash
cd /Users/kthrcoedxmm16/rffl-mcp-server
python3 -m py_compile rffl_mcp_server.py
```
**Expected:** Exit code 0, no errors
**Status:** ✅ Already verified

---

### 2. Dependencies Check

**Test:** Verify requirements.txt is valid
```bash
cat requirements.txt
```
**Expected:**
```
fastmcp>=2.6,<3
espn_api>=0.45
```
**Status:** ✅ Already verified

---

### 3. Module Structure Validation

**Test:** Verify the `mcp` object can be imported (requires dependencies)
```bash
# Optional - only if you want to test locally
pip install -r requirements.txt
python3 -c "from rffl_mcp_server import mcp; print(f'Server: {mcp.name}'); print(f'Tools: {len(mcp._tools)}')"
```
**Expected:**
```
Server: rffl-mcp-server
Tools: 10
```
**Status:** ⏭️ Skip if dependencies not installed (FastMCP Cloud will handle this)

---

### 4. Tool Registration Check

**Test:** Verify all 10 tools are decorated with @mcp.tool
```bash
grep -c "^@mcp\.tool" rffl_mcp_server.py
```
**Expected:** `10`
**Status:** ✅ Already verified (10 tools found)

---

### 5. Configuration Validation

**Test:** Check all environment variables have defaults
```bash
grep -E "(DEFAULT_LEAGUE_ID|DEFAULT_YEAR|ENABLE_CACHE|LOG_LEVEL)" rffl_mcp_server.py
```
**Expected:** All variables present with fallback defaults
**Status:** ✅ Already verified

---

### 6. Git Repository Validation

**Test:** Verify code is pushed to GitHub
```bash
git remote -v
git log --oneline -1
```
**Expected:**
- Remote: `https://github.com/thorsenk/rffl-mcp-server.git`
- Commit present with all files
**Status:** ✅ Already verified

---

## FastMCP Cloud Deployment Tests

### 7. Repository Connection

**Test:** FastMCP Cloud can access the GitHub repository
- Go to [https://gofastmcp.com](https://gofastmcp.com)
- Sign in with GitHub
- Verify `thorsenk/rffl-mcp-server` appears in repository list

**Expected:** Repository is visible and selectable
**Status:** ⏳ Pending deployment

---

### 8. Entrypoint Configuration

**Test:** Set correct entrypoint in FastMCP Cloud
```
rffl_mcp_server.py:mcp
```

**Expected:** No import errors during deployment
**Status:** ⏳ Pending deployment

---

### 9. Environment Variables

**Test:** Configure required environment variables in FastMCP Cloud (Settings → Environment)
```
ESPN_LEAGUE_ID=323196
ESPN_YEAR=2025
ENABLE_CACHE=true
LOG_LEVEL=INFO
```

**Expected:** All variables accepted and saved
**Status:** ⏳ Pending deployment

---

### 10. Deployment Build

**Test:** FastMCP Cloud successfully builds and deploys
- Dependencies installed from `requirements.txt`
- Server starts without errors
- Endpoint generated: `https://<project>.fastmcp.app/mcp`

**Expected:**
- Build logs show successful installation
- Server status: Running
- Endpoint URL provided

**Status:** ⏳ Pending deployment

---

## Post-Deployment Functional Tests

### 11. Health Check Test

**Tool:** `ping()`
**Expected Response:** `"pong"`
**Purpose:** Verify server is responding
**Priority:** 🔴 Critical

---

### 12. League Data Test

**Tool:** `get_league()`
**Expected Response:**
```json
{
  "league_id": 323196,
  "year": 2025,
  "current_week": <number>,
  "nfl_week": <number>,
  "settings": {...},
  "teams": [...]
}
```
**Purpose:** Verify ESPN API connection works
**Priority:** 🔴 Critical

---

### 13. Standings Test

**Tool:** `get_standings()`
**Expected Response:**
```json
[
  {"rank": 1, "id": <team_id>, "name": "...", "wins": <n>, "losses": <n>, ...},
  ...
]
```
**Purpose:** Verify data retrieval and ordering
**Priority:** 🟡 Important

---

### 14. Matchups Test (Current Week)

**Tool:** `get_matchups()`
**Expected Response:**
```json
[
  {
    "week": <current_week>,
    "home": {"id": <n>, "name": "...", "score": <n>, ...},
    "away": {"id": <n>, "name": "...", "score": <n>, ...}
  },
  ...
]
```
**Purpose:** Verify box scores and live scoring
**Priority:** 🟡 Important

---

### 15. Matchups Test (Specific Week)

**Tool:** `get_matchups(week=5)`
**Expected Response:** Matchups for week 5
**Purpose:** Verify week parameter works
**Priority:** 🟢 Nice to have

---

### 16. Power Rankings Test

**Tool:** `get_power_rankings()`
**Expected Response:**
```json
[
  {"score": <float>, "team": {...}},
  ...
]
```
**Purpose:** Verify power rankings calculation
**Priority:** 🟢 Nice to have

---

### 17. Teams List Test

**Tool:** `get_teams()`
**Expected Response:** Array of all team objects
**Purpose:** Verify team data retrieval
**Priority:** 🟡 Important

---

### 18. Player Info Test

**Tool:** `get_player_info(name="Patrick Mahomes")`
**Expected Response:**
```json
{
  "name": "Patrick Mahomes",
  "playerId": <id>,
  "position": "QB",
  "proTeam": "KC",
  ...
}
```
**Purpose:** Verify player lookup functionality
**Priority:** 🟢 Nice to have

---

### 19. Cache Statistics Test (First Call)

**Tool:** `get_cache_stats()`
**Expected Response (fresh server):**
```json
{
  "enabled": true,
  "hits": 0,
  "misses": 1,
  "total_requests": 1,
  "hit_rate_percent": 0.0,
  "cached_leagues": 1
}
```
**Purpose:** Verify cache tracking works
**Priority:** 🟡 Important

---

### 20. Cache Statistics Test (After Multiple Calls)

**Steps:**
1. Call `get_league()` - cache miss
2. Call `get_standings()` - cache hit (same league)
3. Call `get_matchups()` - cache hit
4. Call `get_cache_stats()`

**Expected Response:**
```json
{
  "enabled": true,
  "hits": 2,
  "misses": 1,
  "total_requests": 3,
  "hit_rate_percent": 66.67,
  "cached_leagues": 1
}
```
**Purpose:** Verify cache is working correctly
**Priority:** 🔴 Critical

---

### 21. Clear Cache Test

**Steps:**
1. Call `get_cache_stats()` - note current stats
2. Call `clear_cache()`
3. Call `get_cache_stats()` - verify cache cleared

**Expected Response from clear_cache():**
```json
{
  "status": "success",
  "message": "Cleared 1 cached league(s)"
}
```

**Expected Response from get_cache_stats() after:**
```json
{
  "enabled": true,
  "hits": <prev>,
  "misses": <prev + 1>,
  ...
  "cached_leagues": 0
}
```
**Purpose:** Verify cache clearing works
**Priority:** 🟡 Important

---

### 22. Logging Verification

**Test:** Check FastMCP Cloud logs dashboard
**Expected Log Entries:**
```json
{"timestamp": "...", "level": "INFO", "message": "Fetching league from ESPN API", "cache_hit": false, ...}
{"timestamp": "...", "level": "INFO", "message": "Successfully loaded league from ESPN", "duration_ms": <n>, ...}
{"timestamp": "...", "level": "INFO", "message": "get_matchups completed", "tool": "get_matchups", "duration_ms": <n>, ...}
```
**Purpose:** Verify structured logging works
**Priority:** 🟡 Important

---

### 23. Cache Toggle Test (Disable)

**Test:** Update environment variable in FastMCP Cloud
```
ENABLE_CACHE=false
```
Redeploy, then call `get_cache_stats()`

**Expected Response:**
```json
{
  "enabled": false,
  ...
}
```
**Purpose:** Verify cache can be disabled
**Priority:** 🟢 Nice to have

---

### 24. Private League Error Test

**Test:** Call with a private league ID (if known)
```
get_league(league_id=<private_league_id>)
```

**Expected Response:** Error with message:
```
"Unable to load league XXX (YYYY) without auth. This build is PUBLIC-ONLY and does not support private leagues."
```
**Purpose:** Verify proper error handling for private leagues
**Priority:** 🟢 Nice to have

---

### 25. Performance Test

**Test:** Measure response times
- First call (cache miss): Should be 500-1500ms
- Second call (cache hit): Should be <100ms

**Purpose:** Verify caching improves performance
**Priority:** 🟡 Important

---

## Test Execution Checklist

### Phase 1: Pre-Deployment ✅
- [x] Python syntax validation
- [x] Dependencies check
- [x] Tool registration count
- [x] Configuration validation
- [x] Git push verification

### Phase 2: Deployment 🟦
- [ ] Connect repository to FastMCP Cloud
- [ ] Set entrypoint: `rffl_mcp_server.py:mcp`
- [ ] Configure environment variables
- [ ] Deploy and verify build succeeds
- [ ] Get endpoint URL

### Phase 3: Critical Tests (Must Pass) 🔴
- [ ] Test 11: `ping()` - Health check
- [ ] Test 12: `get_league()` - ESPN API connection
- [ ] Test 20: Cache hit rate increases over time
- [ ] Test 22: Logs appear in dashboard

### Phase 4: Important Tests (Should Pass) 🟡
- [ ] Test 13: `get_standings()` - Standings work
- [ ] Test 14: `get_matchups()` - Current week matchups
- [ ] Test 17: `get_teams()` - Teams list
- [ ] Test 19: `get_cache_stats()` - Initial cache stats
- [ ] Test 21: `clear_cache()` - Cache clearing
- [ ] Test 25: Performance (cache vs no-cache)

### Phase 5: Optional Tests (Nice to Have) 🟢
- [ ] Test 15: `get_matchups(week=5)` - Specific week
- [ ] Test 16: `get_power_rankings()` - Power rankings
- [ ] Test 18: `get_player_info()` - Player lookup
- [ ] Test 23: Cache toggle (disable)
- [ ] Test 24: Private league error handling

---

## Success Criteria

**Minimum to Deploy:**
- ✅ All Phase 1 tests pass
- ✅ Phase 2 deployment completes
- ✅ All Phase 3 critical tests pass

**Production Ready:**
- ✅ Minimum criteria met
- ✅ At least 80% of Phase 4 tests pass
- ✅ Cache hit rate >50% after 10+ requests
- ✅ Logs visible in FastMCP Cloud dashboard

---

## Troubleshooting Guide

### Issue: Deployment fails with import error
**Solution:** Verify entrypoint is exactly `rffl_mcp_server.py:mcp` (no `.py:` typo)

### Issue: ESPN API returns 401/403
**Solution:** League might be private. Verify league ID 323196 is public, or use a different public league

### Issue: Cache stats always show 0% hit rate
**Solution:** Check `ENABLE_CACHE=true` in environment variables. Verify multiple calls use same league_id/year

### Issue: No logs in dashboard
**Solution:** Check `LOG_LEVEL=INFO` or `DEBUG`. Verify structured logging is enabled

### Issue: Tools return empty data
**Solution:** Verify ESPN_YEAR matches current season. Check ESPN API isn't rate limiting

---

## Quick Test Script (Post-Deployment)

Once deployed, run these tests in order:

```python
# 1. Health check
ping()

# 2. Get league (cache miss)
get_league()

# 3. Get standings (cache hit)
get_standings()

# 4. Check cache stats (should show ~50% hit rate)
get_cache_stats()

# 5. Get current matchups
get_matchups()

# 6. Check cache again (hit rate should increase)
get_cache_stats()

# 7. Clear cache
clear_cache()

# 8. Verify cache cleared
get_cache_stats()
```

**Expected Results:**
- All calls succeed
- Cache hit rate increases from 0% → ~60-70%
- After clear_cache(), cached_leagues = 0
- Logs appear in FastMCP Cloud dashboard

---

## Next Steps After Testing

1. ✅ Complete Phase 1 (Pre-deployment) - **DONE**
2. 🟦 Complete Phase 2 (Deployment) - **READY TO START**
3. 🔴 Run Phase 3 (Critical tests) - **PENDING**
4. 🟡 Run Phase 4 (Important tests) - **PENDING**
5. 📊 Review logs and performance metrics
6. 🎯 Iterate based on findings

---

**Current Status:** Pre-deployment tests complete ✅
**Next Action:** Deploy to FastMCP Cloud and run functional tests

