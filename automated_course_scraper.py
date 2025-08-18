#!/usr/bin/env python3
"""
Automated Montgomery College Course Scraper
Complete automation from term selection to HTML report generation
"""

import asyncio
import json
import re
from datetime import datetime
from playwright.async_api import async_playwright

class MontgomeryCollegeScraper:
    def __init__(self):
        self.courses = []
        self.config = {
            'term': 'Fall 2025',
            'subjects': ['COMM'],  # Can add multiple: ['COMM', 'MATH', 'ENGL']
            'campus_filter': None,  # 'Rockville', 'Germantown', 'Takoma', 'Distance' or None for all
            'course_number_filter': None,  # '108' or None for all
            'min_seats_over_waitlist': 0  # 0 to show all, 1+ to only show available
        }
    
    async def scrape_courses(self, term=None, subjects=None, campus_filter=None, course_number=None, min_availability=0):
        """Main scraping function with configurable parameters"""
        
        # Update configuration
        if term:
            self.config['term'] = term
        if subjects:
            self.config['subjects'] = subjects if isinstance(subjects, list) else [subjects]
        if campus_filter:
            self.config['campus_filter'] = campus_filter
        if course_number:
            self.config['course_number_filter'] = course_number
        if min_availability >= 0:
            self.config['min_seats_over_waitlist'] = min_availability
        
        print(f"🚀 Starting automated scrape with configuration:")
        print(f"   Term: {self.config['term']}")
        print(f"   Subjects: {self.config['subjects']}")
        print(f"   Campus Filter: {self.config['campus_filter'] or 'All campuses'}")
        print(f"   Course Number Filter: {self.config['course_number_filter'] or 'All courses'}")
        print(f"   Min Seats Over Waitlist: {self.config['min_seats_over_waitlist']}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            
            try:
                # Step 1: Navigate and select term
                await self._select_term(page)
                
                # Step 2: For each subject, get course data
                all_courses = []
                for subject in self.config['subjects']:
                    print(f"\\n📚 Processing subject: {subject}")
                    subject_courses = await self._scrape_subject(page, subject)
                    all_courses.extend(subject_courses)
                
                # Step 3: Filter and process results
                self.courses = self._filter_courses(all_courses)
                
                # Step 4: Generate reports
                await self._generate_reports()
                
                print(f"\\n✅ Scraping completed successfully!")
                print(f"📊 Total courses found: {len(all_courses)}")
                print(f"🎯 Courses meeting criteria: {len(self.courses)}")
                
                return self.courses
                
            except Exception as e:
                print(f"❌ Error during scraping: {e}")
                import traceback
                traceback.print_exc()
                return []
            finally:
                await browser.close()
    
    async def _select_term(self, page):
        """Step 1: Navigate to site and select term"""
        print("🔗 Navigating to Montgomery College course search...")
        await page.goto('https://mcssb.glb.montgomerycollege.edu/eagle/bwckschd.p_disp_dyn_sched')
        await page.wait_for_load_state('networkidle')
        
        print(f"📅 Selecting term: {self.config['term']}")
        await page.select_option('select', label=self.config['term'])
        await page.click('input[type="submit"]')
        await page.wait_for_load_state('networkidle')
        print("✅ Term selected successfully")
    
    async def _scrape_subject(self, page, subject):
        """Step 2: Select subject and scrape course data"""
        print(f"🔍 Searching for {subject} courses...")
        
        # Find and select the subject
        subject_options = await page.locator('select[name="sel_subj"] option').all_text_contents()
        subject_option = None
        
        for option in subject_options:
            if subject in option and ('Communication' in option or 'Math' in option or 'English' in option or subject.upper() in option.upper()):
                subject_option = option
                break
        
        if not subject_option:
            print(f"❌ Subject {subject} not found")
            return []
        
        print(f"✅ Found subject option: {subject_option}")
        await page.select_option('select[name="sel_subj"]', label=subject_option)
        
        # Optional: Set campus filter if specified
        if self.config['campus_filter']:
            await self._set_campus_filter(page)
        
        # Optional: Set course number filter if specified
        if self.config['course_number_filter']:
            await page.fill('input[name="course_number"]', self.config['course_number_filter'])
        
        # Click search
        await page.click('input[value="Class Search"]')
        await page.wait_for_load_state('networkidle')
        
        # Extract course data
        courses = await self._extract_course_data(page, subject)
        print(f"📊 Found {len(courses)} {subject} course sections")
        
        return courses
    
    async def _set_campus_filter(self, page):
        """Optional: Set campus filter if available"""
        try:
            campus_options = await page.locator('select[name="sel_camp"] option').all_text_contents()
            campus_option = None
            
            for option in campus_options:
                if self.config['campus_filter'].lower() in option.lower():
                    campus_option = option
                    break
            
            if campus_option:
                await page.select_option('select[name="sel_camp"]', label=campus_option)
                print(f"🏫 Campus filter set to: {campus_option}")
            else:
                print(f"⚠️  Campus filter '{self.config['campus_filter']}' not found, using all campuses")
        except Exception as e:
            print(f"⚠️  Could not set campus filter: {e}")
    
    async def _extract_course_data(self, page, subject):
        """Step 3: Extract course data from results page"""
        
        course_data = await page.evaluate(f"""
            () => {{
                const courses = [];
                const fullText = document.body.innerText;
                const lines = fullText.split('\\n');
                
                let currentCourseTitle = '';
                let i = 0;
                
                while (i < lines.length) {{
                    const line = lines[i].trim();
                    
                    // Look for course title headers
                    if (line.includes('{subject}') && line.includes(' - ')) {{
                        currentCourseTitle = line;
                        i++;
                        continue;
                    }}
                    
                    // Look for course data lines
                    if (line.match(/^{subject}\\d+\\s+\\d{{5}}/)) {{
                        const parts = line.split(/\\s+/);
                        if (parts.length >= 6) {{
                            const courseCode = parts[0];
                            const crn = parts[1]; 
                            const credits = parts[2];
                            const days = parts[3];
                            
                            // Extract time information
                            let timeStr = '';
                            let j = 4;
                            while (j < parts.length && !parts[j].match(/\\d{{2}}\\/\\d{{2}}\\/\\d{{2}}/)) {{
                                timeStr += parts[j] + ' ';
                                j++;
                            }}
                            timeStr = timeStr.trim();
                            
                            // Extract date range
                            let dateRange = '';
                            if (j < parts.length && parts[j].match(/\\d{{2}}\\/\\d{{2}}\\/\\d{{2}}/)) {{
                                dateRange = parts[j];
                                if (j + 2 < parts.length && parts[j + 1] === '-') {{
                                    dateRange += ' - ' + parts[j + 2];
                                }}
                            }}
                            
                            // Look for seat/waitlist/campus info in subsequent lines
                            let seatsAvail = 0;
                            let waitlistCount = 0;
                            let campus = '';
                            let location = '';
                            let instructor = '';
                            
                            // Check next 10 lines for additional info
                            for (let k = i + 1; k < Math.min(i + 10, lines.length); k++) {{
                                const nextLine = lines[k].trim();
                                
                                // Pattern: seats waitlist campus location instructor
                                const seatPattern = nextLine.match(/^(\\d+)\\s+(\\d+)\\s+([A-Za-z\\s\\/]+?)\\s+([A-Z]{{2}}\\s+\\d+|REMOTE|[A-Z]+\\s+[A-Z\\d]+)\\s*(.*)/);
                                if (seatPattern) {{
                                    seatsAvail = parseInt(seatPattern[1]) || 0;
                                    waitlistCount = parseInt(seatPattern[2]) || 0;
                                    campus = seatPattern[3].trim();
                                    location = seatPattern[4].trim();
                                    instructor = seatPattern[5] ? seatPattern[5].trim() : '';
                                    break;
                                }}
                                
                                // Alternative pattern: look for campus names
                                if (nextLine.includes('Rockville') || nextLine.includes('Germantown') || 
                                    nextLine.includes('Takoma') || nextLine.includes('Distance')) {{
                                    
                                    // Try to extract numbers from nearby lines
                                    const campusLine = nextLine;
                                    const parts = campusLine.split(/\\s+/);
                                    
                                    // Look for two consecutive numbers
                                    for (let m = 0; m < parts.length - 1; m++) {{
                                        if (parts[m].match(/^\\d+$/) && parts[m + 1].match(/^\\d+$/)) {{
                                            seatsAvail = parseInt(parts[m]);
                                            waitlistCount = parseInt(parts[m + 1]);
                                            break;
                                        }}
                                    }}
                                    
                                    // Extract campus and location
                                    if (campusLine.includes('Rockville')) campus = 'Rockville';
                                    else if (campusLine.includes('Germantown')) campus = 'Germantown';
                                    else if (campusLine.includes('Takoma')) campus = 'Takoma Park/Silver Spring';
                                    else if (campusLine.includes('Distance')) campus = 'Distance Learning';
                                    
                                    // Look for location pattern
                                    const locMatch = campusLine.match(/([A-Z]{{2}}\\s+\\d+|REMOTE)/);
                                    if (locMatch) location = locMatch[1];
                                    
                                    // Look for instructor name
                                    const instrMatch = campusLine.match(/([A-Z][a-z]+\\s+[A-Z]?\\.?\\s*[A-Z][a-z]+)/);
                                    if (instrMatch) instructor = instrMatch[1];
                                    
                                    break;
                                }}
                            }}
                            
                            courses.push({{
                                courseTitle: currentCourseTitle,
                                course: courseCode,
                                crn: crn,
                                credits: credits,
                                days: days,
                                time: timeStr,
                                dateRange: dateRange,
                                seatsAvailable: seatsAvail,
                                waitlistCount: waitlistCount,
                                campus: campus,
                                location: location,
                                instructor: instructor,
                                hasAvailability: seatsAvail > waitlistCount,
                                rawLine: line,
                                subject: '{subject}'
                            }});
                        }}
                    }}
                    i++;
                }}
                
                return courses;
            }}
        """)
        
        return course_data
    
    def _filter_courses(self, courses):
        """Step 4: Filter courses based on criteria"""
        filtered = courses
        
        # Filter by campus if specified
        if self.config['campus_filter']:
            filtered = [c for c in filtered if self.config['campus_filter'].lower() in c['campus'].lower()]
        
        # Filter by course number if specified  
        if self.config['course_number_filter']:
            filtered = [c for c in filtered if self.config['course_number_filter'] in c['course']]
        
        # Filter by seat availability
        if self.config['min_seats_over_waitlist'] > 0:
            filtered = [c for c in filtered if c['seatsAvailable'] - c['waitlistCount'] >= self.config['min_seats_over_waitlist']]
        
        return filtered
    
    async def _generate_reports(self):
        """Step 5: Generate HTML and JSON reports"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate HTML report
        html_filename = f"course_report_{timestamp}.html"
        self._generate_html_report(html_filename)
        
        # Generate JSON data
        json_filename = f"course_data_{timestamp}.json"
        with open(json_filename, 'w') as f:
            json.dump(self.courses, f, indent=2)
        
        print(f"📄 Reports generated:")
        print(f"   HTML: {html_filename}")
        print(f"   JSON: {json_filename}")
    
    def _generate_html_report(self, filename):
        """Generate comprehensive HTML report"""
        
        available_courses = [c for c in self.courses if c['hasAvailability']]
        
        # Group by subject and campus for better organization
        subjects = list(set(c['subject'] for c in self.courses))
        campuses = list(set(c['campus'] for c in self.courses if c['campus']))
        
        html = f'''<!DOCTYPE html>
<html>
<head>
    <title>Montgomery College Course Report - {self.config['term']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f9f9f9; }}
        .container {{ max-width: 1600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c5aa0; text-align: center; margin-bottom: 10px; }}
        .config {{ background-color: #e8f4f8; padding: 15px; border-radius: 4px; margin: 20px 0; }}
        .summary {{ background-color: #fff3cd; padding: 15px; border-radius: 4px; margin: 20px 0; }}
        .available {{ background-color: #d4edda; }}
        .unavailable {{ background-color: #f8d7da; }}
        .rockville {{ background-color: #e8f5e8; }}
        .germantown {{ background-color: #e6f3ff; }}
        .takoma {{ background-color: #f0e6ff; }}
        .distance {{ background-color: #fff8e1; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 12px; }}
        th {{ background-color: #2c5aa0; color: white; padding: 12px 6px; text-align: left; font-size: 11px; }}
        td {{ padding: 8px 6px; border-bottom: 1px solid #ddd; vertical-align: top; }}
        tr:hover {{ background-color: #e8f4f8; }}
        .filter-section {{ margin: 20px 0; }}
        .stats {{ display: flex; justify-content: space-around; background-color: #f8f9fa; padding: 15px; border-radius: 4px; margin: 20px 0; }}
        .stat {{ text-align: center; }}
        .stat-number {{ font-size: 24px; font-weight: bold; color: #2c5aa0; }}
        .available-highlight {{ color: #28a745; font-weight: bold; }}
        .waitlist-highlight {{ color: #dc3545; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Montgomery College Course Report</h1>
        
        <div class="config">
            <h3>🔧 Search Configuration</h3>
            <ul>
                <li><strong>Term:</strong> {self.config['term']}</li>
                <li><strong>Subjects:</strong> {', '.join(self.config['subjects'])}</li>
                <li><strong>Campus Filter:</strong> {self.config['campus_filter'] or 'All campuses'}</li>
                <li><strong>Course Number Filter:</strong> {self.config['course_number_filter'] or 'All courses'}</li>
                <li><strong>Minimum Seats Over Waitlist:</strong> {self.config['min_seats_over_waitlist']}</li>
            </ul>
        </div>
        
        <div class="stats">
            <div class="stat">
                <div class="stat-number">{len(self.courses)}</div>
                <div>Total Sections</div>
            </div>
            <div class="stat">
                <div class="stat-number available-highlight">{len(available_courses)}</div>
                <div>Available Sections</div>
            </div>
            <div class="stat">
                <div class="stat-number">{len(subjects)}</div>
                <div>Subjects</div>
            </div>
            <div class="stat">
                <div class="stat-number">{len(campuses)}</div>
                <div>Campuses</div>
            </div>
        </div>
'''
        
        if available_courses:
            html += f'''
        <div class="summary">
            <h3>🎉 Available Courses (Seats > Waitlist)</h3>
            <p>Found <strong>{len(available_courses)}</strong> sections with available seats!</p>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>CRN</th>
                    <th>Course</th>
                    <th>Days</th>
                    <th>Time</th>
                    <th>Campus</th>
                    <th>Location</th>
                    <th>Instructor</th>
                    <th>Seats</th>
                    <th>Waitlist</th>
                    <th>Available</th>
                </tr>
            </thead>
            <tbody>
            '''
            
            for course in available_courses:
                campus_class = ""
                if "Rockville" in course['campus']:
                    campus_class = "rockville"
                elif "Germantown" in course['campus']:
                    campus_class = "germantown"
                elif "Takoma" in course['campus']:
                    campus_class = "takoma"
                elif "Distance" in course['campus']:
                    campus_class = "distance"
                
                available_seats = course['seatsAvailable'] - course['waitlistCount']
                
                html += f'''
                <tr class="available {campus_class}">
                    <td><strong>{course['crn']}</strong></td>
                    <td>{course['course']}</td>
                    <td>{course['days']}</td>
                    <td>{course['time']}</td>
                    <td>{course['campus']}</td>
                    <td>{course['location']}</td>
                    <td>{course['instructor']}</td>
                    <td class="available-highlight">{course['seatsAvailable']}</td>
                    <td>{course['waitlistCount']}</td>
                    <td class="available-highlight">+{available_seats}</td>
                </tr>
                '''
            
            html += '</tbody></table>'
        else:
            html += '''
        <div class="summary">
            <h3>⚠️ No Available Courses</h3>
            <p>No sections found with seats available > waitlist count</p>
        </div>
            '''
        
        # Show all courses for reference
        html += f'''
        <h2>📋 All Course Sections ({len(self.courses)} total)</h2>
        <table>
            <thead>
                <tr>
                    <th>CRN</th>
                    <th>Course</th>
                    <th>Days</th>
                    <th>Time</th>
                    <th>Campus</th>
                    <th>Location</th>
                    <th>Instructor</th>
                    <th>Seats</th>
                    <th>Waitlist</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
        '''
        
        for course in self.courses:
            campus_class = "unavailable"
            if course['hasAvailability']:
                campus_class = "available"
            
            if "Rockville" in course['campus']:
                campus_class += " rockville"
            elif "Germantown" in course['campus']:
                campus_class += " germantown" 
            elif "Takoma" in course['campus']:
                campus_class += " takoma"
            elif "Distance" in course['campus']:
                campus_class += " distance"
            
            if course['hasAvailability']:
                status = f"✅ +{course['seatsAvailable'] - course['waitlistCount']}"
            else:
                status = f"❌ {course['seatsAvailable']} ≤ {course['waitlistCount']}"
            
            html += f'''
            <tr class="{campus_class}">
                <td>{course['crn']}</td>
                <td>{course['course']}</td>
                <td>{course['days']}</td>
                <td>{course['time']}</td>
                <td>{course['campus']}</td>
                <td>{course['location']}</td>
                <td>{course['instructor']}</td>
                <td>{course['seatsAvailable']}</td>
                <td class="waitlist-highlight">{course['waitlistCount']}</td>
                <td>{status}</td>
            </tr>
            '''
        
        html += f'''
            </tbody>
        </table>
        
        <div style="margin-top: 20px; padding: 15px; background-color: #f0f0f0; border-radius: 4px; font-size: 12px;">
            <p><strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            <p><strong>Data Source:</strong> Montgomery College Course Schedule</p>
            <p><strong>Legend:</strong></p>
            <ul>
                <li>🟢 Available sections (seats > waitlist)</li>
                <li>🔴 Waitlisted sections (seats ≤ waitlist)</li>
                <li>Campus colors: Rockville (green), Germantown (blue), Takoma (purple), Distance (yellow)</li>
            </ul>
        </div>
    </div>
</body>
</html>
        '''
        
        with open(filename, 'w') as f:
            f.write(html)

# Example usage functions
async def search_comm_courses():
    """Example: Search for all COMM courses"""
    scraper = MontgomeryCollegeScraper()
    return await scraper.scrape_courses(
        term='Fall 2025',
        subjects=['COMM'],
        campus_filter=None,  # All campuses
        course_number=None,  # All COMM courses
        min_availability=0   # Show all courses
    )

async def search_comm_108_rockville():
    """Example: Search specifically for COMM 108 at Rockville with availability"""
    scraper = MontgomeryCollegeScraper()
    return await scraper.scrape_courses(
        term='Fall 2025',
        subjects=['COMM'],
        campus_filter='Rockville',
        course_number='108',
        min_availability=1  # Only show courses with seats > waitlist
    )

async def search_multiple_subjects():
    """Example: Search multiple subjects across all campuses"""
    scraper = MontgomeryCollegeScraper()
    return await scraper.scrape_courses(
        term='Fall 2025',
        subjects=['COMM', 'MATH', 'ENGL'],
        campus_filter=None,
        course_number=None,
        min_availability=1  # Only available courses
    )

if __name__ == "__main__":
    print("🚀 Montgomery College Automated Course Scraper")
    print("\\nAvailable functions:")
    print("1. search_comm_courses() - All COMM courses")
    print("2. search_comm_108_rockville() - COMM 108 at Rockville only") 
    print("3. search_multiple_subjects() - COMM, MATH, ENGL with availability")
    print("\\nRunning default search for COMM courses...")
    
    asyncio.run(search_comm_courses())