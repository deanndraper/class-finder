#!/usr/bin/env python3
"""
Simple Automated Montgomery College Course Scraper
Focuses on core automation workflow
"""

import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright

async def automated_course_search(term='Fall 2025', subject='COMM', course_number=None, campus=None):
    """
    Automated course search with configurable parameters
    
    Args:
        term: e.g., 'Fall 2025', 'Spring 2026'
        subject: e.g., 'COMM', 'MATH', 'ENGL'
        course_number: e.g., '108' (optional)
        campus: e.g., 'Rockville', 'Germantown' (optional)
    """
    
    print(f"🚀 Automated Montgomery College Course Search")
    print(f"📅 Term: {term}")
    print(f"📚 Subject: {subject}")
    print(f"🔢 Course Number: {course_number or 'All'}")
    print(f"🏫 Campus: {campus or 'All'}")
    print("")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            # Step 1: Navigate and select term
            print("🔗 Step 1: Navigating to course search...")
            await page.goto('https://mcssb.glb.montgomerycollege.edu/eagle/bwckschd.p_disp_dyn_sched')
            await page.wait_for_load_state('networkidle')
            
            print(f"📅 Step 2: Selecting term '{term}'...")
            await page.select_option('select', label=term)
            await page.click('input[type="submit"]')
            await page.wait_for_load_state('networkidle')
            
            # Step 2: Select subject and filters
            print(f"📚 Step 3: Finding {subject} in subject list...")
            subject_options = await page.locator('select[name="sel_subj"] option').all_text_contents()
            
            subject_option = None
            for option in subject_options:
                if subject in option:
                    subject_option = option
                    break
            
            if not subject_option:
                print(f"❌ Subject '{subject}' not found!")
                return []
            
            print(f"✅ Found: {subject_option}")
            await page.select_option('select[name="sel_subj"]', label=subject_option)
            
            # Optional: Set course number filter
            if course_number:
                print(f"🔢 Step 4: Setting course number filter to '{course_number}'...")
                try:
                    await page.fill('input[name="course_number"]', course_number)
                except:
                    print("⚠️  Course number field not available")
            
            # Optional: Set campus filter  
            if campus:
                print(f"🏫 Step 5: Setting campus filter to '{campus}'...")
                try:
                    campus_options = await page.locator('select[name="sel_camp"] option').all_text_contents()
                    campus_option = None
                    for option in campus_options:
                        if campus.lower() in option.lower():
                            campus_option = option
                            break
                    
                    if campus_option:
                        await page.select_option('select[name="sel_camp"]', label=campus_option)
                        print(f"✅ Campus set to: {campus_option}")
                    else:
                        print(f"⚠️  Campus '{campus}' not found, using all campuses")
                except:
                    print("⚠️  Campus selection not available")
            
            # Step 3: Search for courses
            print("🔍 Step 6: Searching for courses...")
            await page.click('input[value="Class Search"]')
            await page.wait_for_load_state('networkidle')
            
            # Step 4: Take screenshot for verification
            screenshot_name = f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            await page.screenshot(path=screenshot_name)
            print(f"📸 Screenshot saved: {screenshot_name}")
            
            # Step 5: Extract basic course information
            print("📊 Step 7: Extracting course data...")
            
            # Get the page text content for analysis
            page_text = await page.evaluate("() => document.body.innerText")
            
            # Simple parsing to find course sections
            lines = page_text.split('\\n')
            courses = []
            
            for i, line in enumerate(lines):
                line = line.strip()
                # Look for course code + CRN pattern
                if line.startswith(subject) and len(line.split()) >= 2:
                    parts = line.split()
                    if len(parts) >= 2 and parts[1].isdigit() and len(parts[1]) == 5:
                        course_info = {
                            'course': parts[0],
                            'crn': parts[1],
                            'credits': parts[2] if len(parts) > 2 else '',
                            'days': parts[3] if len(parts) > 3 else '',
                            'time': '',
                            'campus': '',
                            'instructor': '',
                            'seatsAvailable': 0,
                            'waitlistCount': 0,
                            'rawLine': line
                        }
                        
                        # Look ahead for additional info
                        for j in range(i + 1, min(i + 5, len(lines))):
                            next_line = lines[j].strip()
                            
                            # Look for campus names
                            if any(campus_name in next_line for campus_name in ['Rockville', 'Germantown', 'Takoma', 'Distance']):
                                course_info['campus'] = next_line
                                
                                # Try to extract numbers from this line
                                numbers = [int(x) for x in next_line.split() if x.isdigit()]
                                if len(numbers) >= 2:
                                    course_info['seatsAvailable'] = numbers[0]
                                    course_info['waitlistCount'] = numbers[1]
                                break
                        
                        courses.append(course_info)
            
            # Step 6: Generate simple HTML report
            html_filename = f"course_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            generate_simple_html_report(courses, html_filename, term, subject, course_number, campus)
            
            # Step 7: Save JSON data
            json_filename = f"course_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(json_filename, 'w') as f:
                json.dump(courses, f, indent=2)
            
            print(f"\\n✅ Automation completed!")
            print(f"📊 Found {len(courses)} course sections")
            print(f"📄 HTML Report: {html_filename}")
            print(f"💾 JSON Data: {json_filename}")
            print(f"📸 Screenshot: {screenshot_name}")
            
            # Keep browser open for inspection
            print("\\n🔍 Browser will stay open for 10 seconds for inspection...")
            await asyncio.sleep(10)
            
            return courses
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            await browser.close()

def generate_simple_html_report(courses, filename, term, subject, course_number, campus):
    """Generate a simple HTML report"""
    
    available_courses = [c for c in courses if c['seatsAvailable'] > c['waitlistCount']]
    
    html = f'''<!DOCTYPE html>
<html>
<head>
    <title>Course Search Results - {subject} {term}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f9f9f9; }}
        .container {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c5aa0; text-align: center; }}
        .search-params {{ background-color: #e8f4f8; padding: 15px; border-radius: 4px; margin: 20px 0; }}
        .summary {{ background-color: #fff3cd; padding: 15px; border-radius: 4px; margin: 20px 0; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th {{ background-color: #2c5aa0; color: white; padding: 12px 8px; text-align: left; }}
        td {{ padding: 10px 8px; border-bottom: 1px solid #ddd; }}
        tr:hover {{ background-color: #e8f4f8; }}
        .available {{ background-color: #d4edda; }}
        .unavailable {{ background-color: #f8d7da; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Automated Course Search Results</h1>
        
        <div class="search-params">
            <h3>🔍 Search Parameters</h3>
            <ul>
                <li><strong>Term:</strong> {term}</li>
                <li><strong>Subject:</strong> {subject}</li>
                <li><strong>Course Number:</strong> {course_number or 'All'}</li>
                <li><strong>Campus:</strong> {campus or 'All'}</li>
                <li><strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</li>
            </ul>
        </div>
        
        <div class="summary">
            <h3>📊 Results Summary</h3>
            <ul>
                <li>Total sections found: <strong>{len(courses)}</strong></li>
                <li>Available sections (seats > waitlist): <strong>{len(available_courses)}</strong></li>
            </ul>
        </div>
'''
    
    if available_courses:
        html += '''
        <h2>🎉 Available Courses (Seats > Waitlist)</h2>
        <table>
            <thead>
                <tr>
                    <th>CRN</th>
                    <th>Course</th>
                    <th>Credits</th>
                    <th>Days</th>
                    <th>Campus</th>
                    <th>Seats</th>
                    <th>Waitlist</th>
                </tr>
            </thead>
            <tbody>
        '''
        
        for course in available_courses:
            html += f'''
                <tr class="available">
                    <td><strong>{course['crn']}</strong></td>
                    <td>{course['course']}</td>
                    <td>{course['credits']}</td>
                    <td>{course['days']}</td>
                    <td>{course['campus']}</td>
                    <td><strong>{course['seatsAvailable']}</strong></td>
                    <td>{course['waitlistCount']}</td>
                </tr>
            '''
        
        html += '</tbody></table>'
    
    # Show all courses
    html += f'''
        <h2>📋 All Course Sections ({len(courses)} total)</h2>
        <table>
            <thead>
                <tr>
                    <th>CRN</th>
                    <th>Course</th>
                    <th>Credits</th>
                    <th>Days</th>
                    <th>Campus</th>
                    <th>Seats</th>
                    <th>Waitlist</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
    '''
    
    for course in courses:
        row_class = "available" if course['seatsAvailable'] > course['waitlistCount'] else "unavailable"
        status = "✅ Available" if course['seatsAvailable'] > course['waitlistCount'] else "❌ Waitlisted"
        
        html += f'''
            <tr class="{row_class}">
                <td>{course['crn']}</td>
                <td>{course['course']}</td>
                <td>{course['credits']}</td>
                <td>{course['days']}</td>
                <td>{course['campus']}</td>
                <td>{course['seatsAvailable']}</td>
                <td>{course['waitlistCount']}</td>
                <td>{status}</td>
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

# Example usage
if __name__ == "__main__":
    print("Choose an option:")
    print("1. COMM courses (all)")
    print("2. COMM 108 at Rockville")
    print("3. Custom search")
    
    # Default: Run COMM course search
    asyncio.run(automated_course_search(
        term='Fall 2025',
        subject='COMM',
        course_number=None,
        campus=None
    ))