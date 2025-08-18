#!/usr/bin/env python3
"""
Extract course data directly from the browser using targeted queries
"""

def get_course_data_chunks():
    """
    JavaScript code to extract course data in manageable chunks
    Returns only the essential course information to avoid token limits
    """
    
    js_code = """
    (() => {
        const courses = [];
        
        // Method 1: Look for table-based course data
        const tables = document.querySelectorAll('table');
        
        tables.forEach((table, tableIndex) => {
            const rows = table.querySelectorAll('tr');
            
            rows.forEach((row, rowIndex) => {
                const cells = row.querySelectorAll('td');
                
                if (cells.length >= 8) {
                    const courseText = cells[0]?.textContent?.trim() || '';
                    const crnText = cells[1]?.textContent?.trim() || '';
                    const seatsText = cells[5]?.textContent?.trim() || '';
                    const waitlistText = cells[6]?.textContent?.trim() || '';
                    const campusText = cells[7]?.textContent?.trim() || '';
                    
                    // Only include COMM courses with valid CRNs
                    if (courseText.includes('COMM') && crnText.match(/^\\d{5}$/)) {
                        const seats = parseInt(seatsText) || 0;
                        const waitlist = parseInt(waitlistText) || 0;
                        
                        courses.push({
                            course: courseText,
                            crn: crnText,
                            seats: seats,
                            waitlist: waitlist,
                            campus: campusText,
                            available: seats > waitlist
                        });
                    }
                }
            });
        });
        
        // Method 2: Look for text-based course listings
        const allText = document.body.innerText;
        const lines = allText.split('\\n');
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            
            // Look for COMM course patterns
            if (line.match(/^COMM\\d+\\s+\\d{5}/)) {
                const match = line.match(/^(COMM\\d+)\\s+(\\d{5}).*?(\\d+)\\s+(\\d+)\\s+(Rockville|Germantown|Takoma|Distance)/);
                if (match) {
                    const seats = parseInt(match[3]);
                    const waitlist = parseInt(match[4]);
                    
                    courses.push({
                        course: match[1],
                        crn: match[2],
                        seats: seats,
                        waitlist: waitlist,
                        campus: match[5],
                        available: seats > waitlist,
                        source: 'text'
                    });
                }
            }
        }
        
        // Remove duplicates based on CRN
        const uniqueCourses = courses.reduce((acc, course) => {
            if (!acc.find(c => c.crn === course.crn)) {
                acc.push(course);
            }
            return acc;
        }, []);
        
        return {
            totalFound: uniqueCourses.length,
            available: uniqueCourses.filter(c => c.available),
            all: uniqueCourses
        };
    })();
    """
    
    return js_code

if __name__ == "__main__":
    print("JavaScript code to extract course data:")
    print(get_course_data_chunks())