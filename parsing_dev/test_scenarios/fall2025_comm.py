#!/usr/bin/env python3
"""
Test Scenario: Fall 2025 COMM Courses
Known issue: Many courses show waitlist=0 when they should have waitlists

Expected Behavior:
- ~100+ COMM courses should be found
- At least 60% should have non-zero waitlists (real COMM classes fill up)
- Campus, instructor, location should be populated
- Should find COMM108, COMM110, COMM111, etc.
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.async_api import async_playwright
import json
from datetime import datetime

class Fall2025CommTest:
    def __init__(self):
        self.results = []
        self.metadata = {}
        
    async def run_test(self, parser_function=None):
        """Run the test scenario with a specific parser"""
        print("🧪 Testing Fall 2025 COMM Courses")
        print("=" * 50)
        
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
                
                # Find COMM subject
                print("📚 Looking for COMM subject...")
                subject_options = await page.locator('select[name="sel_subj"] option').all_text_contents()
                comm_option = None
                for option in subject_options:
                    if option.upper().startswith('COMM-'):
                        comm_option = option
                        break
                
                if not comm_option:
                    raise Exception("COMM subject not found")
                
                print(f"✅ Found: {comm_option}")
                await page.select_option('select[name="sel_subj"]', label=comm_option)
                await page.click('input[value="Class Search"]')
                await page.wait_for_load_state('networkidle')
                
                # Parse the results
                if parser_function:
                    print(f"🔧 Using custom parser: {parser_function.__name__}")
                    self.results = await parser_function(page, 'COMM')
                else:
                    print("🔧 Using default table parser...")
                    self.results = await self.default_table_parser(page, 'COMM')
                
                # Generate metadata
                self.metadata = {
                    'test_name': 'Fall2025_COMM',
                    'timestamp': datetime.now().isoformat(),
                    'total_courses': len(self.results),
                    'parser_used': parser_function.__name__ if parser_function else 'default_table_parser'
                }
                
                print(f"📊 Found {len(self.results)} courses")
                
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
            filename = f"parsing_dev/results/fall2025_comm_{timestamp}.json"
        
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
    test = Fall2025CommTest()
    results, metadata = await test.run_test()
    
    if results:
        filename = test.save_results()
        print(f"\n📋 Test completed:")
        print(f"   Results file: {filename}")
        print(f"   Total courses: {len(results)}")
        
        # Quick analysis
        if len(results) > 0:
            waitlist_counts = [r['waitlistCount'] for r in results]
            non_zero_waitlist = sum(1 for w in waitlist_counts if w > 0)
            tba_campus = sum(1 for r in results if r['campus'] == 'TBA')
            
            print(f"   Non-zero waitlist: {non_zero_waitlist}/{len(results)} ({non_zero_waitlist/len(results)*100:.1f}%)")
            print(f"   TBA campus: {tba_campus}/{len(results)} ({tba_campus/len(results)*100:.1f}%)")
    else:
        print("❌ No results obtained")

if __name__ == "__main__":
    asyncio.run(main())