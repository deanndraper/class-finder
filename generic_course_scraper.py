#!/usr/bin/env python3
"""
Generic Montgomery College Course Scraper
Real-time scraping with intelligent caching for any subject/term
"""

import asyncio
import json
import os
import time
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
import hashlib

class MontgomeryCollegeScraper:
    def __init__(self, cache_duration_minutes=30):
        self.cache_duration = cache_duration_minutes * 60  # Convert to seconds
        self.cache_dir = "course_cache"
        self.ensure_cache_dir()
    
    def ensure_cache_dir(self):
        """Ensure cache directory exists"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def get_cache_key(self, term, subject, course_filter=None, campus_filter=None):
        """Generate unique cache key for search parameters"""
        cache_data = f"{term}_{subject}_{course_filter or 'all'}_{campus_filter or 'all'}"
        return hashlib.md5(cache_data.encode()).hexdigest()
    
    def get_cache_path(self, cache_key):
        """Get full path to cache file"""
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def is_cache_valid(self, cache_path):
        """Check if cache file exists and is not expired"""
        if not os.path.exists(cache_path):
            return False
        
        file_time = os.path.getmtime(cache_path)
        current_time = time.time()
        return (current_time - file_time) < self.cache_duration
    
    def load_from_cache(self, cache_key):
        """Load course data from cache if valid"""
        cache_path = self.get_cache_path(cache_key)
        
        if self.is_cache_valid(cache_path):
            try:
                with open(cache_path, 'r') as f:
                    data = json.load(f)
                    print(f"📋 Loaded from cache: {len(data.get('courses', []))} courses")
                    return data
            except (json.JSONDecodeError, KeyError):
                print("⚠️ Cache file corrupted, will re-scrape")
                os.remove(cache_path)
        
        return None
    
    def save_to_cache(self, cache_key, courses, metadata):
        """Save course data to cache"""
        cache_path = self.get_cache_path(cache_key)
        
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata,
            'courses': courses
        }
        
        try:
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f, indent=2)
            print(f"💾 Saved to cache: {len(courses)} courses")
        except Exception as e:
            print(f"⚠️ Failed to save cache: {e}")
    
    async def scrape_courses(self, term='Fall 2025', subject='COMM', course_filter=None, campus_filter=None, use_cache=True):
        """
        Generic course scraper for any subject/term
        
        Args:
            term: Academic term (e.g., 'Fall 2025')
            subject: Subject code (e.g., 'COMM', 'BIOL', 'MATH')
            course_filter: Filter by course number (e.g., '108')
            campus_filter: Filter by campus (e.g., 'Rockville')
            use_cache: Whether to use/create cache
        """
        
        print(f"🚀 Generic Montgomery College Course Scraper")
        print(f"📅 Term: {term}")
        print(f"📚 Subject: {subject}")
        print(f"🔢 Course Filter: {course_filter or 'All'}")
        print(f"🏫 Campus Filter: {campus_filter or 'All'}")
        
        # Check cache first
        cache_key = self.get_cache_key(term, subject, course_filter, campus_filter)
        
        if use_cache:
            cached_data = self.load_from_cache(cache_key)
            if cached_data:
                return self.apply_filters(cached_data['courses'], course_filter, campus_filter)
        
        # Perform live scraping
        print("🌐 Performing live web scraping...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)  # Headless for production
            page = await browser.new_page()
            
            try:
                # Navigate to course search
                await page.goto('https://mcssb.glb.montgomerycollege.edu/eagle/bwckschd.p_disp_dyn_sched')
                await page.wait_for_load_state('networkidle')
                
                # Select term
                print(f"📅 Selecting term: {term}")
                try:
                    await page.select_option('select', label=term)
                    await page.click('input[type="submit"]')
                    await page.wait_for_load_state('networkidle')
                except Exception as e:
                    print(f"❌ Failed to select term '{term}': {e}")
                    return []
                
                # Find and select subject
                print(f"📚 Looking for subject: {subject}")
                subject_options = await page.locator('select[name="sel_subj"] option').all_text_contents()
                
                target_option = None
                # Look for exact subject match first (e.g., "COMM-Communication Studies")
                for option in subject_options:
                    if option.upper().startswith(f'{subject.upper()}-'):
                        target_option = option
                        break
                
                # Fallback to contains match if no exact match found
                if not target_option:
                    for option in subject_options:
                        if subject.upper() in option.upper():
                            target_option = option
                            break
                
                if not target_option:
                    print(f"❌ Subject '{subject}' not found. Available subjects:")
                    for opt in subject_options[:10]:  # Show first 10
                        if opt.strip():
                            print(f"   - {opt}")
                    return []
                
                print(f"✅ Found subject option: {target_option}")
                await page.select_option('select[name="sel_subj"]', label=target_option)
                
                # Click Class Search
                await page.click('input[value="Class Search"]')
                await page.wait_for_load_state('networkidle')
                
                # Extract course data
                print("📊 Extracting course data...")
                
                # Debug: Check if we have the right page content
                debug_count = await page.evaluate(f"""
                    () => {{
                        const text = document.body.innerText;
                        const lines = text.split('\\n');
                        let count = 0;
                        for (let line of lines) {{
                            if (line.trim().match(/^{subject}\\d+\\s+\\d{{5}}/)) {{
                                count++;
                            }}
                        }}
                        return count;
                    }}
                """)
                print(f"🔍 Debug: Found {debug_count} {subject} course lines on page")
                
                courses = await self.extract_course_data(page, subject)
                print(f"🔍 Debug: Extracted {len(courses)} course objects")
                
                # Save to cache
                if use_cache and courses:
                    metadata = {
                        'term': term,
                        'subject': subject,
                        'scraped_at': datetime.now().isoformat(),
                        'total_courses': len(courses)
                    }
                    self.save_to_cache(cache_key, courses, metadata)
                
                # Apply filters
                filtered_courses = self.apply_filters(courses, course_filter, campus_filter)
                
                print(f"✅ Extraction complete: {len(courses)} total, {len(filtered_courses)} after filters")
                return filtered_courses
                
            except Exception as e:
                print(f"❌ Scraping error: {e}")
                import traceback
                traceback.print_exc()
                return []
            finally:
                await browser.close()
    
    async def extract_course_data(self, page, subject):
        """Extract course data from the page"""
        
        # Use table-based extraction since Montgomery College uses proper HTML tables
        course_data = await page.evaluate(f"""
            () => {{
                const courses = [];
                
                // Find all tables that contain course data
                const courseTables = Array.from(document.querySelectorAll('table')).filter(table => {{
                    return table.textContent.includes('{subject}') && table.textContent.includes('CRN');
                }});
                
                courseTables.forEach(table => {{
                    const rows = Array.from(table.querySelectorAll('tr'));
                    
                    // Skip header row, process data rows
                    for (let i = 1; i < rows.length; i++) {{
                        const row = rows[i];
                        const cells = Array.from(row.querySelectorAll('td')).map(cell => cell.textContent.trim());
                        
                        // Ensure we have enough cells and this is a course row
                        if (cells.length >= 8 && cells[0].startsWith('{subject}')) {{
                            const courseCode = cells[0] || 'TBA';
                            const crn = cells[1] || 'TBA';
                            const credits = cells[2] || '3.000';
                            const days = cells[3] || 'TBA';
                            const time = cells[4] || 'TBA';
                            const dates = cells[5] || 'TBA';
                            const seatsAvailable = parseInt(cells[6]) || 0;
                            const waitlistCount = parseInt(cells[7]) || 0;
                            const campus = cells[8] || 'TBA';
                            const location = cells[9] || 'TBA';
                            const instructor = cells[10] || 'TBA';
                            const scheduleType = cells[11] || 'Lecture';
                            
                            // Determine availability
                            const hasAvailability = seatsAvailable > waitlistCount;
                            const status = hasAvailability ? 
                                `✅ ${{seatsAvailable}} > ${{waitlistCount}}` : 
                                `❌ ${{seatsAvailable}} ≤ ${{waitlistCount}}`;
                            
                            const course = {{
                                course: courseCode,
                                crn: crn,
                                courseTitle: courseCode,
                                section: '001', // Will extract later if needed
                                credits: credits,
                                days: days,
                                time: time,
                                dates: dates,
                                seatsAvailable: seatsAvailable,
                                waitlistCount: waitlistCount,
                                campus: campus,
                                location: location,
                                instructor: instructor,
                                scheduleType: scheduleType,
                                hasAvailability: hasAvailability,
                                status: status
                            }};
                            
                            courses.push(course);
                        }}
                    }}
                }});
                
                return courses;
            }}
        """)
        
        return course_data
    
    def apply_filters(self, courses, course_filter=None, campus_filter=None):
        """Apply filtering to course list"""
        filtered = courses.copy()
        
        if course_filter:
            filtered = [c for c in filtered if course_filter in c['course']]
            print(f"🔢 Filtered by course '{course_filter}': {len(filtered)} courses")
        
        if campus_filter:
            filtered = [c for c in filtered if campus_filter.lower() in c['campus'].lower()]
            print(f"🏫 Filtered by campus '{campus_filter}': {len(filtered)} courses")
        
        return filtered

# Convenience functions for common use cases
async def search_courses(term='Fall 2025', subject='COMM', course_filter=None, campus_filter=None, use_cache=True):
    """Simple interface for course searching"""
    scraper = MontgomeryCollegeScraper()
    return await scraper.scrape_courses(term, subject, course_filter, campus_filter, use_cache)

async def search_biol_courses(course_filter=None, campus_filter=None):
    """Search BIOL courses specifically"""
    return await search_courses('Fall 2025', 'BIOL', course_filter, campus_filter)

async def search_math_courses(course_filter=None, campus_filter=None):
    """Search MATH courses specifically"""
    return await search_courses('Fall 2025', 'MATH', course_filter, campus_filter)

# Example usage
if __name__ == "__main__":
    import sys
    
    async def main():
        if len(sys.argv) > 1:
            subject = sys.argv[1].upper()
        else:
            subject = 'BIOL'
        
        print(f"Testing generic scraper with {subject} courses...")
        courses = await search_courses(subject=subject)
        
        if courses:
            available = [c for c in courses if c['hasAvailability']]
            print(f"\n🎉 Found {len(available)} available {subject} courses:")
            for course in available[:5]:  # Show first 5
                print(f"   ✅ CRN {course['crn']}: {course['course']} - {course['campus']} - {course['status']}")
        else:
            print(f"\n❌ No {subject} courses found")
    
    asyncio.run(main())