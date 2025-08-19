#!/usr/bin/env python3
"""
Debug script to examine actual HTML structure for waitlist data
This will help us understand why waitlist is always 0
"""

import asyncio
from playwright.async_api import async_playwright

async def debug_html_structure():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            print("🔍 Debugging HTML structure for course data extraction...")
            
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
                if option.upper().startswith('BIOL-'):
                    biol_option = option
                    break
            
            if biol_option:
                print(f"✅ Found BIOL option: {biol_option}")
                await page.select_option('select[name="sel_subj"]', label=biol_option)
                await page.click('input[value="Class Search"]')
                await page.wait_for_load_state('networkidle')
                
                # Debug 1: Check if we're using tables or text parsing
                html_structure = await page.evaluate("""
                    () => {
                        const tables = document.querySelectorAll('table');
                        const coursePattern = /BIOL\\d+\\s+\\d{5}/;
                        
                        const result = {
                            total_tables: tables.length,
                            has_course_tables: false,
                            text_based_courses: 0,
                            sample_table_content: [],
                            sample_text_lines: []
                        };
                        
                        // Check tables for course data
                        tables.forEach((table, idx) => {
                            const tableText = table.textContent;
                            if (coursePattern.test(tableText)) {
                                result.has_course_tables = true;
                                result.sample_table_content.push({
                                    table_index: idx,
                                    rows: table.querySelectorAll('tr').length,
                                    first_few_cells: Array.from(table.querySelectorAll('td')).slice(0, 10).map(td => td.textContent.trim())
                                });
                            }
                        });
                        
                        // Check text-based parsing
                        const bodyText = document.body.innerText;
                        const lines = bodyText.split('\\n');
                        for (let i = 0; i < lines.length; i++) {
                            if (coursePattern.test(lines[i].trim())) {
                                result.text_based_courses++;
                                if (result.sample_text_lines.length < 3) {
                                    result.sample_text_lines.push({
                                        line_number: i,
                                        content: lines[i].trim(),
                                        next_5_lines: lines.slice(i+1, i+6).map((line, idx) => ({
                                            offset: idx + 1,
                                            content: line.trim()
                                        }))
                                    });
                                }
                            }
                        }
                        
                        return result;
                    }
                """)
                
                print(f"\n📊 HTML Structure Analysis:")
                print(f"Total tables: {html_structure['total_tables']}")
                print(f"Has course tables: {html_structure['has_course_tables']}")
                print(f"Text-based courses found: {html_structure['text_based_courses']}")
                
                if html_structure['sample_table_content']:
                    print(f"\n📋 Sample Table Content:")
                    for table_info in html_structure['sample_table_content']:
                        print(f"  Table {table_info['table_index']}: {table_info['rows']} rows")
                        print(f"  First cells: {table_info['first_few_cells']}")
                
                if html_structure['sample_text_lines']:
                    print(f"\n📝 Sample Text-Based Courses:")
                    for sample in html_structure['sample_text_lines']:
                        print(f"  Line {sample['line_number']}: {sample['content']}")
                        print(f"  Next 5 lines:")
                        for next_line in sample['next_5_lines']:
                            print(f"    +{next_line['offset']}: '{next_line['content']}'")
                        print()
                
                # Debug 2: Specific waitlist extraction test
                print(f"\n🔍 Waitlist Extraction Test:")
                waitlist_debug = await page.evaluate("""
                    () => {
                        const bodyText = document.body.innerText;
                        const lines = bodyText.split('\\n');
                        const coursePattern = /BIOL\\d+\\s+\\d{5}/;
                        const results = [];
                        
                        for (let i = 0; i < lines.length; i++) {
                            if (coursePattern.test(lines[i].trim())) {
                                const courseInfo = {
                                    course_line: lines[i].trim(),
                                    line_number: i,
                                    parsing_attempt: {
                                        seats: null,
                                        waitlist: null,
                                        numbers_found: [],
                                        campus_line: null
                                    }
                                };
                                
                                // Look ahead for data
                                for (let j = i + 1; j < Math.min(i + 10, lines.length); j++) {
                                    const line = lines[j].trim();
                                    
                                    // Track all numbers found
                                    if (/^\\d+$/.test(line)) {
                                        courseInfo.parsing_attempt.numbers_found.push({
                                            line_offset: j - i,
                                            value: parseInt(line)
                                        });
                                    }
                                    
                                    // Track campus line
                                    if (line.includes('Rockville') || line.includes('Germantown') || 
                                        line.includes('Takoma') || line.includes('Distance')) {
                                        courseInfo.parsing_attempt.campus_line = {
                                            line_offset: j - i,
                                            content: line
                                        };
                                        break;
                                    }
                                }
                                
                                // Apply current parsing logic
                                if (courseInfo.parsing_attempt.numbers_found.length >= 2) {
                                    courseInfo.parsing_attempt.seats = courseInfo.parsing_attempt.numbers_found[0].value;
                                    courseInfo.parsing_attempt.waitlist = courseInfo.parsing_attempt.numbers_found[1].value;
                                } else if (courseInfo.parsing_attempt.numbers_found.length === 1) {
                                    courseInfo.parsing_attempt.seats = courseInfo.parsing_attempt.numbers_found[0].value;
                                    courseInfo.parsing_attempt.waitlist = 0;
                                }
                                
                                results.push(courseInfo);
                                if (results.length >= 3) break; // Only show first 3 for debugging
                            }
                        }
                        
                        return results;
                    }
                """)
                
                for idx, course in enumerate(waitlist_debug):
                    print(f"  Course {idx + 1}: {course['course_line']}")
                    print(f"    Numbers found: {course['parsing_attempt']['numbers_found']}")
                    print(f"    Parsed seats: {course['parsing_attempt']['seats']}")
                    print(f"    Parsed waitlist: {course['parsing_attempt']['waitlist']}")
                    if course['parsing_attempt']['campus_line']:
                        print(f"    Campus line: {course['parsing_attempt']['campus_line']}")
                    print()
                
                # Debug 3: Check for alternative data structures
                print(f"\n🔍 Alternative Data Structure Check:")
                alt_structure = await page.evaluate("""
                    () => {
                        // Look for common patterns in course websites
                        const patterns = {
                            datatable_class: document.querySelectorAll('.datadisplaytable, .pagebodydiv table').length,
                            form_fields: document.querySelectorAll('input[type="hidden"]').length,
                            javascript_data: document.querySelectorAll('script').length
                        };
                        
                        // Check if data might be in table format instead
                        const courseTables = Array.from(document.querySelectorAll('table')).filter(table => {
                            return table.textContent.includes('BIOL') && table.textContent.includes('CRN');
                        });
                        
                        patterns.course_tables_found = courseTables.length;
                        
                        if (courseTables.length > 0) {
                            const firstTable = courseTables[0];
                            const rows = Array.from(firstTable.querySelectorAll('tr'));
                            patterns.sample_table_structure = {
                                total_rows: rows.length,
                                header_row: rows[0] ? Array.from(rows[0].querySelectorAll('th, td')).map(cell => cell.textContent.trim()) : [],
                                first_data_row: rows[1] ? Array.from(rows[1].querySelectorAll('td')).map(cell => cell.textContent.trim()) : []
                            };
                        }
                        
                        return patterns;
                    }
                """)
                
                for key, value in alt_structure.items():
                    print(f"  {key}: {value}")
                
                print(f"\n✅ Debug complete. Check output above for parsing insights.")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await asyncio.sleep(10)  # Give time to inspect page
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_html_structure())