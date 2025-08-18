#!/usr/bin/env python3
"""
Debug HTML structure to correctly extract seat availability data
"""

import asyncio
from playwright.async_api import async_playwright

async def debug_html_structure():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            print("🔍 Debugging HTML structure...")
            
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
                
                print("📊 Analyzing HTML structure...")
                
                # Debug the HTML structure
                debug_data = await page.evaluate("""
                    () => {
                        // Method 1: Look at the actual HTML structure
                        const tables = document.querySelectorAll('table');
                        let structureInfo = {
                            tableCount: tables.length,
                            sampleRowStructures: [],
                            allText: document.body.innerText.split('\\n').slice(0, 100),
                            potentialSeatData: []
                        };
                        
                        // Analyze first few tables
                        for (let i = 0; i < Math.min(3, tables.length); i++) {
                            const table = tables[i];
                            const rows = table.querySelectorAll('tr');
                            
                            for (let j = 0; j < Math.min(5, rows.length); j++) {
                                const row = rows[j];
                                const cells = row.querySelectorAll('td, th');
                                
                                if (cells.length > 0) {
                                    const cellData = [];
                                    for (let k = 0; k < cells.length; k++) {
                                        cellData.push({
                                            index: k,
                                            text: cells[k].textContent.trim(),
                                            html: cells[k].innerHTML.trim()
                                        });
                                    }
                                    
                                    structureInfo.sampleRowStructures.push({
                                        tableIndex: i,
                                        rowIndex: j,
                                        cellCount: cells.length,
                                        cells: cellData
                                    });
                                }
                            }
                        }
                        
                        // Method 2: Look for specific patterns in text
                        const bodyText = document.body.innerText;
                        const lines = bodyText.split('\\n');
                        
                        for (let i = 0; i < lines.length; i++) {
                            const line = lines[i].trim();
                            
                            // Look for lines that might contain seat data
                            if (line.includes('COMM108') || (line.includes('Seats') && line.includes('Waitlist'))) {
                                structureInfo.potentialSeatData.push({
                                    lineIndex: i,
                                    content: line,
                                    nextLine: i + 1 < lines.length ? lines[i + 1].trim() : '',
                                    prevLine: i > 0 ? lines[i - 1].trim() : ''
                                });
                            }
                        }
                        
                        // Method 3: Look for specific column headers
                        const allCells = document.querySelectorAll('td, th');
                        const headerPatterns = ['Seats', 'Waitlist', 'Avail', 'Count', 'Capacity', 'Remaining'];
                        
                        allCells.forEach((cell, index) => {
                            const text = cell.textContent.trim();
                            headerPatterns.forEach(pattern => {
                                if (text.toLowerCase().includes(pattern.toLowerCase())) {
                                    structureInfo.potentialSeatData.push({
                                        type: 'header',
                                        cellIndex: index,
                                        content: text,
                                        html: cell.innerHTML
                                    });
                                }
                            });
                        });
                        
                        return structureInfo;
                    }
                """)
                
                print("\\n📋 HTML Structure Analysis:")
                print(f"Tables found: {debug_data['tableCount']}")
                
                print("\\n🔍 Sample row structures:")
                for structure in debug_data['sampleRowStructures'][:10]:  # Show first 10
                    print(f"Table {structure['tableIndex']}, Row {structure['rowIndex']}: {structure['cellCount']} cells")
                    for cell in structure['cells'][:8]:  # Show first 8 cells
                        print(f"  Cell {cell['index']}: '{cell['text'][:50]}'")
                    print("")
                
                print("\\n🎯 Potential seat data found:")
                for data in debug_data['potentialSeatData'][:10]:  # Show first 10
                    print(f"Type: {data.get('type', 'line')}")
                    print(f"Content: {data['content'][:100]}")
                    if 'nextLine' in data:
                        print(f"Next line: {data['nextLine'][:50]}")
                    print("")
                
                print("\\n📝 Sample text lines:")
                for i, line in enumerate(debug_data['allText'][:20]):  # Show first 20 lines
                    if line.strip():
                        print(f"{i}: {line}")
                
                return debug_data
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_html_structure())