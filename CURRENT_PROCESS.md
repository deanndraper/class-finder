# Current Process Analysis

## Overview
We've built a web scraping system for Montgomery College course data that has evolved through multiple iterations, leading to some complexity and inconsistencies.

## Current Architecture

### 1. Frontend (Web Interface)
- **File**: `frontend/index.html`, `frontend/script_api.js`, `frontend/styles.css`
- **Purpose**: Professional web interface for course searching
- **Features**: 
  - Form with term, subject, course number, campus selection
  - "Available Only" checkbox for filtering
  - Results display with summary cards and course tables
  - Export functionality (HTML, JSON, CSV)

### 2. Backend API (Flask Server)
- **File**: `backend_api.py`
- **Port**: 8080
- **Purpose**: REST API that connects frontend to scraping logic
- **Key Endpoint**: `POST /api/search` - receives search criteria, returns course data
- **Integration**: Uses `MontgomeryCollegeScraper` class from `generic_course_scraper.py`

### 3. Scraping Engine (Core Logic)
- **File**: `generic_course_scraper.py`
- **Class**: `MontgomeryCollegeScraper`
- **Purpose**: Automated web scraping of Montgomery College course catalog
- **Caching**: 30-minute cache system in `course_cache/` directory

## Current Scraping Process

### Step 1: Navigation
1. Launch Playwright browser (headless)
2. Navigate to: `https://mcssb.glb.montgomerycollege.edu/eagle/bwckschd.p_disp_dyn_sched`
3. Select academic term (e.g., "Fall 2025")
4. Submit to reach subject selection page

### Step 2: Subject Selection
1. Get all available subject options from dropdown
2. **Find subject match using improved logic**:
   - First: Look for exact prefix match (e.g., "COMM-Communication Studies")
   - Fallback: Look for contains match
3. Select the matched subject option
4. Click "Class Search" to get results

### Step 3: Data Extraction
**Current Method**: JavaScript evaluation that parses `document.body.innerText`

**Pattern Matching**:
```javascript
// Look for lines matching: SUBJECTCODE + digits + space + 5-digit CRN
const coursePattern = new RegExp(`^${subject}\\d+\\s+\\d{5}`);
```

**Data Structure Expected**:
```
BIOL101	20125	4.000	TR	9:00 AM - 9:50 AM	09/02/25 - 12/21/25	
[empty line]
0          <- Seats Available
[empty line]
0          <- Waitlist Count  
[empty line]
Rockville	SC 124	Amina Gaber 	Lecture
```

### Step 4: Parsing Logic
**For each course line found**:
1. Extract: course code, CRN, credits, days from main line
2. Extract: time and dates using regex patterns
3. **Look ahead 8 lines** for:
   - Single numbers on their own lines (seats, then waitlist)
   - Campus information (Rockville/Germantown/Takoma/Distance)
   - Location and instructor (tab-separated in campus line)

## Known Issues

### 1. Inconsistent Data Quality
**Problem**: Different subjects have different HTML structures
- **BIOL**: Works well, finds 177 courses
- **MATH**: Works well, finds 282 courses  
- **COMM**: Finds 107 courses but data quality issues

### 2. Missing Campus/Instructor Data
**Current Output Example**:
```json
{
  "course": "BIOL101",
  "crn": "20125", 
  "seatsAvailable": 0,
  "waitlistCount": 0,
  "campus": "TBA",        // ← Should be "Rockville"
  "location": "TBA",      // ← Should be "SC 124"
  "instructor": "TBA"     // ← Should be "Amina Gaber"
}
```

### 3. Waitlist Always Zero Issue
**Current Problem**: As you noted, waitlist counts are coming back as 0
**Likely Cause**: The parsing logic for finding the second number (waitlist) isn't working correctly

### 4. Complex Parsing Logic
**Challenge**: The JavaScript evaluation approach is trying to parse complex, inconsistent HTML structure
**Result**: Brittle parsing that works differently for different subjects

## Files and Their Purposes

### Core System Files
- `generic_course_scraper.py` - Main scraping engine (current approach)
- `backend_api.py` - Flask API server
- `frontend/` - Web interface

### Legacy/Development Files
- `complete_automation.py` - Older COMM-specific automation
- `corrected_comm_data.py` - Hardcoded COMM data for fallback
- `course_scraper.py` - Earlier scraping attempt
- `automated_course_scraper.py` - Another iteration

### Debug/Test Files
- `test_suite.py` - Comprehensive testing framework
- `debug_*.py` - Various debugging scripts
- `simple_biol_extractor.py` - Simple working extraction (107 lines, worked well)
- Various `*_scraper.py` files - Development iterations

### Generated Files (Excluded from Git)
- `course_cache/` - Cached scraping results
- `automated_*.html` - Generated reports
- `*.png` - Debug screenshots
- `*_debug.png`, `*_page_text.txt` - Debug artifacts

## What's Working

### ✅ Successful Components
1. **Frontend Interface**: Professional, responsive, good UX
2. **API Integration**: Clean REST API with proper error handling
3. **Subject Detection**: Now correctly finds "COMM-Communication Studies" vs "ADS-Community Arts"
4. **Caching System**: 30-minute intelligent caching
5. **Multiple Subject Support**: Works with BIOL, MATH, COMM
6. **Course Count Accuracy**: Finds correct number of courses per subject

### ✅ Checkbox Filtering
- Frontend properly sends `availability: true/false`
- Backend correctly filters results
- UI shows clear difference between filtered/unfiltered views

## What's Not Working

### ❌ Data Quality Issues
1. **Campus Extraction**: Often shows "TBA" instead of actual campus
2. **Waitlist Parsing**: Always returns 0 instead of actual waitlist count
3. **Instructor/Location**: Missing in most results
4. **Seats Available**: May be inaccurate

### ❌ Parsing Reliability
- Different subjects have different HTML structures
- Current approach tries to handle all with one pattern
- Brittle JavaScript evaluation method

## Alternative Approaches Considered

### 1. Table-Based Parsing
Some subjects may use HTML tables instead of text patterns

### 2. BeautifulSoup HTML Parsing
Could use Python HTML parsing instead of JavaScript text parsing

### 3. Subject-Specific Parsers
Different parsing logic for different subjects based on their structure

### 4. Screenshot + OCR
Visual parsing approach (probably overkill)

## Next Steps Considerations

### Option A: Fix Current Approach
- Debug why waitlist parsing fails
- Improve campus/instructor extraction
- Make parsing more robust

### Option B: Redesign Parsing Strategy
- Use HTML structure analysis instead of text parsing
- Create subject-specific parsing logic
- Use BeautifulSoup for structured HTML parsing

### Option C: Hybrid Approach
- Keep working components (frontend, API, caching)
- Replace only the extraction logic
- Use simpler, more reliable parsing method

## Current System Status
- **Frontend**: ✅ Working well
- **Backend API**: ✅ Working well  
- **Subject Detection**: ✅ Fixed and working
- **Course Discovery**: ✅ Finds correct course counts
- **Data Extraction**: ❌ Inconsistent quality, missing key data
- **Caching**: ✅ Working well
- **Git Setup**: ✅ Properly configured

## Recommendation
The core architecture (frontend → API → scraper → cache) is solid. The issue is specifically in the data extraction/parsing logic within `generic_course_scraper.py`. We should focus on that component rather than rebuilding the entire system.