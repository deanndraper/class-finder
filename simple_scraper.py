#!/usr/bin/env python3
"""
Simple Montgomery College COMM Course Scraper
"""

import asyncio
from playwright.async_api import async_playwright

async def scrape_courses():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            print("Navigating to Montgomery College...")
            await page.goto('https://mcssb.glb.montgomerycollege.edu/eagle/bwckschd.p_disp_dyn_sched')
            await page.wait_for_load_state('networkidle')
            
            # Take screenshot to see what we have
            await page.screenshot(path='initial_page.png')
            print("Screenshot saved as initial_page.png")
            
            # Get page title and URL
            title = await page.title()
            url = page.url
            print(f"Page title: {title}")
            print(f"Current URL: {url}")
            
            # Look for the term dropdown
            term_select = await page.locator('select').first.is_visible()
            if term_select:
                print("Found term dropdown")
                
                # Get all options
                options = await page.locator('select option').all_text_contents()
                print(f"Available terms: {options[:5]}")  # Show first 5
                
                # Try to select Fall 2025
                try:
                    await page.select_option('select', label='Fall 2025')
                    print("Selected Fall 2025")
                    
                    # Click Submit
                    await page.click('input[type="submit"]')
                    await page.wait_for_load_state('networkidle')
                    
                    # Take another screenshot
                    await page.screenshot(path='after_submit.png')
                    print("Screenshot after submit saved as after_submit.png")
                    
                except Exception as e:
                    print(f"Error selecting term: {e}")
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            # Keep browser open for inspection
            print("Browser will stay open for 30 seconds...")
            await asyncio.sleep(30)
            await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_courses())