#!/usr/bin/env python3
"""
Debug our parsing logic to find why CRN 203519 is missing
"""

import asyncio
import re
from playwright.async_api import async_playwright

async def debug_parsing_logic():
    """
    Debug our parsing to understand why we're missing courses
    """
    
    print("🔧 Debugging our course parsing logic...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            # Navigate and search
            await page.goto('https://mcssb.glb.montgomerycollege.edu/eagle/bwckschd.p_disp_dyn_sched')
            await page.wait_for_load_state('networkidle')
            
            await page.select_option('select', label='Fall 2025')
            await page.click('input[type="submit"]')
            await page.wait_for_load_state('networkidle')
            
            # Select COMM
            subject_options = await page.locator('select[name="sel_subj"] option').all_text_contents()
            for option in subject_options:
                if 'COMM' in option and 'Communication' in option:
                    await page.select_option('select[name="sel_subj"]', label=option)
                    break
            
            await page.click('input[value="Class Search"]')
            await page.wait_for_load_state('networkidle')
            
            # Get page text
            page_text = await page.evaluate("() => document.body.innerText")
            lines = page_text.split('\\n')
            
            print(f"📄 Total lines in page: {len(lines)}")
            
            # Debug: Show first 50 lines to understand structure
            print("\\n📋 First 50 lines of page content:")
            for i, line in enumerate(lines[:50]):
                if line.strip():
                    print(f"{i:3d}: {line.strip()}")
            
            # Look for any line containing COMM and numbers
            print("\\n🔍 Lines containing 'COMM' and numbers:")
            comm_lines = []
            for i, line in enumerate(lines):
                if 'COMM' in line and any(char.isdigit() for char in line):
                    comm_lines.append((i, line.strip()))
                    print(f"{i:3d}: {line.strip()}")
            
            print(f"\\nFound {len(comm_lines)} lines with COMM and numbers")
            
            # Look specifically for CRN patterns
            print("\\n🔍 Lines with 5-digit numbers (potential CRNs):")
            crn_lines = []
            for i, line in enumerate(lines):
                if re.search(r'\\b\\d{5}\\b', line):
                    crn_lines.append((i, line.strip()))
                    print(f"{i:3d}: {line.strip()}")
            
            print(f"\\nFound {len(crn_lines)} lines with 5-digit numbers")
            
            # Look for 203519 specifically
            print("\\n🎯 Searching specifically for '203519':")
            found_203519 = False
            for i, line in enumerate(lines):
                if '203519' in line:
                    found_203519 = True
                    print(f"✅ Found at line {i}: {line.strip()}")
                    
                    # Show context
                    print("Context:")
                    for j in range(max(0, i-3), min(len(lines), i+4)):
                        marker = ">>> " if j == i else "    "
                        print(f"{marker}{j:3d}: {lines[j].strip()}")
            
            if not found_203519:
                print("❌ CRN 203519 not found anywhere in the page")
                
                # Check if we need different search parameters
                print("\\n🔍 Maybe we need to search differently...")
                
                # Try searching all subjects to see if 203519 exists elsewhere
                print("\\n🔍 Trying broader search (all subjects)...")
                await page.go_back()
                await page.wait_for_load_state('networkidle')
                
                # Don't select a specific subject - search all
                await page.click('input[value="Class Search"]')
                await page.wait_for_load_state('networkidle')
                
                all_page_text = await page.evaluate("() => document.body.innerText")
                if '203519' in all_page_text:
                    print("✅ Found 203519 in broader search!")
                    all_lines = all_page_text.split('\\n')
                    for i, line in enumerate(all_lines):
                        if '203519' in line:
                            print(f"Found at line {i}: {line.strip()}")
                            # Show context
                            for j in range(max(0, i-3), min(len(all_lines), i+4)):
                                marker = ">>> " if j == i else "    "
                                print(f"{marker}{j:3d}: {all_lines[j].strip()}")
                            break
                else:
                    print("❌ CRN 203519 not found even in broader search")
            
            # Test our regex patterns
            print("\\n🧪 Testing our regex patterns:")
            
            # Test pattern 1: COMM + 5-digit number
            pattern1 = r'^COMM\\d+\\s+\\d{5}'
            matches1 = []
            for line in lines:
                if re.match(pattern1, line.strip()):
                    matches1.append(line.strip())
            
            print(f"Pattern 1 (^COMM\\d+\\s+\\d{{5}}): {len(matches1)} matches")
            for match in matches1[:5]:  # Show first 5
                print(f"  {match}")
            
            # Test pattern 2: Just look for COMM followed by numbers
            pattern2 = r'COMM\\d+'
            matches2 = []
            for line in lines:
                if re.search(pattern2, line):
                    matches2.append(line.strip())
            
            print(f"\\nPattern 2 (COMM\\d+): {len(matches2)} matches")
            for match in matches2[:10]:  # Show first 10
                print(f"  {match}")
            
            # Look for table structure
            print("\\n🔍 Looking for table structure...")
            table_rows = await page.locator('table tr').count()
            print(f"Found {table_rows} table rows")
            
            if table_rows > 0:
                print("\\n📋 Checking table content...")
                for i in range(min(10, table_rows)):
                    try:
                        row_text = await page.locator(f'table tr:nth-child({i+1})').inner_text()
                        if 'COMM' in row_text or any(char.isdigit() for char in row_text):
                            print(f"Row {i+1}: {row_text.strip()}")
                    except:
                        continue
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await asyncio.sleep(5)
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_parsing_logic())