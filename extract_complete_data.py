#!/usr/bin/env python3
"""
Extract complete course data with proper seat availability parsing
"""

import asyncio
import re
from playwright.async_api import async_playwright

async def extract_complete_course_data():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            print("🎯 Extracting complete course data...")
            
            # Navigate to course search
            await page.goto('https://mcssb.glb.montgomerycollege.edu/eagle/bwckschd.p_disp_dyn_sched')
            await page.wait_for_load_state('networkidle')
            
            # Select Fall 2025 term
            await page.select_option('select', label='Fall 2025')
            await page.click('input[type="submit"]')
            await page.wait_for_load_state('networkidle')
            
            # Select COMM subject
            subject_options = await page.locator('select[name="sel_subj"] option').all_text_contents()
            comm_option = None
            for option in subject_options:
                if 'COMM' in option and 'Communication' in option:
                    comm_option = option
                    break
            
            if comm_option:
                await page.select_option('select[name="sel_subj"]', label=comm_option)
                await page.click('input[value="Class Search"]')
                await page.wait_for_load_state('networkidle')
                
                print("📊 Extracting course data using multiple methods...")
                
                # Extract data using comprehensive approach
                course_data = await page.evaluate("""
                    () => {
                        const courses = [];
                        
                        // Method 1: Parse the full text content for structured data
                        const fullText = document.body.innerText;
                        const lines = fullText.split('\\n');
                        
                        let currentCourse = null;
                        let i = 0;
                        
                        while (i < lines.length) {
                            const line = lines[i].trim();
                            
                            // Look for course title lines
                            if (line.includes('COMM ') && line.includes(' - ')) {
                                currentCourse = line;
                                i++;
                                continue;
                            }
                            
                            // Look for main course data lines (tab-separated)
                            if (line.match(/^COMM\\d+\\s+\\d{5}/)) {
                                const parts = line.split(/\\s+/);
                                if (parts.length >= 6) {
                                    const courseCode = parts[0];  // COMM108
                                    const crn = parts[1];         // 20388
                                    const credits = parts[2];     // 3.000
                                    const days = parts[3];        // TR
                                    const timeStart = parts[4];   // 8:00
                                    const timeUnit1 = parts[5];   // AM
                                    
                                    // Continue parsing to get full time and date info
                                    let j = 6;
                                    let timeEnd = '';
                                    let dateRange = '';
                                    let seatsAvail = 0;
                                    let waitlistCount = 0;
                                    let campus = '';
                                    let location = '';
                                    let instructor = '';
                                    
                                    // Look for time pattern continuation
                                    while (j < parts.length) {
                                        if (parts[j] === '-' && j + 2 < parts.length) {
                                            timeEnd = parts[j + 1] + ' ' + parts[j + 2];
                                            j += 3;
                                            break;
                                        }
                                        j++;
                                    }
                                    
                                    // Look for date pattern (MM/DD/YY - MM/DD/YY)
                                    while (j < parts.length) {
                                        if (parts[j].match(/\\d{2}\\/\\d{2}\\/\\d{2}/)) {
                                            dateRange = parts[j];
                                            if (j + 2 < parts.length && parts[j + 1] === '-') {
                                                dateRange += ' - ' + parts[j + 2];
                                                j += 3;
                                            } else {
                                                j++;
                                            }
                                            break;
                                        }
                                        j++;
                                    }
                                    
                                    // Now look in the next few lines for seat availability
                                    for (let k = i + 1; k < Math.min(i + 10, lines.length); k++) {
                                        const nextLine = lines[k].trim();
                                        
                                        // Look for seat/waitlist patterns
                                        // Pattern 1: "2    5    Rockville TA 210"
                                        const seatMatch1 = nextLine.match(/^(\\d+)\\s+(\\d+)\\s+([A-Za-z\\s\\/]+)\\s+([A-Z]{2}\\s+\\d+)/);
                                        if (seatMatch1) {
                                            seatsAvail = parseInt(seatMatch1[1]);
                                            waitlistCount = parseInt(seatMatch1[2]);
                                            campus = seatMatch1[3].trim();
                                            location = seatMatch1[4].trim();
                                            break;
                                        }
                                        
                                        // Pattern 2: "Seats Avail: 2    Waitlist Count: 5"
                                        const seatMatch2 = nextLine.match(/.*?(\\d+).*?(\\d+).*(Rockville|Germantown|Takoma|Distance)/);
                                        if (seatMatch2) {
                                            seatsAvail = parseInt(seatMatch2[1]);
                                            waitlistCount = parseInt(seatMatch2[2]);
                                            campus = seatMatch2[3];
                                            break;
                                        }
                                        
                                        // Pattern 3: Look for campus names alone, then check nearby lines
                                        if (nextLine.includes('Rockville') || nextLine.includes('Germantown') || 
                                            nextLine.includes('Takoma') || nextLine.includes('Distance')) {
                                            campus = nextLine;
                                            
                                            // Check previous lines for numbers
                                            for (let m = Math.max(0, k - 3); m < k; m++) {
                                                const prevLine = lines[m].trim();
                                                const numberMatch = prevLine.match(/^(\\d+)\\s+(\\d+)/);
                                                if (numberMatch) {
                                                    seatsAvail = parseInt(numberMatch[1]);
                                                    waitlistCount = parseInt(numberMatch[2]);
                                                    break;
                                                }
                                            }
                                            break;
                                        }
                                    }
                                    
                                    // Create course entry
                                    const courseEntry = {
                                        courseTitle: currentCourse || '',
                                        course: courseCode,
                                        crn: crn,
                                        credits: credits,
                                        days: days,
                                        timeStart: timeStart + ' ' + timeUnit1,
                                        timeEnd: timeEnd,
                                        dateRange: dateRange,
                                        seatsAvailable: seatsAvail,
                                        waitlistCount: waitlistCount,
                                        campus: campus,
                                        location: location,
                                        instructor: instructor,
                                        hasAvailability: seatsAvail > waitlistCount,
                                        rawLine: line
                                    };
                                    
                                    courses.push(courseEntry);
                                }
                            }
                            
                            i++;
                        }
                        
                        return courses;
                    }
                """)
                
                # Filter and analyze results
                total_courses = len(course_data)
                available_courses = [c for c in course_data if c['hasAvailability']]
                comm_108_courses = [c for c in course_data if '108' in c['course']]
                rockville_courses = [c for c in course_data if 'Rockville' in c['campus']]
                
                print(f"\\n📈 CORRECTED RESULTS:")
                print(f"Total COMM sections found: {total_courses}")
                print(f"Available sections (seats > waitlist): {len(available_courses)}")
                print(f"COMM 108 sections: {len(comm_108_courses)}")
                print(f"Rockville sections: {len(rockville_courses)}")
                
                # Show detailed COMM 108 results
                print(f"\\n🎯 COMM 108 DETAILED RESULTS:")
                for course in comm_108_courses[:10]:  # Show first 10
                    status = "✅ AVAILABLE" if course['hasAvailability'] else f"❌ {course['seatsAvailable']} ≤ {course['waitlistCount']}"
                    print(f"CRN {course['crn']}: {course['campus'][:20]} - {course['days']} {course['timeStart']}-{course['timeEnd']} - {status}")
                    print(f"  Seats: {course['seatsAvailable']}, Waitlist: {course['waitlistCount']}")
                    print(f"  Raw: {course['rawLine'][:80]}...")
                    print("")
                
                # Save corrected data
                import json
                with open('corrected_comm_courses.json', 'w') as f:
                    json.dump(course_data, f, indent=2)
                print(f"💾 Corrected data saved to corrected_comm_courses.json")
                
                return course_data
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(extract_complete_course_data())