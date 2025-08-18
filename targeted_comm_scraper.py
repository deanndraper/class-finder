#!/usr/bin/env python3
"""
Targeted COMM Course Scraper for Montgomery College
Focuses specifically on COMM courses and seat availability
"""

import asyncio
import json
from playwright.async_api import async_playwright

async def scrape_comm_courses():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            print("🎯 Starting Montgomery College COMM course search...")
            
            # Navigate to course search
            await page.goto('https://mcssb.glb.montgomerycollege.edu/eagle/bwckschd.p_disp_dyn_sched')
            await page.wait_for_load_state('networkidle')
            
            # Select Fall 2025 term
            print("📅 Selecting Fall 2025 term...")
            await page.select_option('select', label='Fall 2025')
            await page.click('input[type="submit"]')
            await page.wait_for_load_state('networkidle')
            
            # Now we should be on the course search form
            print("🔍 Looking for COMM courses...")
            
            # Find and select COMM subject
            subject_options = await page.locator('select[name="sel_subj"] option').all_text_contents()
            comm_option = None
            for option in subject_options:
                if 'COMM' in option and 'Communication' in option:
                    comm_option = option
                    break
            
            if comm_option:
                print(f"✅ Found COMM option: {comm_option}")
                await page.select_option('select[name="sel_subj"]', label=comm_option)
                
                # Click Class Search
                await page.click('input[value="Class Search"]')
                await page.wait_for_load_state('networkidle')
                
                print("📊 Extracting course data...")
                
                # Extract course data using JavaScript
                course_data = await page.evaluate("""
                    () => {
                        const courses = [];
                        const tables = document.querySelectorAll('table');
                        
                        tables.forEach(table => {
                            const rows = table.querySelectorAll('tr');
                            
                            rows.forEach(row => {
                                const cells = row.querySelectorAll('td');
                                
                                // Look for rows with course data (typically 10+ cells)
                                if (cells.length >= 8) {
                                    const courseText = cells[0]?.textContent?.trim() || '';
                                    const crnText = cells[1]?.textContent?.trim() || '';
                                    
                                    // Only process COMM courses with valid CRNs
                                    if (courseText.includes('COMM') && /^\\d{5}$/.test(crnText)) {
                                        
                                        const credits = cells[2]?.textContent?.trim() || '';
                                        const daysTime = cells[3]?.textContent?.trim() || '';
                                        const dates = cells[4]?.textContent?.trim() || '';
                                        
                                        // Extract seat information
                                        const seatsText = cells[5]?.textContent?.trim() || '0';
                                        const waitlistText = cells[6]?.textContent?.trim() || '0';
                                        const campusText = cells[7]?.textContent?.trim() || '';
                                        const locationText = cells[8]?.textContent?.trim() || '';
                                        const instructorText = cells[9]?.textContent?.trim() || '';
                                        
                                        const seats = parseInt(seatsText) || 0;
                                        const waitlist = parseInt(waitlistText) || 0;
                                        
                                        courses.push({
                                            course: courseText,
                                            crn: crnText,
                                            credits: credits,
                                            daysTime: daysTime,
                                            dates: dates,
                                            seatsAvailable: seats,
                                            waitlistCount: waitlist,
                                            campus: campusText,
                                            location: locationText,
                                            instructor: instructorText,
                                            hasAvailability: seats > waitlist
                                        });
                                    }
                                }
                            });
                        });
                        
                        return courses;
                    }
                """)
                
                # Filter and analyze results
                available_courses = [c for c in course_data if c['hasAvailability']]
                comm_108_courses = [c for c in course_data if '108' in c['course']]
                comm_108_available = [c for c in comm_108_courses if c['hasAvailability']]
                rockville_courses = [c for c in course_data if 'Rockville' in c['campus']]
                rockville_available = [c for c in rockville_courses if c['hasAvailability']]
                
                print(f"\n📈 RESULTS SUMMARY:")
                print(f"Total COMM sections found: {len(course_data)}")
                print(f"Available sections (seats > waitlist): {len(available_courses)}")
                print(f"COMM 108 sections: {len(comm_108_courses)}")
                print(f"COMM 108 available: {len(comm_108_available)}")
                print(f"Rockville sections: {len(rockville_courses)}")
                print(f"Rockville available: {len(rockville_available)}")
                
                # Show specific COMM 108 results
                print(f"\n🎯 COMM 108 SECTIONS:")
                for course in comm_108_courses:
                    status = "✅ AVAILABLE" if course['hasAvailability'] else f"❌ {course['seatsAvailable']} ≤ {course['waitlistCount']}"
                    print(f"CRN {course['crn']}: {course['campus']} - {course['daysTime']} - {status}")
                
                # Show available courses if any
                if available_courses:
                    print(f"\n🎉 AVAILABLE COURSES (seats > waitlist):")
                    for course in available_courses:
                        print(f"CRN {course['crn']}: {course['course']} - {course['campus']} - {course['seatsAvailable']} seats, {course['waitlistCount']} waitlist")
                else:
                    print(f"\n⚠️  No courses found with seats > waitlist")
                
                # Save data to files
                with open('comm_courses_data.json', 'w') as f:
                    json.dump(course_data, f, indent=2)
                print(f"\n💾 Data saved to comm_courses_data.json")
                
                # Generate HTML report
                generate_html_report(course_data, available_courses, comm_108_courses)
                
                return course_data
            
            else:
                print("❌ Could not find COMM subject option")
                return []
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
        finally:
            await browser.close()

def generate_html_report(all_courses, available_courses, comm_108_courses):
    """Generate HTML report"""
    
    html = f'''<!DOCTYPE html>
<html>
<head>
    <title>Montgomery College COMM Courses - Fall 2025</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f9f9f9; }}
        .container {{ max-width: 1400px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c5aa0; text-align: center; }}
        .summary {{ background-color: #e8f4f8; padding: 15px; border-radius: 4px; margin: 20px 0; }}
        .available {{ background-color: #d4edda; }}
        .unavailable {{ background-color: #f8d7da; }}
        .rockville {{ background-color: #e8f5e8; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 12px; }}
        th {{ background-color: #2c5aa0; color: white; padding: 12px 8px; text-align: left; }}
        td {{ padding: 10px 8px; border-bottom: 1px solid #ddd; }}
        tr:hover {{ background-color: #e8f4f8; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Montgomery College COMM Courses - Fall 2025</h1>
        
        <div class="summary">
            <h3>📊 Summary</h3>
            <ul>
                <li>Total COMM sections: {len(all_courses)}</li>
                <li>Available sections (seats > waitlist): {len(available_courses)}</li>
                <li>COMM 108 sections: {len(comm_108_courses)}</li>
                <li>COMM 108 available: {len([c for c in comm_108_courses if c['hasAvailability']])}</li>
            </ul>
        </div>
'''
    
    if available_courses:
        html += '''
        <h2>🎉 Available Courses (Seats > Waitlist)</h2>
        <table>
            <thead>
                <tr><th>CRN</th><th>Course</th><th>Days/Time</th><th>Campus</th><th>Location</th><th>Instructor</th><th>Seats</th><th>Waitlist</th></tr>
            </thead>
            <tbody>
        '''
        
        for course in available_courses:
            row_class = "available"
            if "Rockville" in course['campus']:
                row_class += " rockville"
            
            html += f'''
                <tr class="{row_class}">
                    <td><strong>{course['crn']}</strong></td>
                    <td>{course['course']}</td>
                    <td>{course['daysTime']}</td>
                    <td>{course['campus']}</td>
                    <td>{course['location']}</td>
                    <td>{course['instructor']}</td>
                    <td><strong>{course['seatsAvailable']}</strong></td>
                    <td>{course['waitlistCount']}</td>
                </tr>
            '''
        html += '</tbody></table>'
    else:
        html += '<div class="summary"><h3>⚠️ No Available Sections</h3><p>All sections have seats ≤ waitlist count</p></div>'
    
    # Show COMM 108 specifically
    html += '''
        <h2>🎯 COMM 108 Sections (Specific Request)</h2>
        <table>
            <thead>
                <tr><th>CRN</th><th>Course</th><th>Days/Time</th><th>Campus</th><th>Location</th><th>Instructor</th><th>Seats</th><th>Waitlist</th><th>Status</th></tr>
            </thead>
            <tbody>
    '''
    
    for course in comm_108_courses:
        row_class = "unavailable"
        if course['hasAvailability']:
            row_class = "available"
        if "Rockville" in course['campus']:
            row_class += " rockville"
        
        status = "✅ Available" if course['hasAvailability'] else f"❌ {course['seatsAvailable']} ≤ {course['waitlistCount']}"
        
        html += f'''
            <tr class="{row_class}">
                <td>{course['crn']}</td>
                <td>{course['course']}</td>
                <td>{course['daysTime']}</td>
                <td>{course['campus']}</td>
                <td>{course['location']}</td>
                <td>{course['instructor']}</td>
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
    
    with open('comm_courses_report.html', 'w') as f:
        f.write(html)
    print("📄 HTML report saved to comm_courses_report.html")

if __name__ == "__main__":
    asyncio.run(scrape_comm_courses())