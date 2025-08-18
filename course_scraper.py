#!/usr/bin/env python3
"""
Montgomery College Course Data Collector
This script provides a structure for manually collecting and processing course data.
"""

from dataclasses import dataclass
from typing import List, Optional
import json

@dataclass
class CourseSection:
    crn: str
    course_title: str
    section_number: str
    instructor: Optional[str]
    days_times: str
    location: str
    seats_capacity: int
    seats_remaining: int
    waitlist_capacity: int
    waitlist_count: int
    
    def should_include(self) -> bool:
        """Return True if seats remaining > waitlist count"""
        return self.seats_remaining > self.waitlist_count

class CourseDataProcessor:
    def __init__(self):
        self.sections: List[CourseSection] = []
    
    def add_section(self, section: CourseSection):
        """Add a course section to the collection"""
        self.sections.append(section)
    
    def add_section_from_data(self, crn: str, course_title: str, section_number: str,
                            instructor: Optional[str], days_times: str, location: str,
                            seats_capacity: int, seats_remaining: int,
                            waitlist_capacity: int, waitlist_count: int):
        """Add a section from individual data points"""
        section = CourseSection(
            crn=crn,
            course_title=course_title,
            section_number=section_number,
            instructor=instructor,
            days_times=days_times,
            location=location,
            seats_capacity=seats_capacity,
            seats_remaining=seats_remaining,
            waitlist_capacity=waitlist_capacity,
            waitlist_count=waitlist_count
        )
        self.add_section(section)
    
    def get_available_sections(self) -> List[CourseSection]:
        """Return only sections where seats remaining > waitlist count"""
        return [section for section in self.sections if section.should_include()]
    
    def save_to_json(self, filename: str):
        """Save sections to JSON file"""
        data = []
        for section in self.get_available_sections():
            data.append({
                'crn': section.crn,
                'course_title': section.course_title,
                'section_number': section.section_number,
                'instructor': section.instructor,
                'days_times': section.days_times,
                'location': section.location,
                'seats_capacity': section.seats_capacity,
                'seats_remaining': section.seats_remaining,
                'waitlist_capacity': section.waitlist_capacity,
                'waitlist_count': section.waitlist_count
            })
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def generate_html(self) -> str:
        """Generate HTML table with available sections"""
        sections = self.get_available_sections()
        
        if not sections:
            return "<p>No sections found with seats remaining > waitlist count.</p>"
        
        html = """
        <table border="1" style="border-collapse: collapse; width: 100%;">
            <thead>
                <tr style="background-color: #f0f0f0;">
                    <th>CRN</th>
                    <th>Course Title</th>
                    <th>Section</th>
                    <th>Instructor</th>
                    <th>Days/Times</th>
                    <th>Location</th>
                    <th>Seats Capacity</th>
                    <th>Seats Remaining</th>
                    <th>Waitlist Capacity</th>
                    <th>Waitlist Count</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for section in sections:
            html += f"""
                <tr>
                    <td>{section.crn}</td>
                    <td>{section.course_title}</td>
                    <td>{section.section_number}</td>
                    <td>{section.instructor or 'TBA'}</td>
                    <td>{section.days_times}</td>
                    <td>{section.location}</td>
                    <td>{section.seats_capacity}</td>
                    <td>{section.seats_remaining}</td>
                    <td>{section.waitlist_capacity}</td>
                    <td>{section.waitlist_count}</td>
                </tr>
            """
        
        html += """
            </tbody>
        </table>
        """
        
        return html

# Example usage:
if __name__ == "__main__":
    processor = CourseDataProcessor()
    
    # Example of manually adding course data:
    # processor.add_section_from_data(
    #     crn="12345",
    #     course_title="Introduction to Python",
    #     section_number="001",
    #     instructor="Dr. Smith",
    #     days_times="MW 10:00-11:15",
    #     location="SC 123",
    #     seats_capacity=25,
    #     seats_remaining=5,
    #     waitlist_capacity=10,
    #     waitlist_count=3
    # )
    
    # Generate and save HTML
    html_output = processor.generate_html()
    with open('course_results.html', 'w') as f:
        f.write(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Montgomery College Course Availability</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                table {{ margin-top: 20px; }}
                th {{ padding: 8px; text-align: left; }}
                td {{ padding: 8px; }}
            </style>
        </head>
        <body>
            <h1>Montgomery College Course Availability - Fall 2025</h1>
            <h2>Rockville Campus</h2>
            <p>Showing sections where seats remaining > waitlist count</p>
            {html_output}
        </body>
        </html>
        """)
    
    print("HTML file generated: course_results.html")