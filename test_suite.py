#!/usr/bin/env python3
"""
Comprehensive test suite for the course scraping system
Tests each component to identify where the failure is occurring
"""

import asyncio
import json
import requests
from datetime import datetime

def test_backend_health():
    """Test 1: Backend health check"""
    print("🔧 TEST 1: Backend Health Check")
    try:
        response = requests.get('http://localhost:8080/api/health', timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_generic_scraper_direct():
    """Test 2: Direct generic scraper test"""
    print("\n🔧 TEST 2: Direct Generic Scraper")
    try:
        from generic_course_scraper import MontgomeryCollegeScraper
        
        async def run_test():
            scraper = MontgomeryCollegeScraper()
            print("   ✅ Scraper created successfully")
            
            # Test with BIOL
            print("   🧬 Testing BIOL courses...")
            biol_courses = await scraper.scrape_courses(
                term='Fall 2025',
                subject='BIOL',
                course_filter=None,
                campus_filter=None,
                use_cache=False  # Force fresh scrape
            )
            
            print(f"   📊 BIOL Results: {len(biol_courses)} courses")
            if biol_courses:
                available = [c for c in biol_courses if c.get('hasAvailability', False)]
                print(f"   ✅ Available: {len(available)} courses")
                
                # Show sample course
                sample = biol_courses[0]
                print(f"   📋 Sample course: {sample}")
                return len(biol_courses) > 0
            else:
                print("   ❌ No BIOL courses found")
                return False
        
        return asyncio.run(run_test())
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_backend_import():
    """Test 3: Backend import capabilities"""
    print("\n🔧 TEST 3: Backend Import Test")
    try:
        # Test individual imports
        from generic_course_scraper import MontgomeryCollegeScraper
        print("   ✅ MontgomeryCollegeScraper imported successfully")
        
        from generic_course_scraper import search_courses
        print("   ✅ search_courses function imported successfully")
        
        # Test function signature
        import inspect
        sig = inspect.signature(search_courses)
        print(f"   📋 search_courses signature: {sig}")
        
        return True
    except Exception as e:
        print(f"   ❌ Import error: {e}")
        return False

def test_backend_api_call():
    """Test 4: Full API call test"""
    print("\n🔧 TEST 4: Backend API Call")
    try:
        payload = {
            'term': 'Fall 2025',
            'subject': 'BIOL',
            'courseNumber': None,
            'campus': None,
            'availability': False
        }
        
        print(f"   📤 Sending request: {payload}")
        response = requests.post(
            'http://localhost:8080/api/search', 
            json=payload,
            timeout=120  # 2 minutes for scraping
        )
        
        print(f"   📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   📊 Success: {data.get('success', False)}")
            print(f"   📋 Total results: {data.get('totalResults', 0)}")
            print(f"   ✅ Available results: {data.get('availableResults', 0)}")
            
            if data.get('results'):
                sample = data['results'][0]
                print(f"   📋 Sample result: {sample}")
            
            return data.get('success', False) and data.get('totalResults', 0) > 0
        else:
            print(f"   ❌ HTTP Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_simple_comm_fallback():
    """Test 5: COMM fallback test"""
    print("\n🔧 TEST 5: COMM Fallback Test")
    try:
        payload = {
            'term': 'Fall 2025',
            'subject': 'COMM',
            'courseNumber': None,
            'campus': None,
            'availability': False
        }
        
        response = requests.post(
            'http://localhost:8080/api/search', 
            json=payload,
            timeout=60
        )
        
        print(f"   📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   📊 Success: {data.get('success', False)}")
            print(f"   📋 Total results: {data.get('totalResults', 0)}")
            return data.get('success', False) and data.get('totalResults', 0) > 0
        else:
            print(f"   ❌ HTTP Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_cache_functionality():
    """Test 6: Cache system"""
    print("\n🔧 TEST 6: Cache System Test")
    try:
        import os
        cache_dir = "course_cache"
        
        if os.path.exists(cache_dir):
            cache_files = os.listdir(cache_dir)
            print(f"   📁 Cache directory exists with {len(cache_files)} files")
            
            for file in cache_files[:3]:  # Show first 3
                file_path = os.path.join(cache_dir, file)
                size = os.path.getsize(file_path)
                mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                print(f"   📄 {file}: {size} bytes, modified {mtime}")
            
            return len(cache_files) > 0
        else:
            print("   ⚠️ No cache directory found")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_browser_availability():
    """Test 7: Browser/Playwright availability"""
    print("\n🔧 TEST 7: Browser Availability")
    try:
        from playwright.async_api import async_playwright
        
        async def browser_test():
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto('https://www.google.com')
                title = await page.title()
                await browser.close()
                return "Google" in title
        
        result = asyncio.run(browser_test())
        print(f"   🌐 Browser test: {'✅ Success' if result else '❌ Failed'}")
        return result
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def run_all_tests():
    """Run all tests and provide summary"""
    print("🧪 COURSE SCRAPER TEST SUITE")
    print("=" * 50)
    
    tests = [
        ("Backend Health", test_backend_health),
        ("Generic Scraper Direct", test_generic_scraper_direct),
        ("Backend Imports", test_backend_import),
        ("Backend API Call", test_backend_api_call),
        ("COMM Fallback", test_simple_comm_fallback),
        ("Cache System", test_cache_functionality),
        ("Browser Availability", test_browser_availability)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"\n🎯 OVERALL: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! System should be working.")
    else:
        print("⚠️ Some tests failed. Check individual test outputs above.")
        
        # Provide specific guidance
        if not results.get("Backend Health", False):
            print("💡 Try: Make sure backend server is running on port 8080")
        
        if not results.get("Browser Availability", False):
            print("💡 Try: Install browser with 'playwright install chromium'")
        
        if not results.get("Generic Scraper Direct", False):
            print("💡 Issue: Direct scraper is failing - check playwright/network")
        
        if not results.get("Backend API Call", False):
            print("💡 Issue: API integration is broken - check backend logs")

if __name__ == "__main__":
    run_all_tests()