import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def search_jobs(driver, keywords, location):
    search_url = (
        f"https://www.naukri.com/{keywords.replace(' ', '-')}-jobs-in-{location.replace(' ', '-')}"
    )
    print("🔎 Searching:", search_url)
    driver.get(search_url)
    time.sleep(5)  # Give page more time to load

    wait = WebDriverWait(driver, 15)
    
    # Try multiple selectors to find job cards
    selectors = [
        "article.jobTuple",
        "a.title",
        "div[data-job-id]",
        "article[data-job-id]",
        ".jobTuple",
        ".jobCard"
    ]
    
    job_cards = []
    for selector in selectors:
        try:
            print(f"🔍 Trying selector: {selector}")
            job_cards = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
            )
            if job_cards:
                print(f"✅ Found {len(job_cards)} jobs using selector: {selector}")
                break
        except Exception as e:
            print(f"⚠️ Selector {selector} failed: {str(e)[:50]}")
            continue
    
    if not job_cards:
        print("⚠️ No jobs found with any selector. Checking page source...")
        # Try to find any clickable job elements
        try:
            job_cards = driver.find_elements(By.CSS_SELECTOR, "a[href*='/job-listings/'], a[href*='/job-details/']")
            if job_cards:
                print(f"✅ Found {len(job_cards)} potential job links")
        except:
            pass
    
    return job_cards
