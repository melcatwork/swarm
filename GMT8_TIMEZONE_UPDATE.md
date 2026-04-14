# GMT+8 Timezone Update

**Date**: 2026-04-14
**Status**: ✅ Completed

## Overview
Updated the entire project to use GMT+8 timezone consistently across both frontend and backend components.

## Changes Made

### Backend Changes

#### 1. Created Timezone Utility (`backend/app/utils/timezone.py`)
- New utility module for consistent GMT+8 timezone handling
- **Functions**:
  - `now_gmt8()` - Get current datetime in GMT+8
  - `now_gmt8_iso()` - Get current datetime as ISO 8601 string with +08:00 suffix
  - `to_gmt8(dt)` - Convert any datetime to GMT+8
  - `parse_iso_to_gmt8(iso_string)` - Parse ISO 8601 string to GMT+8
  - `format_gmt8(dt, format_str)` - Format datetime in GMT+8

#### 2. Updated Archive Service (`backend/app/services/archive_service.py`)
- Replaced `datetime.utcnow()` with `now_gmt8()`
- Replaced `datetime.utcnow().isoformat() + "Z"` with `now_gmt8_iso()`
- **Affected methods**:
  - `generate_run_id()` - Now uses GMT+8 for run ID timestamps
  - `generate_default_name()` - Now uses GMT+8 for default names
  - `save_run()` - Created timestamps now in GMT+8
  - `update_run_name()` - Updated timestamps now in GMT+8

#### 3. Updated Job Tracker (`backend/app/swarm/job_tracker.py`)
- Replaced all `datetime.now(timezone.utc)` with `now_gmt8()`
- **Affected methods**:
  - `Job.__init__()` - Start time in GMT+8
  - `Job.update_status()` - Log timestamps in GMT+8
  - `Job.complete()` - Completion time in GMT+8
  - `Job.fail()` - Failure time in GMT+8

#### 4. Updated Parsers (`backend/app/parsers/`)
- Updated both Terraform and CloudFormation parsers to use GMT+8
- **Files changed**:
  - `cloudformation_parser.py` - `parsed_at` timestamp in GMT+8
  - `terraform_parser.py` - `parsed_at` timestamp in GMT+8

#### 5. Updated Threat Intel Adapters (`backend/app/threat_intel/adapters/`)
- Updated all threat intelligence adapters to use GMT+8
- **Files changed**:
  - `nvd_cve.py` - CVE fetch times and fallback timestamps in GMT+8
  - `hackernews_rss.py` - RSS feed parsing fallback timestamps in GMT+8
  - `attack_stix.py` - STIX cache age checking and fallback timestamps in GMT+8

#### 6. Updated Threat Intel Core (`backend/app/threat_intel/core/`)
- Updated threat intelligence scoring and feed management to use GMT+8
- **Files changed**:
  - `scorer.py` - Recency calculations for threat intel scoring in GMT+8
  - `feed_manager.py` - Feed status last_fetch timestamps in GMT+8

### Frontend Changes

#### 7. Enhanced Formatters (`frontend/src/utils/formatters.js`)
- Added GMT+8 conversion utilities
- **New functions**:
  - `toGMT8(date)` - Convert date to GMT+8
  - `nowGMT8()` - Get current time in GMT+8
  - `formatGMT8Date(date, options)` - Format date in GMT+8 with custom options
  - `formatGMT8DateShort(date)` - Format date as "Apr 14, 2026"
  - `formatGMT8Time(date)` - Format time as "03:30 PM"
  - `formatGMT8DateTime(date)` - Format full datetime in GMT+8
- **Updated functions**:
  - `formatRelativeTime()` - Now uses GMT+8 for calculations

#### 8. Updated Threat Model Page (`frontend/src/pages/ThreatModelPage.jsx`)
- Imported new GMT+8 formatters
- Updated archived run timestamp display to show GMT+8 explicitly
- Format: "Apr 14, 2026 at 03:30 PM GMT+8"

## Testing Verification

### Backend Tests
```bash
✅ Timezone utility import and function test
✅ Archive service initialization with GMT+8
✅ Job tracker initialization with GMT+8
✅ Parser modules updated with GMT+8
✅ Threat intel adapters updated with GMT+8
✅ Threat intel core modules updated with GMT+8
✅ Backend server health check after changes
✅ Backend API endpoints responding correctly
```

### Example Output
```
GMT+8 time: 2026-04-14T14:40:09.336264+08:00
Service initialized successfully
Job tracker initialized successfully
Backend status: ok
LLM provider: ollama (6 models available)
```

## Benefits

1. **Consistency**: All timestamps across the application now use GMT+8
2. **Clarity**: Timestamps explicitly show GMT+8 timezone in frontend
3. **Accuracy**: Relative time calculations use GMT+8 for correct results
4. **Maintainability**: Centralized timezone utilities make future changes easier
5. **User Experience**: Users see times in their expected timezone (GMT+8)

## Backward Compatibility

- Existing timestamps stored with UTC or other timezones will be automatically converted to GMT+8 for display
- ISO 8601 format preserved for API responses with explicit +08:00 timezone suffix
- No breaking changes to API contracts

## Files Modified

### Backend (11 files)
- `backend/app/utils/__init__.py` (new)
- `backend/app/utils/timezone.py` (new)
- `backend/app/services/archive_service.py`
- `backend/app/swarm/job_tracker.py`
- `backend/app/parsers/cloudformation_parser.py`
- `backend/app/parsers/terraform_parser.py`
- `backend/app/threat_intel/adapters/nvd_cve.py`
- `backend/app/threat_intel/adapters/hackernews_rss.py`
- `backend/app/threat_intel/adapters/attack_stix.py`
- `backend/app/threat_intel/core/scorer.py`
- `backend/app/threat_intel/core/feed_manager.py`

### Frontend (2 files)
- `frontend/src/utils/formatters.js`
- `frontend/src/pages/ThreatModelPage.jsx`

## Documentation Updates Needed

- Update CLAUDE.md to reflect GMT+8 as the standard timezone
- Add timezone information to API documentation
- Update README.md with timezone information

## Future Considerations

1. Consider adding timezone preference to user settings if multi-timezone support needed
2. Add GMT+8 timezone indicator to more UI components
3. Consider adding timezone conversion utilities for other timezones if needed

## Notes

- All new timestamps will use ISO 8601 format with explicit +08:00 suffix
- Example: `2026-04-14T14:36:54.758404+08:00`
- Frontend uses `Asia/Singapore` timezone (equivalent to GMT+8) for Intl.DateTimeFormat
- Backend uses Python's `timezone(timedelta(hours=8))` for GMT+8
