#!/usr/bin/env python3
"""
Parse COMM course HTML from the current page
This script assumes you have the HTML content from the Montgomery College course page
"""

import re
import json
from bs4 import BeautifulSoup

def parse_course_html(html_content):
    """Parse course data from HTML content"""
    
    soup = BeautifulSoup(html_content, 'html.parser')
    courses = []
    
    # Look for all text content that might contain course data
    page_text = soup.get_text()
    lines = page_text.split('\n')
    
    current_course_title = ""
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Look for course title headers
        if 'COMM' in line and ('-' in line or 'COMMUNICATION' in line.upper()):
            current_course_title = line
            continue
        
        # Look for course data lines (pattern: COMMXXX XXXXX credits days times dates seats waitlist campus location instructor)
        if re.match(r'^COMM\d+\s+\d{5}', line):
            parts = line.split()
            if len(parts) >= 8:
                try:
                    course_code = parts[0]  # COMM108
                    crn = parts[1]          # 20388
                    credits = parts[2]      # 3.000
                    
                    # Find the seats and waitlist numbers
                    seats_avail = 0
                    waitlist_count = 0
                    campus = ""
                    location = ""
                    instructor = ""
                    days_time = ""
                    dates = ""
                    
                    # Look for numeric patterns that could be seats/waitlist
                    for j in range(3, len(parts)):
                        if parts[j].isdigit() and j + 1 < len(parts) and parts[j + 1].isdigit():
                            # Check if the next items after numbers contain campus names
                            if j + 2 < len(parts):
                                potential_campus = ' '.join(parts[j + 2:j + 4])
                                if any(campus_name in potential_campus for campus_name in ['Rockville', 'Germantown', 'Takoma', 'Distance']):
                                    seats_avail = int(parts[j])
                                    waitlist_count = int(parts[j + 1])
                                    campus = potential_campus
                                    break
                    
                    # Try to extract more details by looking at the full line
                    # Pattern matching for common course schedule formats
                    time_pattern = r'(\d{1,2}:\d{2}\s+[AP]M\s*-\s*\d{1,2}:\d{2}\s+[AP]M)'
                    date_pattern = r'(\d{2}/\d{2}/\d{2}\s*-\s*\d{2}/\d{2}/\d{2})'
                    
                    time_match = re.search(time_pattern, line)
                    date_match = re.search(date_pattern, line)
                    
                    if time_match:
                        days_time = time_match.group(1)
                    if date_match:
                        dates = date_match.group(1)
                    
                    # Create course entry
                    course_entry = {
                        'course_title': current_course_title,
                        'course_code': course_code,
                        'crn': crn,
                        'credits': credits,
                        'days_time': days_time,
                        'dates': dates,
                        'seats_available': seats_avail,
                        'waitlist_count': waitlist_count,
                        'campus': campus,
                        'location': location,
                        'instructor': instructor,
                        'meets_criteria': seats_avail > waitlist_count,
                        'raw_line': line  # Keep raw line for debugging
                    }
                    
                    courses.append(course_entry)
                    
                except (ValueError, IndexError) as e:
                    # Skip lines that don't parse correctly
                    continue
    
    return courses

def filter_courses(courses, campus_filter=None, course_number=None):
    """Filter courses by campus and/or course number"""
    filtered = courses
    
    if campus_filter:
        filtered = [c for c in filtered if campus_filter.lower() in c['campus'].lower()]
    
    if course_number:
        filtered = [c for c in filtered if course_number in c['course_code']]
    
    return filtered

def generate_html_report(courses, filename='comm_courses_report.html'):
    """Generate HTML report of courses"""
    
    available_courses = [c for c in courses if c['meets_criteria']]
    
    html = f'''<!DOCTYPE html>
<html>
<head>
    <title>Montgomery College COMM Courses - Fall 2025</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f9f9f9; }}
        .container {{ max-width: 1400px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c5aa0; text-align: center; margin-bottom: 10px; }}
        .info {{ background-color: #e8f4f8; padding: 10px; border-radius: 4px; margin-bottom: 20px; text-align: center; }}
        .summary {{ background-color: #fff3cd; padding: 15px; border-radius: 4px; margin-bottom: 20px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 12px; }}
        th {{ background-color: #2c5aa0; color: white; padding: 12px 8px; text-align: left; font-weight: bold; }}
        td {{ padding: 10px 8px; border-bottom: 1px solid #ddd; vertical-align: top; }}
        tr:nth-child(even) {{ background-color: #f8f9fa; }}
        tr:hover {{ background-color: #e8f4f8; }}
        .available {{ background-color: #d4edda; }}
        .rockville {{ background-color: #e8f5e8; }}
        .distance {{ background-color: #fff3cd; }}
        .unavailable {{ background-color: #f8d7da; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Montgomery College COMM Courses - Fall 2025</h1>
        <div class="info">
            <strong>Analysis Results</strong><br>
            Total sections found: {len(courses)}<br>
            Available sections (seats > waitlist): {len(available_courses)}
        </div>
'''
    
    if available_courses:
        html += '''
        <div class="summary">
            <h3>✅ Available Sections (Seats > Waitlist):</h3>
        </div>
        <table>
            <thead>
                <tr>
                    <th>CRN</th>
                    <th>Course</th>
                    <th>Days/Time</th>
                    <th>Campus</th>
                    <th>Seats Available</th>
                    <th>Waitlist</th>
                    <th>Raw Data</th>
                </tr>
            </thead>
            <tbody>
        '''
        
        for course in available_courses:
            row_class = "available"
            if "Rockville" in course['campus']:
                row_class += " rockville"
            elif "Distance" in course['campus']:
                row_class += " distance"
            
            html += f'''
                <tr class="{row_class}">
                    <td><strong>{course['crn']}</strong></td>
                    <td>{course['course_code']}</td>
                    <td>{course['days_time']}</td>
                    <td>{course['campus']}</td>
                    <td><strong>{course['seats_available']}</strong></td>
                    <td>{course['waitlist_count']}</td>
                    <td style="font-size: 10px; color: #666;">{course['raw_line'][:100]}...</td>
                </tr>
            '''
    else:
        html += '''
        <div class="summary">
            <h3>❌ No Available Sections Found</h3>
            <p>All sections currently have seats available ≤ waitlist count</p>
        </div>
        '''
    
    # Show all courses for reference
    html += '''
        </tbody>
        </table>
        
        <h3>All COMM Course Sections (for reference):</h3>
        <table>
            <thead>
                <tr>
                    <th>CRN</th>
                    <th>Course</th>
                    <th>Campus</th>
                    <th>Seats</th>
                    <th>Waitlist</th>
                    <th>Status</th>
                    <th>Raw Data</th>
                </tr>
            </thead>
            <tbody>
    '''
    
    for course in courses:
        row_class = "unavailable"
        if course['meets_criteria']:
            row_class = "available"
        if "Rockville" in course['campus']:
            row_class += " rockville"
        elif "Distance" in course['campus']:
            row_class += " distance"
        
        status = "✅ Available" if course['meets_criteria'] else f"❌ {course['seats_available']} ≤ {course['waitlist_count']}"
        
        html += f'''
            <tr class="{row_class}">
                <td>{course['crn']}</td>
                <td>{course['course_code']}</td>
                <td>{course['campus']}</td>
                <td>{course['seats_available']}</td>
                <td>{course['waitlist_count']}</td>
                <td>{status}</td>
                <td style="font-size: 10px; color: #666;">{course['raw_line'][:80]}...</td>
            </tr>
        '''
    
    html += '''
            </tbody>
        </table>
    </div>
</body>
</html>
    '''
    
    with open(filename, 'w') as f:
        f.write(html)
    
    return filename

# For testing with sample data
if __name__ == "__main__":
    # This would be where we get HTML content from the browser
    print("This script needs HTML content from the Montgomery College course page")
    print("Use it by calling parse_course_html(html_content) with the page HTML")