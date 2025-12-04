import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def search_jobs(driver, keywords, location):
    search_url = (
        f"https://www.naukri.com/{keywords.replace(' ', '-')}-jobs-in-{location.replace(' ', '-')}"
    )
    print("🔎 Searching:", search_url)
    
    # Check for Access Denied before navigating
    try:
        current_url = driver.current_url
        if "access" in current_url.lower() or "denied" in current_url.lower():
            print("⚠️ Access Denied detected on current page. Trying to navigate to homepage first...")
            driver.get("https://www.naukri.com/mnjuser/homepage")
            time.sleep(5)
    except:
        pass
    
    # Navigate to search URL
    driver.get(search_url)
    
    # Wait for page to fully load
    time.sleep(8)  # Increased wait time
    
    # Check if we got Access Denied
    try:
        page_title = driver.title.lower()
        page_source = driver.page_source.lower()
        current_url = driver.current_url.lower()
        
        if "access denied" in page_title or "access denied" in page_source or len(driver.page_source) < 1000:
            print("⚠️ Access Denied detected! Trying alternative approach...")
            
            # Try navigating via homepage first
            driver.get("https://www.naukri.com/mnjuser/homepage")
            time.sleep(5)
            
            # Try using the search box on homepage instead
            try:
                from selenium.webdriver.common.keys import Keys
                search_input = driver.find_element(By.CSS_SELECTOR, "input[placeholder*='Search'], input[name*='search'], input[id*='search']")
                search_input.clear()
                search_input.send_keys(keywords)
                search_input.send_keys(Keys.RETURN)
                time.sleep(8)
                print("✅ Used homepage search box")
            except:
                # If that fails, try direct URL again
                driver.get(search_url)
                time.sleep(8)
    except Exception as e:
        print(f"⚠️ Error checking for Access Denied: {str(e)[:50]}")
    
    # Wait for page to be ready
    try:
        WebDriverWait(driver, 20).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
    except:
        pass
    
    wait = WebDriverWait(driver, 20)
    
    # Try to handle any popups or overlays first
    try:
        close_buttons = driver.find_elements(By.CSS_SELECTOR, "button[class*='close'], span[class*='close'], a[class*='close']")
        for btn in close_buttons[:3]:  # Try first 3 close buttons
            try:
                if btn.is_displayed():
                    btn.click()
                    time.sleep(1)
            except:
                pass
    except:
        pass
    
    # Scroll down to load more content
    try:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        time.sleep(2)
    except:
        pass
    
    # Expanded list of selectors to try
    selectors = [
        "article.jobTuple",
        "a.title",
        "div[data-job-id]",
        "article[data-job-id]",
        ".jobTuple",
        ".jobCard",
        "div[class*='jobTuple']",
        "div[class*='jobCard']",
        "article[class*='job']",
        "a[href*='/job-listings/']",
        "a[href*='/job-details/']",
        "div[class*='list'] a[href*='job']",
        ".srp-jobtuple-wrapper",
        ".row",
        "div[class*='srp'] a[title]"
    ]
    
    job_cards = []
    for selector in selectors:
        try:
            print(f"🔍 Trying selector: {selector}")
            # Try with explicit wait first
            try:
                job_cards = wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
                )
            except TimeoutException:
                # If explicit wait fails, try direct find
                job_cards = driver.find_elements(By.CSS_SELECTOR, selector)
            
            if job_cards and len(job_cards) > 0:
                print(f"✅ Found {len(job_cards)} jobs using selector: {selector}")
                break
        except Exception as e:
            error_msg = str(e)
            if len(error_msg) > 100:
                error_msg = error_msg[:100]
            print(f"⚠️ Selector {selector} failed: {error_msg}")
            continue
    
    # If still no jobs, try more aggressive search
    if not job_cards or len(job_cards) == 0:
        print("⚠️ No jobs found with standard selectors. Trying alternative methods...")
        
        # Try to find any links that might be job listings
        try:
            all_links = driver.find_elements(By.TAG_NAME, "a")
            job_links = []
            for link in all_links:
                try:
                    href = link.get_attribute("href") or ""
                    if href and ("/job-listings/" in href or "/job-details/" in href or "/job/" in href):
                        if link not in job_links:
                            job_links.append(link)
                except:
                    continue
            if job_links:
                job_cards = job_links
                print(f"✅ Found {len(job_cards)} jobs using link search")
        except Exception as e:
            print(f"⚠️ Link search failed: {str(e)[:50]}")
        
        # Try to find by text content
        if not job_cards or len(job_cards) == 0:
            try:
                # Look for elements with job-related text
                job_elements = driver.find_elements(By.XPATH, "//*[contains(@class, 'job') or contains(@class, 'listing')]")
                if job_elements:
                    job_cards = job_elements[:50]  # Limit to first 50
                    print(f"✅ Found {len(job_cards)} potential job elements using class search")
            except:
                pass
    
    # Final check - if still no jobs, print page info for debugging
    if not job_cards or len(job_cards) == 0:
        try:
            page_title = driver.title
            current_url = driver.current_url
            print(f"⚠️ Page title: {page_title}")
            print(f"⚠️ Current URL: {current_url}")
            print(f"⚠️ Page source length: {len(driver.page_source)} characters")
        except:
            pass
    
    # Extract job links immediately to avoid stale element references
    job_links = []
    for card in job_cards:
        try:
            if card.tag_name == 'a':
                href = card.get_attribute('href')
            else:
                link_elem = card.find_element(By.CSS_SELECTOR, "a")
                href = link_elem.get_attribute('href')
            
            if href and href not in job_links:
                job_links.append(href)
        except:
            continue
    
    if job_links:
        print(f"✅ Extracted {len(job_links)} job links")
        return job_links
    else:
        # If we couldn't extract links, return empty list
        return []
