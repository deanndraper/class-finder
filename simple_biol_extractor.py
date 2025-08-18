#!/usr/bin/env python3
"""
Simple BIOL extractor to debug the issue
"""

import asyncio
from playwright.async_api import async_playwright

async def simple_biol_extractor():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            # Navigate and search for BIOL
            await page.goto('https://mcssb.glb.montgomerycollege.edu/eagle/bwckschd.p_disp_dyn_sched')
            await page.wait_for_load_state('networkidle')
            
            await page.select_option('select', label='Fall 2025')
            await page.click('input[type="submit"]')
            await page.wait_for_load_state('networkidle')
            
            subject_options = await page.locator('select[name="sel_subj"] option').all_text_contents()
            biol_option = None
            for option in subject_options:
                if 'BIOL' in option.upper():
                    biol_option = option
                    break
            
            if biol_option:
                await page.select_option('select[name="sel_subj"]', label=biol_option)
                await page.click('input[value="Class Search"]')
                await page.wait_for_load_state('networkidle')
                
                # Very simple extraction
                courses = await page.evaluate("""
                    () => {
                        const courses = [];
                        const text = document.body.innerText;
                        const lines = text.split('\\n');
                        
                        console.log('Starting extraction...');
                        
                        for (let i = 0; i < lines.length; i++) {
                            const line = lines[i].trim();
                            
                            // Simple pattern: BIOL followed by digits, space, then 5 digits
                            if (line.match(/^BIOL\\d+\\s+\\d{5}/)) {
                                console.log('Found course line:', line);
                                
                                const parts = line.split(/\\s+/);
                                const courseCode = parts[0];
                                const crn = parts[1];
                                
                                // Look for seats in next few lines
                                let seats = 0;
                                let waitlist = 0;
                                let campus = 'TBA';
                                
                                for (let j = i + 1; j < Math.min(i + 8, lines.length); j++) {
                                    const nextLine = lines[j].trim();
                                    
                                    // Single number on line = seats or waitlist
                                    if (/^\\d+$/.test(nextLine)) {
                                        const num = parseInt(nextLine);
                                        if (seats === 0) {
                                            seats = num;
                                        } else if (waitlist === 0) {
                                            waitlist = num;
                                        }
                                    }
                                    
                                    // Campus line
                                    if (nextLine.includes('Rockville') || nextLine.includes('Germantown') || 
                                        nextLine.includes('Takoma') || nextLine.includes('Distance')) {
                                        campus = nextLine.split('\\t')[0] || 'TBA';
                                        break;
                                    }
                                }
                                
                                const course = {
                                    course: courseCode,
                                    crn: crn,
                                    seatsAvailable: seats,
                                    waitlistCount: waitlist,
                                    campus: campus,
                                    hasAvailability: seats > waitlist
                                };
                                
                                courses.push(course);
                                console.log('Added course:', course);
                            }
                        }
                        
                        console.log('Total courses extracted:', courses.length);
                        return courses;
                    }
                """)
                
                print(f"✅ Extracted {len(courses)} BIOL courses")
                
                if courses:
                    available_courses = [c for c in courses if c['hasAvailability']]
                    print(f"🎉 Found {len(available_courses)} available courses:")
                    
                    for course in available_courses[:10]:  # Show first 10
                        print(f"   ✅ CRN {course['crn']}: {course['course']} - {course['campus']} - {course['seatsAvailable']} seats, {course['waitlistCount']} waitlist")
                else:
                    print("❌ No courses extracted")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await asyncio.sleep(5)
            await browser.close()

if __name__ == "__main__":
    asyncio.run(simple_biol_extractor())