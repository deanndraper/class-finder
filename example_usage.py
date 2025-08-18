#!/usr/bin/env python3
"""
Example usage of the course data processor
"""

from course_scraper import CourseDataProcessor

def main():
    # Create processor instance
    processor = CourseDataProcessor()
    
    # Example: Add course data manually (you would replace this with your actual data)
    # You can copy data from the Montgomery College website and input it here
    
    # Example course sections:
    processor.add_section_from_data(
        crn="12345",
        course_title="MATH 181 - Calculus I",
        section_number="001",
        instructor="Dr. Johnson",
        days_times="MWF 9:00-9:50",
        location="SC 210",
        seats_capacity=30,
        seats_remaining=8,
        waitlist_capacity=5,
        waitlist_count=2
    )
    
    processor.add_section_from_data(
        crn="12346",
        course_title="MATH 181 - Calculus I",
        section_number="002",
        instructor="Dr. Williams",
        days_times="TR 11:00-12:15",
        location="SC 215",
        seats_capacity=25,
        seats_remaining=1,
        waitlist_capacity=5,
        waitlist_count=3
    )
    
    # This section will be filtered out (seats remaining <= waitlist count)
    processor.add_section_from_data(
        crn="12347",
        course_title="MATH 181 - Calculus I",
        section_number="003",
        instructor="Dr. Davis",
        days_times="MW 2:00-3:15",
        location="SC 220",
        seats_capacity=20,
        seats_remaining=2,
        waitlist_capacity=10,
        waitlist_count=5
    )
    
    # Generate HTML file
    html_output = processor.generate_html()
    with open('course_results.html', 'w') as f:
        f.write(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Montgomery College Course Availability</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 20px; 
                    background-color: #f9f9f9;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                h1 {{ 
                    color: #2c5aa0; 
                    text-align: center;
                    margin-bottom: 10px;
                }}
                h2 {{ 
                    color: #666; 
                    text-align: center;
                    margin-bottom: 20px;
                }}
                .info {{
                    background-color: #e8f4f8;
                    padding: 10px;
                    border-radius: 4px;
                    margin-bottom: 20px;
                    text-align: center;
                }}
                table {{ 
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                    font-size: 14px;
                }}
                th {{ 
                    background-color: #2c5aa0;
                    color: white;
                    padding: 12px 8px;
                    text-align: left;
                    font-weight: bold;
                }}
                td {{ 
                    padding: 10px 8px;
                    border-bottom: 1px solid #ddd;
                }}
                tr:nth-child(even) {{
                    background-color: #f8f9fa;
                }}
                tr:hover {{
                    background-color: #e8f4f8;
                }}
                .available {{
                    color: #28a745;
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Montgomery College Course Availability</h1>
                <h2>Fall 2025 - Rockville Campus</h2>
                <div class="info">
                    <strong>Showing sections where seats remaining > waitlist count</strong>
                </div>
                {html_output}
            </div>
        </body>
        </html>
        """)
    
    # Also save as JSON for data processing
    processor.save_to_json('course_data.json')
    
    print(f"Found {len(processor.get_available_sections())} available sections")
    print("Files generated:")
    print("- course_results.html (HTML table)")
    print("- course_data.json (JSON data)")

if __name__ == "__main__":
    main()