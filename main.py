import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

from login import login_with_cookies
from search import search_jobs
from apply import apply_to_jobs

if __name__ == "__main__":
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--headless=new")
    
    # Anti-detection measures
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Exclude automation indicators
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Additional preferences
    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.default_content_setting_values.notifications": 2
    }
    chrome_options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(20)  # Set page load timeout
    
    # Additional stealth measures via CDP
    try:
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                window.chrome = { runtime: {} };
            '''
        })
    except:
        pass

    # Login with cookies
    login_with_cookies(driver)
    print("🎯 Cookie login success!")
    
    # Wait a bit after login to establish session
    time.sleep(2)
    
    # Navigate to homepage first to establish session
    try:
        driver.get("https://www.naukri.com/mnjuser/homepage")
        time.sleep(2)
        print("✅ Navigated to homepage")
    except:
        pass

    # Skip resume headline update to save time - it's optional
    # Search for jobs
    KEYWORDS = os.getenv("KEYWORDS", "devops engineer")

    job_cards = search_jobs(driver, KEYWORDS)
    print(f"📌 Found {len(job_cards)} jobs.")

    # Apply to jobs (limit to 10 per day)
    MAX_APPLICATIONS = int(os.getenv("MAX_APPLICATIONS", "10"))
    applied = apply_to_jobs(driver, job_cards, max_applications=MAX_APPLICATIONS)
    print(f"🎉 Applied {applied} jobs today! (Limit: {MAX_APPLICATIONS})")

    driver.quit()
