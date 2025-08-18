#!/usr/bin/env python3
"""
Corrected COMM course data based on actual Montgomery College Fall 2025 data
"""

# Real COMM course data from Montgomery College Fall 2025
REAL_COMM_COURSES = [
    # COMM 108 - Foundations of Human Communication (all have waitlists)
    {
        "course": "COMM108",
        "crn": "20388",
        "courseTitle": "Foundations of Human Communication",
        "section": "001",
        "credits": "3.000",
        "days": "TR",
        "time": "8:00 AM - 9:15 AM",
        "dates": "09/02/25 - 12/21/25",
        "seatsAvailable": 1,
        "waitlistCount": 5,
        "campus": "Rockville",
        "location": "TA 210",
        "instructor": "Teodora Salow",
        "hasAvailability": False,
        "status": "❌ 1 ≤ 5"
    },
    {
        "course": "COMM108",
        "crn": "22373",
        "courseTitle": "Foundations of Human Communication",
        "section": "002",
        "credits": "3.000",
        "days": "TR",
        "time": "8:00 AM - 9:15 AM",
        "dates": "09/02/25 - 12/21/25",
        "seatsAvailable": 0,
        "waitlistCount": 2,
        "campus": "Germantown",
        "location": "HT 403",
        "instructor": "Luis Botello",
        "hasAvailability": False,
        "status": "❌ 0 ≤ 2"
    },
    
    # COMM 220 - Small Group Communication (AVAILABLE!)
    {
        "course": "COMM220",
        "crn": "21458",
        "courseTitle": "Small Group Communication",
        "section": "001",
        "credits": "3.000",
        "days": "TR",
        "time": "2:00 PM - 3:15 PM",
        "dates": "09/02/25 - 12/21/25",
        "seatsAvailable": 1,
        "waitlistCount": 0,
        "campus": "Distance Learning",
        "location": "REMOTE",
        "instructor": "Andree Betancourt",
        "hasAvailability": True,
        "status": "✅ 1 > 0"
    },
    
    # COMM 225 - Intercultural Communication (AVAILABLE!)
    {
        "course": "COMM225",
        "crn": "23630",
        "courseTitle": "Intercultural Communication",
        "section": "001",
        "credits": "3.000",
        "days": "MW",
        "time": "9:30 AM - 10:45 AM",
        "dates": "09/03/25 - 12/21/25",
        "seatsAvailable": 12,
        "waitlistCount": 0,
        "campus": "Takoma Park/Silver Spring",
        "location": "CU 201",
        "instructor": "Aayushi Hingle",
        "hasAvailability": True,
        "status": "✅ 12 > 0"
    },
    
    # COMM 230 - Introduction to Public Relations (AVAILABLE!)
    {
        "course": "COMM230",
        "crn": "23398",
        "courseTitle": "Introduction to Public Relations",
        "section": "001",
        "credits": "3.000",
        "days": "W",
        "time": "3:30 PM - 6:15 PM",
        "dates": "09/03/25 - 12/21/25",
        "seatsAvailable": 3,
        "waitlistCount": 0,
        "campus": "Distance Learning",
        "location": "REMOTE",
        "instructor": "Aprill O. Turner",
        "hasAvailability": True,
        "status": "✅ 3 > 0"
    },
    
    # COMM 230 - Introduction to Public Relations (AVAILABLE at Rockville!)
    {
        "course": "COMM230",
        "crn": "21924",
        "courseTitle": "Introduction to Public Relations",
        "section": "002",
        "credits": "3.000",
        "days": "W",
        "time": "6:30 PM - 9:10 PM",
        "dates": "09/03/25 - 12/21/25",
        "seatsAvailable": 9,
        "waitlistCount": 0,
        "campus": "Rockville",
        "location": "TA 211",
        "instructor": "Aprill O. Turner",
        "hasAvailability": True,
        "status": "✅ 9 > 0"
    },
    
    # COMM 250 - Introduction to Communication Inquiry & Theory (AVAILABLE!)
    {
        "course": "COMM250",
        "crn": "20402",
        "courseTitle": "Introduction to Communication Inquiry & Theory",
        "section": "001",
        "credits": "3.000",
        "days": "M",
        "time": "10:00 AM - 11:15 AM",
        "dates": "09/08/25 - 12/21/25",
        "seatsAvailable": 9,
        "waitlistCount": 0,
        "campus": "Rockville",
        "location": "TA 203",
        "instructor": "Nader H. Chaaban",
        "hasAvailability": True,
        "status": "✅ 9 > 0"
    },
    
    # COMM 250 - Distance Learning (AVAILABLE!)
    {
        "course": "COMM250",
        "crn": "21875",
        "courseTitle": "Introduction to Communication Inquiry & Theory",
        "section": "002",
        "credits": "3.000",
        "days": "TBA",
        "time": "TBA",
        "dates": "09/02/25 - 12/21/25",
        "seatsAvailable": 4,
        "waitlistCount": 0,
        "campus": "Distance Learning",
        "location": "DL WEB",
        "instructor": "Nader H. Chaaban",
        "hasAvailability": True,
        "status": "✅ 4 > 0"
    },
    
    # COMM 250 - Germantown (AVAILABLE!)
    {
        "course": "COMM250",
        "crn": "21355",
        "courseTitle": "Introduction to Communication Inquiry & Theory",
        "section": "003",
        "credits": "3.000",
        "days": "MW",
        "time": "1:00 PM - 2:15 PM",
        "dates": "09/03/25 - 12/21/25",
        "seatsAvailable": 16,
        "waitlistCount": 0,
        "campus": "Germantown",
        "location": "HT 403",
        "instructor": "Aaron D. Johnson",
        "hasAvailability": True,
        "status": "✅ 16 > 0"
    },
    
    # COMM 251 - Introduction to Journalism (AVAILABLE!)
    {
        "course": "COMM251",
        "crn": "21451",
        "courseTitle": "Introduction to Journalism",
        "section": "001",
        "credits": "3.000",
        "days": "TBA",
        "time": "TBA",
        "dates": "09/02/25 - 12/21/25",
        "seatsAvailable": 4,
        "waitlistCount": 0,
        "campus": "Distance Learning",
        "location": "DL WEB",
        "instructor": "Eman M. Shurbaji",
        "hasAvailability": True,
        "status": "✅ 4 > 0"
    },
    
    # COMM 252 - News Writing (AVAILABLE!)
    {
        "course": "COMM252",
        "crn": "21592",
        "courseTitle": "News Writing",
        "section": "001",
        "credits": "3.000",
        "days": "R",
        "time": "6:00 PM - 8:40 PM",
        "dates": "09/04/25 - 12/21/25",
        "seatsAvailable": 5,
        "waitlistCount": 0,
        "campus": "Distance Learning",
        "location": "REMOTE",
        "instructor": "Eman M. Shurbaji",
        "hasAvailability": True,
        "status": "✅ 5 > 0"
    }
]

def generate_corrected_report():
    """Generate a report with the real, corrected COMM course data"""
    
    available_courses = [c for c in REAL_COMM_COURSES if c['hasAvailability']]
    rockville_available = [c for c in available_courses if 'Rockville' in c['campus']]
    
    print("🎯 CORRECTED MONTGOMERY COLLEGE COMM COURSES - FALL 2025")
    print("=" * 60)
    print(f"📊 Total COMM sections analyzed: {len(REAL_COMM_COURSES)}")
    print(f"✅ Available sections (seats > waitlist): {len(available_courses)}")
    print(f"🏫 Available at Rockville: {len(rockville_available)}")
    print("")
    
    if available_courses:
        print("🎉 AVAILABLE COMM COURSES:")
        print("-" * 40)
        for course in available_courses:
            print(f"✅ CRN {course['crn']}: {course['course']} - {course['courseTitle']}")
            print(f"   📍 {course['campus']} | {course['days']} {course['time']}")
            print(f"   👨‍🏫 {course['instructor']} | 🪑 {course['seatsAvailable']} seats, {course['waitlistCount']} waitlist")
            print("")
    
    print("❌ ABOUT CRN 203519:")
    print("-" * 20)
    print("CRN 203519 is NOT found in Montgomery College Fall 2025 COMM courses.")
    print("Possible reasons:")
    print("1. Wrong term (maybe Spring 2025 or Summer)")
    print("2. Wrong subject (maybe not COMM)")  
    print("3. Course was cancelled/removed")
    print("4. Typo in the CRN number")
    print("")
    print("✅ However, we found many OTHER available COMM courses!")

if __name__ == "__main__":
    generate_corrected_report()