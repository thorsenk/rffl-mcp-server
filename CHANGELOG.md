# Changelog

All notable changes to the RFFL MCP Server project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.2.0] - 2025-10-20

### Fixed
- **Critical:** `get_matchups()` now works for ALL years 2011-2025 for simple matchups
  - Previously failed for years < 2019 with "Can't use box score before 2019" error
  - Now uses `scoreboard()` API for simple data (works all years)
  - Uses `box_scores()` only when `include_lineups=True` (2019+ only)
  - Significant performance improvement for default calls (commit `a4bfe23`)

- **Critical:** Fixed FastMCP Cloud deployment failures
  - Removed `.claude/` directory (local dev hooks) from repository
  - Added `.claude/` and `.cursor/` to `.gitignore`
  - Deployments now succeed reliably (commit `6559672`)

### Changed
- Updated data availability documentation
  - Simple matchups: Now documented as working 2011-2025
  - Enhanced boxscores: Clarified rolling ~7 year window (currently 2019-2025)
- Improved deployment documentation with troubleshooting guide
- Enhanced test documentation with health check results (94.1% pass rate)

### Documentation
- Added comprehensive health check results (32/34 tests passing)
- Created `PROJECT_HEALTH_REPORT.md` with detailed analysis
- Created `DEPLOYMENT_FIX_SUMMARY.md` explaining deployment issue resolution
- Organized historical health reports into `docs/health-reports/` subdirectory

---

## [1.1.0] - 2025-10-20

### Added
- Comprehensive health check suite (`test_mcp_health.py`)
  - 34 tests across 8 categories
  - Connectivity, cache, current season, historical data, accuracy, features, error handling, performance
- Dedicated verification tests for `get_matchups()` fix (`test_get_matchups_fix.py`)
- Project health reporting system with detailed metrics

### Documentation
- Created detailed deployment troubleshooting guide
- Updated README with improved data availability matrix
- Enhanced TEST_PLAN with current test status

---

## [1.0.0] - 2025-10-14

### Added
- ESPN Fantasy Football MCP server with 11 tools:
  - Core: `get_league`, `get_standings`, `get_matchups`, `get_enhanced_boxscores`, `get_power_rankings`, `get_teams`, `get_scoreboard`, `get_player_info`
  - Observability: `get_cache_stats`, `clear_cache`, `ping`
- **Authentication support** for historical data (2011-2025)
  - ESPN_S2 and SWID cookie authentication
  - Contextual error messages based on auth state and year
- **Configurable caching system**
  - In-memory league cache with hit/miss tracking
  - `ENABLE_CACHE` environment variable toggle
  - Cache statistics and clearing capabilities
- **Structured JSON logging**
  - FastMCP Cloud dashboard compatible
  - Contextual fields: `tool`, `duration_ms`, `cache_hit`, `league_id`, `year`, `week`, `status`
- **Fantasy-expert prompt** for improved natural language understanding
  - Maps natural language to tool calls
  - Extracts years and weeks from user queries
  - Provides fantasy football context

### Documentation
- `README.md` - User documentation with quick start guide
- `CLAUDE.md` - Developer guidance and architecture details
- `DEPLOYMENT.md` - FastMCP Cloud deployment checklist
- `TEST_PLAN.md` - Comprehensive testing strategy
- `HISTORICAL_DATA_FIX.md` - Historical data access investigation and implementation
- `MIGRATION_GUIDE.md` - Guide for adding authentication support

### Technical Details
- Built with FastMCP framework
- Uses `espn-api` (cwendt94) for ESPN API access
- Supports stdio, HTTP, and SSE transports
- Python 3.8+ compatible

---

## Performance Characteristics

### Cache Performance
- **Enabled (default):** 700-800x speedup on cached requests
- **Hit rate target:** 70%+ in production
- **Response times:**
  - League data: ~700ms (initial) → 0ms (cached)
  - Matchups: ~300ms average
  - All cached requests: < 1ms

### Data Availability
| Year Range | Simple Matchups | Enhanced Boxscores | Authentication Required |
|------------|----------------|-------------------|------------------------|
| 2023-2025 | ✅ | ✅ | Optional (public leagues) |
| 2019-2022 | ✅ | ✅ | **Required** |
| 2011-2018 | ✅ | ⚠️ Limited | **Required** |
| 2010 and earlier | ⚠️ Limited | ⚠️ Limited | **Required** |

---

## Known Issues

### Minor (Non-Critical)
1. **Power Rankings Sorting** - Rankings may not be sorted by score (ESPN API behavior)
2. **Week Number Validation** - API accepts invalid weeks without explicit error

These issues do not affect core functionality and are prioritized for future fixes.

---

## Upgrade Notes

### From Pre-1.0 to 1.0+
- Add `ESPN_S2` and `SWID` environment variables for historical data access
- Update `.env` file with authentication cookies
- No code changes required

### From 1.0 to 1.2+
- If upgrading from version with `.claude/` in repository:
  1. Remove from git: `git rm -r --cached .claude/`
  2. Ensure `.gitignore` includes `.claude/` and `.cursor/`
  3. Commit and push changes
- Redeploy to FastMCP Cloud if deployments were failing

---

## Testing Status

**Current:** ✅ **94.1% (A-)**
- **Passed:** 32/34 comprehensive tests
- **Categories:** 8 (Connectivity, Cache, Current Season, Historical Data, Data Accuracy, Enhanced Features, Error Handling, Performance)
- **Deployment:** ✅ Production (FastMCP Cloud)

---

## Links

- **Repository:** https://github.com/thorsenk/rffl-mcp-server
- **FastMCP Cloud:** https://rffl-mcp-server.fastmcp.app/mcp
- **Documentation:** See README.md, CLAUDE.md, and other guides in repository

---

## Acknowledgments

- Built with [FastMCP](https://gofastmcp.com) framework
- ESPN API wrapper by [cwendt94/espn-api](https://github.com/cwendt94/espn-api)
- Development assistance by [Claude Code](https://claude.com/claude-code)

---

**Legend:**
- ✅ = Fully supported
- ⚠️ = Limited support or known issues
- ❌ = Not supported

