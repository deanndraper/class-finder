#!/usr/bin/env python3
"""
Test script to verify the new table-based parsing logic works correctly
"""

import asyncio
import requests
import json

def test_api_with_table_parsing():
    print("🧪 Testing new table-based parsing logic via API...")
    
    # Test BIOL courses
    print("\n📚 Testing BIOL courses...")
    payload = {
        'term': 'Fall 2025',
        'subject': 'BIOL',
        'courseNumber': None,
        'campus': None,
        'availability': False
    }
    
    try:
        response = requests.post('http://localhost:8080/api/search', json=payload, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Success: {data.get('success', False)}")
            print(f"📊 Total results: {data.get('totalResults', 0)}")
            print(f"🎯 Available results: {data.get('availableResults', 0)}")
            
            if data.get('results'):
                print(f"\n📋 Sample BIOL courses with NEW parsing:")
                for i, course in enumerate(data['results'][:5]):  # Show first 5
                    print(f"  {i+1}. CRN {course['crn']}: {course['course']}")
                    print(f"     📍 Campus: {course['campus']}")
                    print(f"     🪑 Seats: {course['seatsAvailable']}, Waitlist: {course['waitlistCount']}")
                    print(f"     👨‍🏫 Instructor: {course['instructor']}")
                    print(f"     📍 Location: {course['location']}")
                    print(f"     ⏰ Time: {course['days']} {course['time']}")
                    print(f"     ✅ Available: {course['hasAvailability']}")
                    print()
                
                # Check if waitlist counts are no longer always 0
                waitlist_counts = [c['waitlistCount'] for c in data['results']]
                non_zero_waitlist = sum(1 for w in waitlist_counts if w > 0)
                print(f"🔍 Waitlist Analysis:")
                print(f"   Total courses: {len(waitlist_counts)}")
                print(f"   Non-zero waitlist: {non_zero_waitlist}")
                print(f"   Waitlist range: {min(waitlist_counts)} to {max(waitlist_counts)}")
                
                # Check campus data quality
                campus_data = [c['campus'] for c in data['results']]
                tba_campus = sum(1 for c in campus_data if c == 'TBA')
                print(f"🏫 Campus Analysis:")
                print(f"   TBA campus entries: {tba_campus} out of {len(campus_data)}")
                
                # Check instructor data quality
                instructor_data = [c['instructor'] for c in data['results']]
                tba_instructor = sum(1 for i in instructor_data if i == 'TBA')
                print(f"👨‍🏫 Instructor Analysis:")
                print(f"   TBA instructor entries: {tba_instructor} out of {len(instructor_data)}")
                
                if non_zero_waitlist > 0:
                    print(f"🎉 SUCCESS: Waitlist parsing is now working! Found {non_zero_waitlist} courses with waitlist > 0")
                else:
                    print(f"⚠️ ISSUE: Still no courses with waitlist > 0")
                    
                if tba_campus < len(campus_data) * 0.5:  # Less than 50% TBA
                    print(f"🎉 SUCCESS: Campus parsing is improved! Only {tba_campus}/{len(campus_data)} are TBA")
                else:
                    print(f"⚠️ ISSUE: Campus parsing still needs work")
            
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")

def test_comm_courses():
    print("\n📚 Testing COMM courses...")
    payload = {
        'term': 'Fall 2025',
        'subject': 'COMM',
        'courseNumber': None,
        'campus': None,
        'availability': False
    }
    
    try:
        response = requests.post('http://localhost:8080/api/search', json=payload, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ COMM Results: {data.get('totalResults', 0)} courses")
            
            if data.get('results'):
                # Show sample COMM course
                sample = data['results'][0]
                print(f"📋 Sample COMM course:")
                print(f"   CRN {sample['crn']}: {sample['course']}")
                print(f"   Campus: {sample['campus']}, Location: {sample['location']}")
                print(f"   Seats: {sample['seatsAvailable']}, Waitlist: {sample['waitlistCount']}")
        else:
            print(f"❌ COMM API Error: {response.status_code}")
    
    except Exception as e:
        print(f"❌ COMM test failed: {e}")

if __name__ == "__main__":
    test_api_with_table_parsing()
    test_comm_courses()