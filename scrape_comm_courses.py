#!/usr/bin/env python3
"""
Montgomery College COMM Course Scraper
Uses Playwright to navigate and BeautifulSoup to parse HTML efficiently
"""

import asyncio
import re
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import json

class MontgomeryCommunicationScraper:
    def __init__(self):
        self.courses = []
    
    async def scrape_comm_courses(self):
        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            
            try:
                # Navigate to course search
                await page.goto('https://mcssb.glb.montgomerycollege.edu/eagle/bwckschd.p_disp_dyn_sched')
                
                # Select Fall 2025 - using the correct selector from our previous work
                await page.select_option('#term_input_id', 'Fall 2025')
                await page.click('input[value="Submit"]')
                
                # Wait for search form to load
                await page.wait_for_load_state('networkidle')
                
                # Select COMM subject - find the option that contains 'COMM'
                comm_option = await page.locator('select[name="sel_subj"] option').filter(has_text="COMM").first.get_attribute('value')
                await page.select_option('select[name="sel_subj"]', comm_option)
                
                # Click search
                await page.click('input[value="Class Search"]')
                
                # Wait for results
                await page.wait_for_load_state('networkidle')
                
                # Get the full HTML content
                html_content = await page.content()
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Extract course data
                self.parse_course_data(soup)
                
                # Filter for available courses (seats > waitlist)
                available_courses = [course for course in self.courses if course['seats_available'] > course['waitlist_count']]
                
                return available_courses
                
            finally:
                await browser.close()
    
    def parse_course_data(self, soup):
        """Parse course data from BeautifulSoup object"""
        
        # Find all course sections
        course_tables = soup.find_all('table')
        
        current_course_title = ""
        
        for table in course_tables:
            # Look for course title headers
            caption = table.find('caption')
            if caption:
                course_title_text = caption.get_text(strip=True)
                if 'COMM' in course_title_text:
                    current_course_title = course_title_text
            
            # Find all rows in the table
            rows = table.find_all('tr')
            
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 8:  # Ensure we have enough columns
                    
                    # Extract data from cells
                    course_code = cells[0].get_text(strip=True)
                    crn = cells[1].get_text(strip=True)
                    
                    # Skip if not a COMM course or not a valid CRN
                    if not course_code.startswith('COMM') or not re.match(r'^\d{5}$', crn):
                        continue
                    
                    credits = cells[2].get_text(strip=True)
                    days_time = cells[3].get_text(strip=True)
                    dates = cells[4].get_text(strip=True)
                    
                    # Parse seats and waitlist
                    seats_text = cells[5].get_text(strip=True)
                    waitlist_text = cells[6].get_text(strip=True)
                    
                    try:
                        seats_available = int(seats_text) if seats_text.isdigit() else 0
                        waitlist_count = int(waitlist_text) if waitlist_text.isdigit() else 0
                    except ValueError:
                        continue
                    
                    # Campus and location
                    campus = cells[7].get_text(strip=True) if len(cells) > 7 else ""
                    location = cells[8].get_text(strip=True) if len(cells) > 8 else ""
                    instructor = cells[9].get_text(strip=True) if len(cells) > 9 else ""
                    
                    # Create course entry
                    course_entry = {
                        'course_title': current_course_title,
                        'course_code': course_code,
                        'crn': crn,
                        'credits': credits,
                        'days_time': days_time,
                        'dates': dates,
                        'seats_available': seats_available,
                        'waitlist_count': waitlist_count,
                        'campus': campus,
                        'location': location,
                        'instructor': instructor,
                        'meets_criteria': seats_available > waitlist_count
                    }
                    
                    self.courses.append(course_entry)
    
    def filter_courses(self, campus_filter=None, course_number=None):
        """Filter courses by campus and/or course number"""
        filtered = self.courses
        
        if campus_filter:
            filtered = [c for c in filtered if campus_filter.lower() in c['campus'].lower()]
        
        if course_number:
            filtered = [c for c in filtered if course_number in c['course_code']]
        
        return filtered
    
    def generate_html_report(self, courses, filename='comm_courses_report.html'):
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
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 12px; }}
        th {{ background-color: #2c5aa0; color: white; padding: 12px 8px; text-align: left; font-weight: bold; }}
        td {{ padding: 10px 8px; border-bottom: 1px solid #ddd; vertical-align: top; }}
        tr:nth-child(even) {{ background-color: #f8f9fa; }}
        tr:hover {{ background-color: #e8f4f8; }}
        .available {{ background-color: #d4edda; }}
        .rockville {{ background-color: #e8f5e8; }}
        .distance {{ background-color: #fff3cd; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Montgomery College COMM Courses - Fall 2025</h1>
        <div class="info">
            <strong>Found {len(available_courses)} available sections (seats > waitlist)</strong><br>
            Total sections found: {len(courses)}
        </div>
        
        <h2>Available Sections (Seats > Waitlist)</h2>
        <table>
            <thead>
                <tr>
                    <th>CRN</th>
                    <th>Course</th>
                    <th>Days/Time</th>
                    <th>Campus</th>
                    <th>Location</th>
                    <th>Instructor</th>
                    <th>Seats Available</th>
                    <th>Waitlist</th>
                </tr>
            </thead>
            <tbody>
        '''
        
        for course in available_courses:
            row_class = ""
            if "Rockville" in course['campus']:
                row_class = "rockville"
            elif "Distance" in course['campus']:
                row_class = "distance"
            
            html += f'''
                <tr class="{row_class} available">
                    <td>{course['crn']}</td>
                    <td>{course['course_code']}</td>
                    <td>{course['days_time']}</td>
                    <td>{course['campus']}</td>
                    <td>{course['location']}</td>
                    <td>{course['instructor']}</td>
                    <td><strong>{course['seats_available']}</strong></td>
                    <td>{course['waitlist_count']}</td>
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

async def main():
    scraper = MontgomeryCommunicationScraper()
    
    print("Scraping Montgomery College COMM courses...")
    try:
        all_courses = await scraper.scrape_comm_courses()
        
        print(f"Found {len(scraper.courses)} total COMM course sections")
        print(f"Found {len(all_courses)} sections with seats > waitlist")
        
        # Filter for COMM 108 specifically
        comm_108_courses = scraper.filter_courses(course_number='108')
        comm_108_available = [c for c in comm_108_courses if c['meets_criteria']]
        
        # Filter for Rockville campus
        rockville_courses = scraper.filter_courses(campus_filter='Rockville')
        rockville_available = [c for c in rockville_courses if c['meets_criteria']]
        
        print(f"\nCOMM 108 sections: {len(comm_108_courses)} total, {len(comm_108_available)} available")
        print(f"Rockville sections: {len(rockville_courses)} total, {len(rockville_available)} available")
        
        # Generate reports
        html_file = scraper.generate_html_report(scraper.courses)
        print(f"\nGenerated HTML report: {html_file}")
        
        # Save raw data as JSON
        with open('comm_courses_data.json', 'w') as f:
            json.dump(scraper.courses, f, indent=2)
        
        # Print available courses
        if all_courses:
            print("\nAvailable courses (seats > waitlist):")
            for course in all_courses:
                print(f"  CRN {course['crn']}: {course['course_code']} - {course['campus']} - {course['seats_available']} seats, {course['waitlist_count']} waitlist")
        else:
            print("\nNo courses found with seats > waitlist")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())