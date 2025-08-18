#!/usr/bin/env python3
"""
Investigate specific CRN 203519 - why it's not showing in reports
"""

import asyncio
from playwright.async_api import async_playwright

async def investigate_crn_203519():
    """
    Search specifically for CRN 203519 to see why it's not appearing
    """
    
    print("🔍 Investigating CRN 203519...")
    print("Expected: COMM course, Fall 2025, 3 seats available")
    print("")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            # Navigate to course search
            print("📅 Step 1: Navigate to Montgomery College...")
            await page.goto('https://mcssb.glb.montgomerycollege.edu/eagle/bwckschd.p_disp_dyn_sched')
            await page.wait_for_load_state('networkidle')
            
            # Select Fall 2025
            print("📅 Step 2: Selecting Fall 2025...")
            await page.select_option('select', label='Fall 2025')
            await page.click('input[type="submit"]')
            await page.wait_for_load_state('networkidle')
            
            # Select COMM subject
            print("📚 Step 3: Selecting COMM subject...")
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
                
                # Take a screenshot for analysis
                await page.screenshot(path='crn_investigation.png')
                print("📸 Screenshot saved: crn_investigation.png")
                
                # Search for CRN 203519 specifically
                print("🔍 Step 4: Searching for CRN 203519...")
                
                # Method 1: Search page content for the CRN
                page_content = await page.content()
                if '203519' in page_content:
                    print("✅ Found CRN 203519 in page content!")
                else:
                    print("❌ CRN 203519 NOT found in page content")
                
                # Method 2: Use page text search
                page_text = await page.evaluate("() => document.body.innerText")
                
                lines = page_text.split('\n')
                crn_found = False
                crn_context = []
                
                for i, line in enumerate(lines):
                    if '203519' in line:
                        crn_found = True
                        print(f"✅ Found CRN 203519 in line {i}: {line.strip()}")
                        
                        # Get context around the CRN
                        start = max(0, i - 3)
                        end = min(len(lines), i + 4)
                        crn_context = lines[start:end]
                        break
                
                if crn_found:
                    print("\\n📋 Context around CRN 203519:")
                    for j, context_line in enumerate(crn_context):
                        marker = ">>> " if '203519' in context_line else "    "
                        print(f"{marker}{context_line.strip()}")
                    
                    # Try to extract seat information from context
                    print("\\n🔍 Analyzing seat information...")
                    for context_line in crn_context:
                        # Look for number patterns that could be seats/waitlist
                        if any(char.isdigit() for char in context_line):
                            numbers = []
                            parts = context_line.split()
                            for part in parts:
                                if part.isdigit():
                                    numbers.append(int(part))
                            if numbers:
                                print(f"    Numbers in line '{context_line.strip()}': {numbers}")
                else:
                    print("❌ CRN 203519 not found in page text")
                
                # Method 3: Check if we need to search more specifically
                print("\\n🔍 Step 5: Checking if CRN search is available...")
                
                # Look for CRN search field
                crn_field_exists = await page.locator('input[name*="crn"], input[name*="CRN"]').count()
                if crn_field_exists > 0:
                    print("✅ Found CRN search field!")
                    # Try searching by CRN directly
                    try:
                        await page.fill('input[name*="crn"], input[name*="CRN"]', '203519')
                        await page.click('input[value="Class Search"]')
                        await page.wait_for_load_state('networkidle')
                        
                        direct_search_text = await page.evaluate("() => document.body.innerText")
                        if '203519' in direct_search_text:
                            print("✅ Found CRN 203519 via direct CRN search!")
                            
                            # Extract the specific course info
                            direct_lines = direct_search_text.split('\\n')
                            for i, line in enumerate(direct_lines):
                                if '203519' in line:
                                    print(f"Direct search result: {line.strip()}")
                                    # Get surrounding context
                                    for j in range(max(0, i-2), min(len(direct_lines), i+3)):
                                        if j != i:
                                            print(f"  Context: {direct_lines[j].strip()}")
                        else:
                            print("❌ CRN 203519 not found even with direct search")
                    except Exception as e:
                        print(f"⚠️  Could not perform direct CRN search: {e}")
                else:
                    print("⚠️  No CRN search field found")
                
                # Method 4: Check our parsing logic against all COMM courses
                print("\\n🔍 Step 6: Analyzing our parsing logic...")
                all_comm_courses = await extract_all_comm_courses(page_text)
                
                print(f"📊 Found {len(all_comm_courses)} COMM courses total")
                
                # Look for CRN 203519 in our parsed results
                target_course = None
                for course in all_comm_courses:
                    if course.get('crn') == '203519':
                        target_course = course
                        break
                
                if target_course:
                    print("✅ Found CRN 203519 in our parsed data!")
                    print("📋 Course details:")
                    for key, value in target_course.items():
                        print(f"    {key}: {value}")
                else:
                    print("❌ CRN 203519 NOT found in our parsed data")
                    print("\\n🔍 This suggests an issue with our parsing logic")
                    
                    # Show some examples of what we DID parse
                    print("\\n📋 Sample of courses we DID find:")
                    for i, course in enumerate(all_comm_courses[:5]):
                        print(f"  {i+1}. CRN {course.get('crn', 'N/A')}: {course.get('course', 'N/A')} - {course.get('seatsAvailable', 'N/A')} seats")
                
            else:
                print("❌ Could not find COMM subject option")
                
        except Exception as e:
            print(f"❌ Error during investigation: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print("\\n⏱️  Keeping browser open for 10 seconds for manual inspection...")
            await asyncio.sleep(10)
            await browser.close()

async def extract_all_comm_courses(page_text):
    """Extract all COMM courses using our current parsing logic"""
    
    courses = []
    lines = page_text.split('\\n')
    
    current_course_title = ''
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Look for course title headers
        if 'COMM' in line and (' - ' in line or 'COMMUNICATION' in line.upper()):
            current_course_title = line
            i += 1
            continue
        
        # Look for course data lines
        if line.match(r'^COMM\\d+\\s+\\d{5}'):
            parts = line.split()
            if len(parts) >= 2:
                course_code = parts[0]
                crn = parts[1]
                
                # Look for seat information in subsequent lines
                seats_avail = 0
                waitlist_count = 0
                campus = ''
                instructor = ''
                
                for k in range(i + 1, min(i + 10, len(lines))):
                    next_line = lines[k].strip()
                    
                    # Look for seat/campus patterns
                    if any(campus_name in next_line for campus_name in ['Rockville', 'Germantown', 'Takoma', 'Distance']):
                        # Try to extract numbers from this line
                        line_parts = next_line.split()
                        numbers = [int(x) for x in line_parts if x.isdigit()]
                        
                        if len(numbers) >= 2:
                            seats_avail = numbers[0]
                            waitlist_count = numbers[1]
                        
                        campus = next_line
                        break
                
                course_entry = {
                    'courseTitle': current_course_title,
                    'course': course_code,
                    'crn': crn,
                    'seatsAvailable': seats_avail,
                    'waitlistCount': waitlist_count,
                    'campus': campus,
                    'instructor': instructor,
                    'hasAvailability': seats_avail > waitlist_count,
                    'rawLine': line
                }
                
                courses.append(course_entry)
        
        i += 1
    
    return courses

if __name__ == "__main__":
    asyncio.run(investigate_crn_203519())