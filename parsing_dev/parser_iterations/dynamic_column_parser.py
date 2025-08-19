#!/usr/bin/env python3
"""
Dynamic Column Parser - Determines column mapping from table headers
Instead of hardcoding cell positions, reads header row to identify columns
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from parser_base import BaseParser
from playwright.async_api import Page
from typing import List, Dict

class DynamicColumnParser(BaseParser):
    """Parser that dynamically determines column positions from table headers"""
    
    def __init__(self):
        super().__init__(
            name="dynamic_column_parser_v1",
            description="Dynamically maps columns based on header text instead of hardcoded positions"
        )
    
    async def extract_course_data(self, page: Page, subject: str) -> List[Dict]:
        return await page.evaluate(f"""
            () => {{
                const courses = [];
                
                // Find all tables that contain course data
                const courseTables = Array.from(document.querySelectorAll('table')).filter(table => {{
                    return table.textContent.includes('{subject}') && table.textContent.includes('CRN');
                }});
                
                courseTables.forEach(table => {{
                    const rows = Array.from(table.querySelectorAll('tr'));
                    
                    if (rows.length < 2) return; // Need header + data rows
                    
                    // STEP 1: Analyze header row to create column mapping
                    const headerRow = rows[0];
                    const headerCells = Array.from(headerRow.querySelectorAll('th, td')).map(cell => cell.textContent.trim().toLowerCase());
                    
                    // Create column mapping based on header text
                    const columnMap = {{}};
                    
                    headerCells.forEach((headerText, index) => {{
                        // Course column
                        if (headerText.includes('course') || headerText === 'course') {{
                            columnMap.course = index;
                        }}
                        // CRN column  
                        else if (headerText.includes('crn') || headerText === 'crn') {{
                            columnMap.crn = index;
                        }}
                        // Credits column
                        else if (headerText.includes('credit') || headerText.includes('hour')) {{
                            columnMap.credits = index;
                        }}
                        // Days column
                        else if (headerText.includes('day') || headerText === 'days') {{
                            columnMap.days = index;
                        }}
                        // Time column
                        else if (headerText.includes('time') || headerText === 'time') {{
                            columnMap.time = index;
                        }}
                        // Dates column
                        else if (headerText.includes('date') || headerText.includes('start') || headerText.includes('end')) {{
                            columnMap.dates = index;
                        }}
                        // Seats Available column - KEY: Look for "seat" or "avail"
                        else if (headerText.includes('seat') && headerText.includes('avail')) {{
                            columnMap.seatsAvailable = index;
                        }}
                        else if (headerText.includes('available') || headerText.includes('open')) {{
                            columnMap.seatsAvailable = index;
                        }}
                        // Waitlist column - KEY: Look for "wait"
                        else if (headerText.includes('wait')) {{
                            columnMap.waitlistCount = index;
                        }}
                        // Campus column
                        else if (headerText.includes('campus') || headerText.includes('location')) {{
                            columnMap.campus = index;
                        }}
                        // Room/Location column (different from campus)
                        else if (headerText.includes('room') || headerText.includes('bldg') || headerText === 'location') {{
                            columnMap.location = index;
                        }}
                        // Instructor column
                        else if (headerText.includes('instructor') || headerText.includes('teacher') || headerText.includes('faculty')) {{
                            columnMap.instructor = index;
                        }}
                        // Schedule Type column
                        else if (headerText.includes('type') || headerText.includes('schedule')) {{
                            columnMap.scheduleType = index;
                        }}
                    }});
                    
                    // Debug: Log the column mapping
                    console.log('Header cells:', headerCells);
                    console.log('Column mapping:', columnMap);
                    
                    // STEP 2: Process data rows using the column mapping
                    for (let i = 1; i < rows.length; i++) {{
                        const row = rows[i];
                        const cells = Array.from(row.querySelectorAll('td, th')).map(cell => cell.textContent.trim());
                        
                        // Only process rows that look like course data
                        if (cells.length >= 3 && cells[columnMap.course || 0] && cells[columnMap.course || 0].startsWith('{subject}')) {{
                            
                            // Extract data using column mapping with fallbacks
                            const course = {{
                                course: cells[columnMap.course || 0] || 'TBA',
                                crn: cells[columnMap.crn || 1] || 'TBA',
                                credits: cells[columnMap.credits || 2] || '3.000',
                                days: cells[columnMap.days || 3] || 'TBA',
                                time: cells[columnMap.time || 4] || 'TBA',
                                dates: cells[columnMap.dates || 5] || 'TBA',
                                seatsAvailable: parseInt(cells[columnMap.seatsAvailable || 6]) || 0,
                                waitlistCount: parseInt(cells[columnMap.waitlistCount || 7]) || 0,
                                campus: cells[columnMap.campus || 8] || 'TBA',
                                location: cells[columnMap.location || 9] || 'TBA',
                                instructor: cells[columnMap.instructor || 10] || 'TBA',
                                scheduleType: cells[columnMap.scheduleType || 11] || 'Lecture',
                                
                                // Debug info
                                _debug_column_map: columnMap,
                                _debug_header_cells: headerCells,
                                _debug_cell_count: cells.length,
                                _debug_raw_cells: cells.slice(0, 13)  // First 13 cells for debugging
                            }};
                            
                            course.hasAvailability = course.seatsAvailable > course.waitlistCount;
                            courses.push(course);
                        }}
                    }}
                }});
                
                return courses;
            }}
        """)


class SmartHeaderParser(BaseParser):
    """Enhanced parser with more sophisticated header matching"""
    
    def __init__(self):
        super().__init__(
            name="smart_header_parser_v1",
            description="Advanced header parsing with fuzzy matching and multiple fallback patterns"
        )
    
    async def extract_course_data(self, page: Page, subject: str) -> List[Dict]:
        return await page.evaluate(f"""
            () => {{
                const courses = [];
                
                // Helper function to match header text with multiple patterns
                function matchHeaderPattern(headerText, patterns) {{
                    const text = headerText.toLowerCase().replace(/[^a-z0-9]/g, '');
                    return patterns.some(pattern => {{
                        const cleanPattern = pattern.toLowerCase().replace(/[^a-z0-9]/g, '');
                        return text.includes(cleanPattern) || cleanPattern.includes(text);
                    }});
                }}
                
                const courseTables = Array.from(document.querySelectorAll('table')).filter(table => {{
                    return table.textContent.includes('{subject}');
                }});
                
                courseTables.forEach(table => {{
                    const rows = Array.from(table.querySelectorAll('tr'));
                    if (rows.length < 2) return;
                    
                    // Find header row (might not be first row)
                    let headerRowIndex = -1;
                    let headerCells = [];
                    
                    for (let i = 0; i < Math.min(3, rows.length); i++) {{
                        const cells = Array.from(rows[i].querySelectorAll('th, td')).map(cell => cell.textContent.trim());
                        
                        // Check if this looks like a header row
                        const hasHeaderKeywords = cells.some(cell => 
                            cell.toLowerCase().includes('course') || 
                            cell.toLowerCase().includes('crn') ||
                            cell.toLowerCase().includes('wait') ||
                            cell.toLowerCase().includes('seat')
                        );
                        
                        if (hasHeaderKeywords) {{
                            headerRowIndex = i;
                            headerCells = cells;
                            break;
                        }}
                    }}
                    
                    if (headerRowIndex === -1) {{
                        console.log('No header row found, using positional fallback');
                        headerRowIndex = 0;
                        headerCells = Array.from(rows[0].querySelectorAll('th, td')).map(cell => cell.textContent.trim());
                    }}
                    
                    // Advanced column mapping with multiple pattern matching
                    const columnMap = {{}};
                    
                    headerCells.forEach((headerText, index) => {{
                        // Course patterns
                        if (matchHeaderPattern(headerText, ['course', 'subject', 'class'])) {{
                            columnMap.course = index;
                        }}
                        // CRN patterns
                        else if (matchHeaderPattern(headerText, ['crn', 'reference', 'number'])) {{
                            columnMap.crn = index;
                        }}
                        // Credits patterns
                        else if (matchHeaderPattern(headerText, ['credit', 'hour', 'units'])) {{
                            columnMap.credits = index;
                        }}
                        // Days patterns
                        else if (matchHeaderPattern(headerText, ['days', 'day'])) {{
                            columnMap.days = index;
                        }}
                        // Time patterns
                        else if (matchHeaderPattern(headerText, ['time', 'period', 'hours'])) {{
                            columnMap.time = index;
                        }}
                        // Dates patterns
                        else if (matchHeaderPattern(headerText, ['date', 'dates', 'start', 'end', 'duration'])) {{
                            columnMap.dates = index;
                        }}
                        // Seats Available patterns - CRITICAL FOR ACCURACY
                        else if (matchHeaderPattern(headerText, ['seatsavail', 'available', 'open', 'capacity', 'spots'])) {{
                            columnMap.seatsAvailable = index;
                        }}
                        // Waitlist patterns - CRITICAL FOR ACCURACY  
                        else if (matchHeaderPattern(headerText, ['wait', 'waitlist', 'queue', 'pending'])) {{
                            columnMap.waitlistCount = index;
                        }}
                        // Campus patterns
                        else if (matchHeaderPattern(headerText, ['campus', 'site', 'center'])) {{
                            columnMap.campus = index;
                        }}
                        // Location/Room patterns
                        else if (matchHeaderPattern(headerText, ['location', 'room', 'building', 'bldg', 'facility'])) {{
                            columnMap.location = index;
                        }}
                        // Instructor patterns
                        else if (matchHeaderPattern(headerText, ['instructor', 'teacher', 'faculty', 'prof'])) {{
                            columnMap.instructor = index;
                        }}
                        // Schedule type patterns
                        else if (matchHeaderPattern(headerText, ['type', 'format', 'method', 'mode'])) {{
                            columnMap.scheduleType = index;
                        }}
                    }});
                    
                    // Enhanced debug logging
                    console.log('=== SMART HEADER PARSER DEBUG ===');
                    console.log('Header row index:', headerRowIndex);
                    console.log('Header cells:', headerCells);
                    console.log('Column mapping:', columnMap);
                    console.log('=====================================');
                    
                    // Process data rows starting after header
                    for (let i = headerRowIndex + 1; i < rows.length; i++) {{
                        const row = rows[i];
                        const cells = Array.from(row.querySelectorAll('td, th')).map(cell => cell.textContent.trim());
                        
                        // Check if this is a course data row
                        const courseCell = cells[columnMap.course || 0] || '';
                        if (cells.length >= 3 && courseCell.startsWith('{subject}')) {{
                            
                            const course = {{
                                course: courseCell || 'TBA',
                                crn: cells[columnMap.crn || 1] || 'TBA',
                                credits: cells[columnMap.credits || 2] || '3.000',
                                days: cells[columnMap.days || 3] || 'TBA',
                                time: cells[columnMap.time || 4] || 'TBA', 
                                dates: cells[columnMap.dates || 5] || 'TBA',
                                seatsAvailable: parseInt(cells[columnMap.seatsAvailable || 6]) || 0,
                                waitlistCount: parseInt(cells[columnMap.waitlistCount || 7]) || 0,
                                campus: cells[columnMap.campus || 8] || 'TBA',
                                location: cells[columnMap.location || 9] || 'TBA',
                                instructor: cells[columnMap.instructor || 10] || 'TBA',
                                scheduleType: cells[columnMap.scheduleType || 11] || 'Lecture',
                                
                                // Enhanced debug info
                                _debug_parser: 'smart_header_parser',
                                _debug_header_row_index: headerRowIndex,
                                _debug_column_map: columnMap,
                                _debug_header_cells: headerCells,
                                _debug_data_row_index: i,
                                _debug_raw_cells: cells
                            }};
                            
                            course.hasAvailability = course.seatsAvailable > course.waitlistCount;
                            courses.push(course);
                        }}
                    }}
                }});
                
                return courses;
            }}
        """)