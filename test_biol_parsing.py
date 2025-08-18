#!/usr/bin/env python3
"""
Test BIOL parsing with simple logic first
"""

import asyncio
from playwright.async_api import async_playwright

async def test_biol_parsing():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            print("🔍 Testing BIOL parsing...")
            
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
                
                # Simple test - count lines with BIOL101
                course_count = await page.evaluate("""
                    () => {
                        const text = document.body.innerText;
                        const lines = text.split('\\n');
                        let count = 0;
                        
                        console.log('Total lines:', lines.length);
                        
                        for (let i = 0; i < lines.length; i++) {
                            const line = lines[i].trim();
                            if (line.startsWith('BIOL101') && line.includes('\\t')) {
                                count++;
                                console.log(`Found BIOL101 line ${i}: ${line}`);
                            }
                        }
                        
                        return count;
                    }
                """)
                
                print(f"Found {course_count} BIOL101 course lines")
                
                # Test the pattern matching
                test_results = await page.evaluate("""
                    () => {
                        const text = document.body.innerText;
                        const lines = text.split('\\n');
                        const results = [];
                        
                        for (let i = 0; i < lines.length; i++) {
                            const line = lines[i].trim();
                            
                            // Test our regex pattern
                            const pattern = /^BIOL\\d+\\s+\\d{5}/;
                            if (pattern.test(line)) {
                                const parts = line.split(/\\s+/);
                                results.push({
                                    line_number: i,
                                    line: line,
                                    course: parts[0],
                                    crn: parts[1],
                                    credits: parts[2],
                                    days: parts[3]
                                });
                            }
                        }
                        
                        return results;
                    }
                """)
                
                print(f"\\nPattern matching found {len(test_results)} courses:")
                for result in test_results[:5]:  # Show first 5
                    print(f"  Line {result['line_number']}: {result['course']} CRN {result['crn']}")
                
                if len(test_results) > 0:
                    # Test parsing the first course's additional data
                    first_course_line = test_results[0]['line_number']
                    additional_data = await page.evaluate(f"""
                        () => {{
                            const text = document.body.innerText;
                            const lines = text.split('\\n');
                            const startLine = {first_course_line};
                            const result = {{
                                seats: null,
                                waitlist: null,
                                campus: null,
                                next_lines: []
                            }};
                            
                            // Look at next 10 lines
                            for (let i = startLine + 1; i < Math.min(startLine + 10, lines.length); i++) {{
                                const line = lines[i].trim();
                                result.next_lines.push({{line_num: i, content: line}});
                                
                                // Check for single numbers (seats/waitlist)
                                if (/^\\d+$/.test(line)) {{
                                    const num = parseInt(line);
                                    if (result.seats === null) {{
                                        result.seats = num;
                                    }} else if (result.waitlist === null) {{
                                        result.waitlist = num;
                                    }}
                                }}
                                
                                // Check for campus
                                if (line.includes('Rockville') || line.includes('Germantown') || 
                                    line.includes('Takoma') || line.includes('Distance')) {{
                                    result.campus = line;
                                    break;
                                }}
                            }}
                            
                            return result;
                        }}
                    """)
                    
                    print(f"\\nFirst course additional data:")
                    print(f"  Seats: {additional_data['seats']}")
                    print(f"  Waitlist: {additional_data['waitlist']}")
                    print(f"  Campus: {additional_data['campus']}")
                    print("  Next lines:")
                    for line_data in additional_data['next_lines']:
                        print(f"    {line_data['line_num']}: {line_data['content']}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await asyncio.sleep(5)
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_biol_parsing())