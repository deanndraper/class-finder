#!/usr/bin/env python3
"""
Integration test for smart header parser in main application
Tests multiple subjects to verify the parser works universally
"""

import requests
import json

def test_subject(subject_name):
    """Test a specific subject with the smart header parser"""
    
    payload = {
        'term': 'Fall 2025',
        'subject': subject_name,
        'courseNumber': None,
        'campus': None,
        'availability': False
    }
    
    print(f"\n🧪 Testing {subject_name} courses...")
    
    try:
        response = requests.post('http://localhost:8080/api/search', json=payload, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success') and data.get('results'):
                results = data['results']
                
                # Calculate metrics
                non_zero_waitlist = sum(1 for c in results if c['waitlistCount'] > 0)
                tba_campus = sum(1 for c in results if c['campus'] == 'TBA')
                availability_count = sum(1 for c in results if c['seatsAvailable'] > c['waitlistCount'])
                
                print(f"  ✅ Total courses: {len(results)}")
                print(f"  📊 Waitlist > 0: {non_zero_waitlist}/{len(results)} ({non_zero_waitlist/len(results)*100:.1f}%)")
                print(f"  🏫 Real campus: {len(results)-tba_campus}/{len(results)} ({(len(results)-tba_campus)/len(results)*100:.1f}%)")
                print(f"  🎯 Available: {availability_count}/{len(results)} ({availability_count/len(results)*100:.1f}%)")
                
                # Sample course
                sample = results[0]
                print(f"  📋 Sample: CRN {sample['crn']} - {sample['seatsAvailable']} seats, {sample['waitlistCount']} waitlist")
                
                return True
            else:
                print(f"  ❌ No {subject_name} results or API failed")
                return False
        else:
            print(f"  ❌ HTTP Error: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    """Run integration tests for multiple subjects"""
    
    print("🚀 Smart Header Parser Integration Test")
    print("=" * 50)
    
    subjects = ['COMM', 'BIOL', 'ENGL', 'MATH']
    results = {}
    
    for subject in subjects:
        results[subject] = test_subject(subject)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 INTEGRATION TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for subject, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {subject}")
    
    print(f"\n🎯 Overall: {passed}/{total} subjects passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Smart header parser integration successful!")
    else:
        print("⚠️ Some tests failed. Check individual subject results above.")
    
    return passed == total

if __name__ == "__main__":
    main()