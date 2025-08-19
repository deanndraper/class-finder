#!/usr/bin/env python3
"""
Test Scenario: Fall 2025 ENGL Courses - Rockville Campus
English courses are typically high-demand, especially ENGL101/102
We'll filter for Rockville campus specifically
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.async_api import async_playwright
import json
from datetime import datetime

class Fall2025EnglRockvilleTest:
    def __init__(self):
        self.results = []
        self.metadata = {}
        
    async def run_test(self, parser_function=None):
        """Run the test scenario with a specific parser"""
        print("🧪 Testing Fall 2025 ENGL Courses - Rockville Campus")
        print("=" * 55)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)  # Visible for debugging
            page = await browser.new_page()
            
            try:
                # Navigate to course search
                print("🌐 Navigating to Montgomery College...")
                await page.goto('https://mcssb.glb.montgomerycollege.edu/eagle/bwckschd.p_disp_dyn_sched')
                await page.wait_for_load_state('networkidle')
                
                # Select Fall 2025 term
                print("📅 Selecting Fall 2025...")
                await page.select_option('select', label='Fall 2025')
                await page.click('input[type="submit"]')
                await page.wait_for_load_state('networkidle')
                
                # Find ENGL subject
                print("📚 Looking for ENGL subject...")
                subject_options = await page.locator('select[name="sel_subj"] option').all_text_contents()
                engl_option = None
                
                # Look for exact ENGL match first
                for option in subject_options:
                    if option.upper().startswith('ENGL-'):
                        engl_option = option
                        break
                
                # If not found, look for English in the name
                if not engl_option:
                    for option in subject_options:
                        if 'english' in option.lower() and not 'academic' in option.lower():
                            engl_option = option
                            break
                
                # Show available options if still not found
                if not engl_option:
                    print("Available subject options containing 'ENG' or 'ENGLISH':")
                    for opt in subject_options:
                        if 'eng' in opt.lower():
                            print(f"   - {opt}")
                
                if not engl_option:
                    raise Exception("ENGL subject not found")
                
                print(f"✅ Found: {engl_option}")
                await page.select_option('select[name="sel_subj"]', label=engl_option)
                await page.click('input[value="Class Search"]')
                await page.wait_for_load_state('networkidle')
                
                # Parse the results
                if parser_function:
                    print(f"🔧 Using custom parser: {parser_function.__name__}")
                    all_results = await parser_function(page, 'ENGL')
                else:
                    print("🔧 Using default table parser...")
                    all_results = await self.default_table_parser(page, 'ENGL')
                
                # Filter for Rockville campus
                rockville_results = [course for course in all_results 
                                   if 'rockville' in course.get('campus', '').lower()]
                
                self.results = rockville_results
                
                # Generate metadata
                self.metadata = {
                    'test_name': 'Fall2025_ENGL_Rockville',
                    'timestamp': datetime.now().isoformat(),
                    'total_courses_all_campuses': len(all_results),
                    'total_courses_rockville': len(rockville_results),
                    'parser_used': parser_function.__name__ if parser_function else 'default_table_parser',
                    'campus_filter': 'Rockville'
                }
                
                print(f"📊 Found {len(all_results)} total ENGL courses")
                print(f"🏫 Found {len(rockville_results)} Rockville ENGL courses")
                
            except Exception as e:
                print(f"❌ Test failed: {e}")
                self.results = []
            finally:
                await browser.close()
        
        return self.results, self.metadata
    
    async def default_table_parser(self, page, subject):
        """Current table-based parser from main system"""
        return await page.evaluate(f"""
            () => {{
                const courses = [];
                
                const courseTables = Array.from(document.querySelectorAll('table')).filter(table => {{
                    return table.textContent.includes('{subject}') && table.textContent.includes('CRN');
                }});
                
                courseTables.forEach(table => {{
                    const rows = Array.from(table.querySelectorAll('tr'));
                    
                    for (let i = 1; i < rows.length; i++) {{
                        const row = rows[i];
                        const cells = Array.from(row.querySelectorAll('td')).map(cell => cell.textContent.trim());
                        
                        if (cells.length >= 8 && cells[0].startsWith('{subject}')) {{
                            const course = {{
                                course: cells[0] || 'TBA',
                                crn: cells[1] || 'TBA',
                                credits: cells[2] || '3.000',
                                days: cells[3] || 'TBA',
                                time: cells[4] || 'TBA',
                                dates: cells[5] || 'TBA',
                                seatsAvailable: parseInt(cells[6]) || 0,
                                waitlistCount: parseInt(cells[7]) || 0,
                                campus: cells[8] || 'TBA',
                                location: cells[9] || 'TBA',
                                instructor: cells[10] || 'TBA',
                                scheduleType: cells[11] || 'Lecture',
                                hasAvailability: (parseInt(cells[6]) || 0) > (parseInt(cells[7]) || 0)
                            }};
                            courses.push(course);
                        }}
                    }}
                }});
                
                return courses;
            }}
        """)
    
    def save_results(self, filename=None):
        """Save test results to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"parsing_dev/results/fall2025_engl_rockville_{timestamp}.json"
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        data = {
            'metadata': self.metadata,
            'results': self.results
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 Results saved to {filename}")
        return filename

# Test runner
async def main():
    test = Fall2025EnglRockvilleTest()
    results, metadata = await test.run_test()
    
    if results:
        filename = test.save_results()
        print(f"\n📋 Test completed:")
        print(f"   Results file: {filename}")
        print(f"   Total Rockville ENGL courses: {len(results)}")
        print(f"   Total all ENGL courses: {metadata.get('total_courses_all_campuses', 'N/A')}")
        
        # Quick analysis
        if len(results) > 0:
            available_courses = [r for r in results if r['hasAvailability']]
            waitlist_courses = [r for r in results if r['waitlistCount'] > 0]
            
            print(f"\n📊 Quick Analysis:")
            print(f"   Courses with availability: {len(available_courses)}/{len(results)} ({len(available_courses)/len(results)*100:.1f}%)")
            print(f"   Courses with waitlist > 0: {len(waitlist_courses)}/{len(results)} ({len(waitlist_courses)/len(results)*100:.1f}%)")
            
            # Show some examples
            print(f"\n🔍 Sample courses:")
            for i, course in enumerate(results[:5]):
                availability = "✅ Available" if course['hasAvailability'] else "❌ Full/Waitlisted" 
                print(f"     {i+1}. CRN {course['crn']}: {course['course']} - {course['seatsAvailable']} seats, {course['waitlistCount']} waitlist - {availability}")
    else:
        print("❌ No results obtained")

if __name__ == "__main__":
    asyncio.run(main())