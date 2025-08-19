#!/usr/bin/env python3
"""
Base class for parser iterations
Each parser attempt inherits from this to maintain consistency
"""

from abc import ABC, abstractmethod
from typing import List, Dict
from playwright.async_api import Page

class BaseParser(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.version = "1.0"
    
    @abstractmethod
    async def extract_course_data(self, page: Page, subject: str) -> List[Dict]:
        """Extract course data from the page - must be implemented by each parser"""
        pass
    
    def get_info(self) -> Dict:
        """Return parser information"""
        return {
            'name': self.name,
            'description': self.description,
            'version': self.version
        }
    
    async def debug_page_structure(self, page: Page, subject: str) -> Dict:
        """Helper method to analyze page structure for debugging"""
        return await page.evaluate(f"""
            () => {{
                const debug_info = {{
                    total_tables: document.querySelectorAll('table').length,
                    course_tables: 0,
                    sample_table_structure: null,
                    text_course_matches: 0,
                    page_title: document.title
                }};
                
                // Find tables with course data
                const courseTables = Array.from(document.querySelectorAll('table')).filter(table => {{
                    return table.textContent.includes('{subject}');
                }});
                
                debug_info.course_tables = courseTables.length;
                
                if (courseTables.length > 0) {{
                    const firstTable = courseTables[0];
                    const rows = Array.from(firstTable.querySelectorAll('tr'));
                    if (rows.length > 0) {{
                        debug_info.sample_table_structure = {{
                            total_rows: rows.length,
                            header_cells: rows[0] ? Array.from(rows[0].querySelectorAll('th, td')).map(cell => cell.textContent.trim()) : [],
                            first_data_row: rows[1] ? Array.from(rows[1].querySelectorAll('td')).map(cell => cell.textContent.trim()) : []
                        }};
                    }}
                }}
                
                // Count text-based course matches
                const bodyText = document.body.innerText;
                const lines = bodyText.split('\\n');
                const coursePattern = new RegExp(`^{subject}\\\\\\\\d+\\\\\\\\s+\\\\\\\\d{{5}}`);
                for (let line of lines) {{
                    if (coursePattern.test(line.trim())) {{
                        debug_info.text_course_matches++;
                    }}
                }}
                
                return debug_info;
            }}
        """)


class TableParser(BaseParser):
    """Current table-based parser (baseline)"""
    
    def __init__(self):
        super().__init__(
            name="table_parser_v1", 
            description="Extracts course data from HTML tables"
        )
    
    async def extract_course_data(self, page: Page, subject: str) -> List[Dict]:
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
                                hasAvailability: (parseInt(cells[6]) || 0) > (parseInt(cells[7]) || 0),
                                _debug_cell_count: cells.length
                            }};
                            courses.push(course);
                        }}
                    }}
                }});
                
                return courses;
            }}
        """)


class EnhancedTableParser(BaseParser):
    """Improved table parser with better error handling"""
    
    def __init__(self):
        super().__init__(
            name="enhanced_table_parser_v1",
            description="Table parser with enhanced cell validation and error handling"
        )
    
    async def extract_course_data(self, page: Page, subject: str) -> List[Dict]:
        return await page.evaluate(f"""
            () => {{
                const courses = [];
                
                // Find all tables, be more flexible about what constitutes a course table
                const allTables = Array.from(document.querySelectorAll('table'));
                
                allTables.forEach(table => {{
                    const rows = Array.from(table.querySelectorAll('tr'));
                    
                    // Look for course data in any row, not just after headers
                    rows.forEach(row => {{
                        const cells = Array.from(row.querySelectorAll('td, th')).map(cell => cell.textContent.trim());
                        
                        // More flexible course detection
                        if (cells.length >= 6) {{  // Reduced minimum cell count
                            const firstCell = cells[0] || '';
                            
                            // Check if first cell looks like a course code
                            if (firstCell.startsWith('{subject}') && firstCell.match(/^{subject}\\d+/)) {{
                                
                                // Try different cell arrangements based on table structure
                                let courseData = null;
                                
                                if (cells.length >= 12) {{
                                    // Standard 12+ column format
                                    courseData = {{
                                        course: cells[0],
                                        crn: cells[1],
                                        credits: cells[2],
                                        days: cells[3],
                                        time: cells[4],
                                        dates: cells[5],
                                        seatsAvailable: parseInt(cells[6]) || 0,
                                        waitlistCount: parseInt(cells[7]) || 0,
                                        campus: cells[8],
                                        location: cells[9],
                                        instructor: cells[10],
                                        scheduleType: cells[11] || 'Lecture'
                                    }};
                                }} else if (cells.length >= 8) {{
                                    // Compact 8+ column format
                                    courseData = {{
                                        course: cells[0],
                                        crn: cells[1],
                                        credits: cells[2] || '3.000',
                                        days: cells[3] || 'TBA',
                                        time: cells[4] || 'TBA',
                                        dates: cells[5] || 'TBA',
                                        seatsAvailable: parseInt(cells[6]) || 0,
                                        waitlistCount: parseInt(cells[7]) || 0,
                                        campus: cells[8] || 'TBA',
                                        location: cells[9] || 'TBA',
                                        instructor: cells[10] || 'TBA',
                                        scheduleType: 'Lecture'
                                    }};
                                }}
                                
                                if (courseData) {{
                                    courseData.hasAvailability = courseData.seatsAvailable > courseData.waitlistCount;
                                    courseData._debug_cell_count = cells.length;
                                    courseData._debug_raw_cells = cells.slice(0, 12);  // First 12 cells for debugging
                                    courses.push(courseData);
                                }}
                            }}
                        }}
                    }});
                }});
                
                return courses;
            }}
        """)


class AlternativeStructureParser(BaseParser):
    """Parser that looks for alternative HTML structures"""
    
    def __init__(self):
        super().__init__(
            name="alternative_structure_parser_v1",
            description="Looks for course data in non-standard HTML structures"
        )
    
    async def extract_course_data(self, page: Page, subject: str) -> List[Dict]:
        return await page.evaluate(f"""
            () => {{
                const courses = [];
                
                // Method 1: Look for data in div structures
                const courseElements = Array.from(document.querySelectorAll('*')).filter(el => {{
                    return el.textContent && el.textContent.includes('{subject}') && el.textContent.match(/{subject}\\d+\\s+\\d{{5}}/);
                }});
                
                courseElements.forEach(element => {{
                    const text = element.textContent;
                    const lines = text.split('\\n').map(line => line.trim()).filter(line => line.length > 0);
                    
                    // Look for course pattern in text
                    lines.forEach(line => {{
                        const courseMatch = line.match(/^({subject}\\d+)\\s+(\\d{{5}})/);
                        if (courseMatch) {{
                            const course = {{
                                course: courseMatch[1],
                                crn: courseMatch[2],
                                credits: '3.000',
                                days: 'TBA',
                                time: 'TBA',
                                dates: 'TBA',
                                seatsAvailable: 0,
                                waitlistCount: 0,
                                campus: 'TBA',
                                location: 'TBA',
                                instructor: 'TBA',
                                scheduleType: 'Lecture',
                                hasAvailability: false,
                                _debug_source: 'alternative_structure',
                                _debug_raw_text: line
                            }};
                            
                            // Try to find additional data in surrounding text
                            const elementText = element.textContent;
                            
                            // Look for numbers that could be seats/waitlist
                            const numberMatches = elementText.match(/\\b\\d+\\b/g);
                            if (numberMatches && numberMatches.length >= 2) {{
                                // Skip CRN, look for next numbers
                                const possibleSeats = parseInt(numberMatches[1]) || 0;
                                const possibleWaitlist = parseInt(numberMatches[2]) || 0;
                                
                                if (possibleSeats < 100 && possibleWaitlist < 50) {{  // Reasonable ranges
                                    course.seatsAvailable = possibleSeats;
                                    course.waitlistCount = possibleWaitlist;
                                    course.hasAvailability = possibleSeats > possibleWaitlist;
                                }}
                            }}
                            
                            // Look for campus names
                            if (elementText.includes('Rockville')) course.campus = 'Rockville';
                            else if (elementText.includes('Germantown')) course.campus = 'Germantown';
                            else if (elementText.includes('Takoma')) course.campus = 'Takoma Park/Silver Spring';
                            else if (elementText.includes('Distance')) course.campus = 'Distance Learning';
                            
                            courses.push(course);
                        }}
                    }});
                }});
                
                return courses;
            }}
        """)