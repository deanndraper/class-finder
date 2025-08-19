#!/usr/bin/env python3
"""
Montgomery College Course Finder - Backend API
Flask API to serve the frontend and handle course search requests
"""

import asyncio
import json
import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS

# Import our automation scripts
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from complete_automation import complete_automated_search
    from corrected_comm_data import REAL_COMM_COURSES
    from generic_course_scraper import MontgomeryCollegeScraper
    print("✅ Successfully imported MontgomeryCollegeScraper")
except ImportError as e:
    print(f"⚠️ Import error: {e}")
    print("Using mock data.")
    complete_automated_search = None
    REAL_COMM_COURSES = []
    MontgomeryCollegeScraper = None

app = Flask(__name__, 
           static_folder='frontend',
           template_folder='frontend')
CORS(app)

# Sample course data for development/demo
SAMPLE_COURSES = [
    {
        "course": "COMM108",
        "crn": "20388",
        "courseTitle": "Foundations of Human Communication",
        "section": "001",
        "credits": "3.000",
        "days": "TR",
        "time": "8:00 AM - 9:15 AM",
        "dates": "09/02/25 - 12/21/25",
        "seatsAvailable": 2,
        "waitlistCount": 5,
        "campus": "Rockville",
        "location": "TA 210",
        "instructor": "Teodora Salow",
        "hasAvailability": False,
        "status": "❌ 2 ≤ 5"
    },
    {
        "course": "COMM108",
        "crn": "22373",
        "courseTitle": "Foundations of Human Communication",
        "section": "002",
        "credits": "3.000",
        "days": "TR", 
        "time": "8:00 AM - 9:15 AM",
        "dates": "09/02/25 - 12/21/25",
        "seatsAvailable": 0,
        "waitlistCount": 1,
        "campus": "Germantown",
        "location": "HT 403",
        "instructor": "Luis Botello",
        "hasAvailability": False,
        "status": "❌ 0 ≤ 1"
    },
    {
        "course": "COMM112",
        "crn": "20398",
        "courseTitle": "Public Speaking",
        "section": "001",
        "credits": "3.000",
        "days": "MW",
        "time": "10:00 AM - 11:15 AM",
        "dates": "09/02/25 - 12/21/25",
        "seatsAvailable": 8,
        "waitlistCount": 2,
        "campus": "Rockville",
        "location": "TA 215",
        "instructor": "Sarah Johnson",
        "hasAvailability": True,
        "status": "✅ 8 > 2"
    },
    {
        "course": "MATH140",
        "crn": "21000",
        "courseTitle": "Precalculus",
        "section": "001",
        "credits": "4.000",
        "days": "MTWF",
        "time": "9:00 AM - 9:50 AM",
        "dates": "09/02/25 - 12/21/25",
        "seatsAvailable": 12,
        "waitlistCount": 3,
        "campus": "Rockville",
        "location": "SM 120",
        "instructor": "Dr. Martinez",
        "hasAvailability": True,
        "status": "✅ 12 > 3"
    }
]

@app.route('/')
def index():
    """Serve the main frontend page"""
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files (CSS, JS, images)"""
    return send_from_directory('frontend', filename)

@app.route('/api/search', methods=['POST'])
def search_courses():
    """
    API endpoint for course search
    Expects JSON payload with search criteria
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'term' not in data or 'subject' not in data:
            return jsonify({
                'error': 'Missing required fields: term and subject'
            }), 400
        
        # Extract search criteria
        search_criteria = {
            'term': data['term'],
            'subject': data['subject'],
            'course_number': data.get('courseNumber'),
            'campus': data.get('campus'),
            'availability_only': data.get('availability', False)
        }
        
        print(f"🔍 API Search request: {search_criteria}")
        
        # Perform the search using generic scraper
        if MontgomeryCollegeScraper:
            # Use generic course scraper for all subjects
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                # Create scraper instance and use it
                scraper = MontgomeryCollegeScraper()
                results = loop.run_until_complete(
                    scraper.scrape_courses(
                        term=search_criteria['term'],
                        subject=search_criteria['subject'],
                        course_filter=search_criteria['course_number'],
                        campus_filter=search_criteria['campus'],
                        use_cache=True  # 30-minute cache for performance
                    )
                )
            finally:
                loop.close()
        elif complete_automated_search and search_criteria['subject'] == 'COMM':
            # Fallback to old COMM-specific automation
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                results = loop.run_until_complete(
                    complete_automated_search(
                        term=search_criteria['term'],
                        subject=search_criteria['subject'],
                        course_filter=search_criteria['course_number'],
                        campus_filter=search_criteria['campus'],
                        simulate_real_data=True
                    )
                )
            finally:
                loop.close()
        else:
            # Use sample data for development
            results = filter_sample_data(search_criteria)
        
        # Filter results if availability only is requested
        if search_criteria['availability_only']:
            results = [r for r in results if r.get('hasAvailability', False)]
        
        # Prepare response
        response = {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'searchCriteria': search_criteria,
            'totalResults': len(results),
            'availableResults': len([r for r in results if r.get('hasAvailability', False)]),
            'results': results
        }
        
        print(f"✅ API Search completed: {len(results)} results")
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ API Search error: {str(e)}")
        return jsonify({
            'error': f'Search failed: {str(e)}',
            'success': False
        }), 500

def filter_sample_data(criteria):
    """Filter sample data based on search criteria"""
    results = SAMPLE_COURSES.copy()
    
    # Filter by subject
    if criteria['subject']:
        results = [r for r in results if r['course'].startswith(criteria['subject'])]
    
    # Filter by course number
    if criteria['course_number']:
        results = [r for r in results if criteria['course_number'] in r['course']]
    
    # Filter by campus
    if criteria['campus']:
        results = [r for r in results if criteria['campus'].lower() in r['campus'].lower()]
    
    return results

@app.route('/api/subjects', methods=['GET'])
def get_subjects():
    """Get available subjects"""
    subjects = [
        {'code': 'COMM', 'name': 'Communication Studies'},
        {'code': 'MATH', 'name': 'Mathematics'},
        {'code': 'ENGL', 'name': 'English'},
        {'code': 'CSCI', 'name': 'Computer Science'},
        {'code': 'HIST', 'name': 'History'},
        {'code': 'PSYC', 'name': 'Psychology'},
        {'code': 'BIOL', 'name': 'Biology'},
        {'code': 'CHEM', 'name': 'Chemistry'},
        {'code': 'PHYS', 'name': 'Physics'},
        {'code': 'ECON', 'name': 'Economics'}
    ]
    return jsonify(subjects)

@app.route('/api/terms', methods=['GET'])
def get_terms():
    """Get available terms"""
    terms = [
        'Fall 2025',
        'Spring 2026',
        'Summer I 2025',
        'Summer II 2025',
        'Extended Winter 2026'
    ]
    return jsonify(terms)

@app.route('/api/campuses', methods=['GET'])
def get_campuses():
    """Get available campuses"""
    campuses = [
        {'code': 'Rockville', 'name': 'Rockville Campus'},
        {'code': 'Germantown', 'name': 'Germantown Campus'},
        {'code': 'Takoma', 'name': 'Takoma Park/Silver Spring Campus'},
        {'code': 'Distance', 'name': 'Distance Learning'}
    ]
    return jsonify(campuses)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'automation_available': complete_automated_search is not None
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🚀 Starting Montgomery College Course Finder API...")
    print("📁 Frontend files should be in the 'frontend' directory")
    print("🌐 Access the application at: http://localhost:8080")
    print("")
    
    # Check if automation is available
    if complete_automated_search:
        print("✅ Real course automation available")
    else:
        print("⚠️  Using sample data (automation module not found)")
    
    print("")
    print("API Endpoints:")
    print("  GET  /                  - Frontend application")
    print("  POST /api/search        - Search courses")
    print("  GET  /api/subjects      - Get available subjects")
    print("  GET  /api/terms         - Get available terms")  
    print("  GET  /api/campuses      - Get available campuses")
    print("  GET  /api/health        - Health check")
    print("")
    
    # Run the development server with enhanced auto-reload
    app.run(debug=True, host='0.0.0.0', port=8080, use_reloader=True, reloader_type='stat')