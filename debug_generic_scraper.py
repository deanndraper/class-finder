#!/usr/bin/env python3
"""
Debug the generic scraper to see what's happening with BIOL courses
"""

import asyncio
from playwright.async_api import async_playwright

async def debug_biol_scraper():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Show browser
        page = await browser.new_page()
        
        try:
            print("🔍 Debugging BIOL course extraction...")
            
            # Navigate to course search
            await page.goto('https://mcssb.glb.montgomerycollege.edu/eagle/bwckschd.p_disp_dyn_sched')
            await page.wait_for_load_state('networkidle')
            
            # Select Fall 2025 term
            await page.select_option('select', label='Fall 2025')
            await page.click('input[type="submit"]')
            await page.wait_for_load_state('networkidle')
            
            # Find BIOL subject
            subject_options = await page.locator('select[name="sel_subj"] option').all_text_contents()
            
            biol_option = None
            for option in subject_options:
                if 'BIOL' in option.upper():
                    biol_option = option
                    break
            
            print(f"Found BIOL option: {biol_option}")
            
            if biol_option:
                await page.select_option('select[name="sel_subj"]', label=biol_option)
                await page.click('input[value="Class Search"]')
                await page.wait_for_load_state('networkidle')
                
                # Take screenshot
                await page.screenshot(path='biol_debug.png')
                print("📸 Screenshot saved: biol_debug.png")
                
                # Get page text
                page_text = await page.evaluate("() => document.body.innerText")
                
                # Save full text to file
                with open('biol_page_text.txt', 'w') as f:
                    f.write(page_text)
                print("📄 Page text saved: biol_page_text.txt")
                
                # Look for any BIOL mentions
                lines = page_text.split('\n')
                biol_lines = []
                for i, line in enumerate(lines):
                    if 'BIOL' in line.upper():
                        biol_lines.append((i, line.strip()))
                
                print(f"\n🔍 Found {len(biol_lines)} lines mentioning BIOL:")
                for i, (line_num, line) in enumerate(biol_lines[:20]):  # Show first 20
                    print(f"{line_num:3d}: {line}")
                
                # Look for course patterns
                course_pattern_lines = []
                for i, line in enumerate(lines):
                    if line.strip() and any(char.isdigit() for char in line) and len(line.strip()) > 5:
                        course_pattern_lines.append((i, line.strip()))
                
                print(f"\n🔍 Lines that might contain course data (first 30):")
                for i, (line_num, line) in enumerate(course_pattern_lines[:30]):
                    print(f"{line_num:3d}: {line}")
                
                # Check if there are any error messages
                if 'no classes were found' in page_text.lower():
                    print("\n❌ Page shows 'No classes were found'")
                elif 'no sections found' in page_text.lower():
                    print("\n❌ Page shows 'No sections found'")
                elif len(page_text.strip()) < 100:
                    print(f"\n⚠️ Very short page content ({len(page_text)} chars)")
                else:
                    print(f"\n📊 Page has {len(lines)} lines, {len(page_text)} chars")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print("\n⏸️ Pausing for 10 seconds to inspect browser...")
            await asyncio.sleep(10)
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_biol_scraper())