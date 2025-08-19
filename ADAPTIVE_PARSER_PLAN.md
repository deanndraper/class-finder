# Adaptive Parser Architecture Plan

## Overview
Create a self-improving parser system that can detect parsing failures and generate new parsing strategies automatically. The system will use multiple parser strategies with fallback mechanisms and user-driven improvement cycles.

## Core Architecture

### 1. Parser Registry System
```
parsers/
├── registry.json              # Parser metadata and priority
├── specific_parsers/          # Subject-specific parsers
│   ├── COMM_parser.py
│   ├── ENGL_parser.py
│   ├── MATH_parser.py
│   └── BIOL_parser.py
├── general_parsers/           # General parsing strategies  
│   ├── table_parser.py        # Current table-based parser
│   ├── text_parser.py         # Original text-based parser
│   └── hybrid_parser.py       # Mixed approach parser
└── parser_base.py             # Base parser interface
```

### 2. Parser Selection Logic
```python
class ParserManager:
    def get_best_parser(self, subject, term, campus):
        # 1. Check for specific parser (COMM_parser.py)
        # 2. Fallback to general parsers by priority
        # 3. Return default parser if none found
        
    def evaluate_parse_quality(self, results):
        # Detect parsing issues:
        # - High % of TBA values
        # - All waitlist = 0
        # - Missing critical fields
        # Return quality score 0-100
```

### 3. Quality Assessment Metrics
```python
QUALITY_METRICS = {
    'waitlist_diversity': {
        'weight': 30,
        'check': 'percentage of non-zero waitlist values > 10%'
    },
    'campus_completeness': {
        'weight': 25,
        'check': 'percentage of non-TBA campus values > 90%'
    },
    'instructor_completeness': {
        'weight': 20,
        'check': 'percentage of non-TBA instructor values > 80%'
    },
    'location_completeness': {
        'weight': 15,
        'check': 'percentage of non-TBA location values > 70%'
    },
    'data_consistency': {
        'weight': 10,
        'check': 'consistent field formats and reasonable values'
    }
}
```

## Implementation Plan

### Phase 1: Core Infrastructure

#### A. Parser Base Class
```python
# parsers/parser_base.py
class BaseParser:
    def __init__(self, name, priority=100):
        self.name = name
        self.priority = priority
        
    async def extract_course_data(self, page, subject):
        raise NotImplementedError
        
    def get_quality_score(self, results):
        # Implement quality assessment
        pass
        
    def can_handle(self, subject, term=None, campus=None):
        # Override in specific parsers
        return True
```

#### B. Parser Registry
```python
# parsers/registry.json
{
    "parsers": [
        {
            "name": "COMM_specific",
            "file": "specific_parsers/COMM_parser.py",
            "priority": 1,
            "subjects": ["COMM"],
            "created": "2025-08-19",
            "success_rate": 95,
            "last_updated": "2025-08-19"
        },
        {
            "name": "table_general",
            "file": "general_parsers/table_parser.py", 
            "priority": 10,
            "subjects": ["*"],
            "success_rate": 85
        },
        {
            "name": "text_fallback",
            "file": "general_parsers/text_parser.py",
            "priority": 90,
            "subjects": ["*"],
            "success_rate": 60
        }
    ]
}
```

#### C. Modified Course Scraper
```python
# Updated generic_course_scraper.py
class MontgomeryCollegeScraper:
    def __init__(self):
        self.parser_manager = ParserManager()
        
    async def scrape_courses(self, term, subject, ...):
        # Existing code...
        
        # Use adaptive parser selection
        parser = self.parser_manager.get_best_parser(subject, term, campus)
        courses = await parser.extract_course_data(page, subject)
        
        # Evaluate quality
        quality_score = parser.get_quality_score(courses)
        
        # Return results with metadata
        return {
            'courses': courses,
            'metadata': {
                'parser_used': parser.name,
                'quality_score': quality_score,
                'needs_improvement': quality_score < 75,
                'total_courses': len(courses)
            }
        }
```

### Phase 2: Frontend Quality Indicators

#### A. Result Quality Display
```javascript
// frontend/script_api.js - Updated showResults function
function showResults(results, metadata) {
    // Existing display logic...
    
    // Add quality indicator
    if (metadata.quality_score < 75) {
        showQualityWarning(metadata);
    }
    
    // Add user feedback section
    addUserFeedbackSection();
}

function showQualityWarning(metadata) {
    const warningHtml = `
        <div class="quality-warning">
            ⚠️ Data Quality Issue Detected
            <p>Parser: ${metadata.parser_used} (Score: ${metadata.quality_score}/100)</p>
            <p>Some course information may be incomplete or inaccurate.</p>
            <button onclick="reportParsingIssue()">Report Issue & Improve Parser</button>
        </div>
    `;
    document.getElementById('qualityIndicator').innerHTML = warningHtml;
}
```

#### B. User Feedback System
```javascript
function addUserFeedbackSection() {
    const feedbackHtml = `
        <div class="user-feedback">
            <h3>How is this data quality?</h3>
            <button onclick="reportGoodData()">✅ Data looks accurate</button>
            <button onclick="reportBadData()">❌ Data has issues</button>
        </div>
    `;
    document.getElementById('userFeedback').innerHTML = feedbackHtml;
}
```

### Phase 3: Parser Generation Tool

#### A. Parser Tool CLI
```bash
# tools/parser_generator.py
python parser_generator.py --subject ENGL --term "Fall 2025" --debug-mode
```

#### B. Claude Code Integration
```python
# tools/parser_generator.py
class ParserGenerator:
    def __init__(self):
        self.claude_code_available = self.check_claude_code()
        
    async def generate_new_parser(self, subject, term, campus=None):
        print(f"🤖 Generating new parser for {subject} {term}")
        
        # 1. Scrape sample data with existing parsers
        sample_data = await self.collect_sample_data(subject, term)
        
        # 2. Generate Claude Code prompt
        prompt = self.create_parser_prompt(subject, sample_data)
        
        # 3. Call Claude Code to generate parser
        if self.claude_code_available:
            new_parser_code = self.call_claude_code(prompt)
            
            # 4. Test generated parser
            if await self.test_parser(new_parser_code, subject):
                # 5. Save and register new parser
                self.save_parser(new_parser_code, subject)
                self.update_registry(subject, priority=1)
                print("✅ New parser generated and registered!")
            else:
                print("❌ Generated parser failed tests")
        else:
            print("❌ Claude Code not available. Manual parser creation required.")
    
    def create_parser_prompt(self, subject, sample_data):
        return f"""
        Create a Python parser for Montgomery College {subject} courses.
        
        Sample HTML structure:
        {sample_data['html_structure']}
        
        Existing parser results (potentially flawed):
        {sample_data['current_results']}
        
        Requirements:
        - Extract: course, crn, credits, days, time, dates, seatsAvailable, waitlistCount, campus, location, instructor
        - Handle edge cases for {subject} specifically
        - Return quality score > 90
        
        Generate a complete parser class that inherits from BaseParser.
        """
```

### Phase 4: Advanced Features

#### A. Parser Performance Tracking
```python
# parsers/performance_tracker.py
class PerformanceTracker:
    def log_parse_attempt(self, parser_name, subject, quality_score, user_feedback):
        # Track parser success rates
        # Identify patterns in failures
        # Recommend parser improvements
        pass
```

#### B. Automatic Parser Testing
```python
# tests/parser_test_suite.py
class ParserTestSuite:
    def test_all_parsers(self):
        # Run comprehensive tests on all registered parsers
        # Compare results across different parsing strategies  
        # Generate test reports
        pass
```

## API Changes

### 1. Enhanced Search Response
```json
{
    "success": true,
    "results": [...],
    "totalResults": 109,
    "availableResults": 45,
    "metadata": {
        "parser_used": "COMM_specific",
        "quality_score": 95,
        "needs_improvement": false,
        "parsing_time": 2.3,
        "cache_used": true
    },
    "quality_issues": []
}
```

### 2. New API Endpoints
```python
# New endpoints in backend_api.py
@app.route('/api/parser-status', methods=['GET'])
def get_parser_status():
    # Return available parsers and their performance

@app.route('/api/report-quality', methods=['POST'])  
def report_data_quality():
    # Log user feedback on data quality

@app.route('/api/trigger-parser-generation', methods=['POST'])
def trigger_parser_generation():
    # Start parser generation process (admin only)
```

## File Structure Changes

```
project/
├── parsers/                    # NEW: Parser system
│   ├── __init__.py
│   ├── parser_base.py
│   ├── parser_manager.py
│   ├── registry.json
│   ├── specific_parsers/
│   └── general_parsers/
├── tools/                      # NEW: Parser generation tools
│   ├── parser_generator.py
│   └── parser_tester.py
├── frontend/
│   ├── index.html             # Updated with quality indicators
│   ├── script_api.js          # Updated with feedback system
│   └── styles.css             # Updated styles
├── generic_course_scraper.py   # Modified to use parser system
├── backend_api.py             # Updated with new endpoints
└── tests/
    └── parser_test_suite.py    # NEW: Comprehensive parser testing
```

## Potential Issues & Improvements

### Issues to Consider:

1. **Parser Generation Reliability**: Claude Code generated parsers may not always work correctly
   - **Solution**: Implement robust testing and validation before deployment

2. **Performance Overhead**: Multiple parser attempts could slow down responses
   - **Solution**: Cache parser quality scores, fail fast on known bad parsers

3. **Parser Conflict**: Multiple parsers might conflict or override each other
   - **Solution**: Clear priority system and parser versioning

4. **User Experience**: Too many quality warnings might confuse users  
   - **Solution**: Progressive disclosure - only show warnings for significant issues

5. **Security Concerns**: Dynamically generated parsers could be malicious
   - **Solution**: Sandboxed execution environment for generated parsers

### Improvements to Consider:

1. **Machine Learning Integration**: Use ML to predict which parser will work best
2. **A/B Testing**: Compare multiple parsers simultaneously 
3. **Community Parsers**: Allow users to submit and vote on parser improvements
4. **Real-time Monitoring**: Continuous quality assessment during scraping
5. **Parser Analytics Dashboard**: Visualize parser performance over time
6. **Automated Parser Updates**: Self-updating parsers based on website changes

## Implementation Priority:

1. **Phase 1 (High Priority)**: Core parser infrastructure and registry system
2. **Phase 2 (Medium Priority)**: Frontend quality indicators and user feedback
3. **Phase 3 (Medium Priority)**: Basic parser generation tool
4. **Phase 4 (Low Priority)**: Advanced analytics and ML features

## Success Metrics:

- **Data Quality**: Average quality score > 90 across all subjects
- **User Satisfaction**: <5% of searches result in quality complaints
- **Parser Coverage**: Specific parsers for top 10 most-used subjects
- **System Reliability**: <1% of searches fail due to parser issues
- **Improvement Speed**: New parsers generated and deployed within 1 hour of issue report

This architecture provides a robust, scalable solution that can adapt to changing website structures while maintaining high data quality and user experience.