import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

from login import login_with_cookies, update_resume_headline
from search import search_jobs
from apply import apply_to_jobs

if __name__ == "__main__":
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--headless=new")

    driver = webdriver.Chrome(options=chrome_options)

    # Login with cookies
    login_with_cookies(driver)
    print("🎯 Cookie login success!")

    # Update resume headline
    new_headline = (
        "With over +2 years of experience in Application Support and a Master's degree in Computer Applications, "
        "I am proficient in technologies such as Unix, SQL, Jenkins, Docker, Git, ITIL, and Shell Scripting, "
        "along with additional exposure to DevOps....."
    )
    
    print("\n📝 Updating resume headline...")
    wait = WebDriverWait(driver, 10)
    try:
        # Navigate to profile page
        driver.get("https://www.naukri.com/mnjuser/profile")
        time.sleep(3)
        update_resume_headline(driver, wait, new_headline)
    except Exception as e:
        print(f"⚠️ Could not update resume headline: {e}")
        print("Continuing with job search...")

    # Search for jobs
    KEYWORDS = os.getenv("KEYWORDS", "devops engineer")
    LOCATION = os.getenv("LOCATION", "bangalore")

    job_cards = search_jobs(driver, KEYWORDS, LOCATION)
    print(f"📌 Found {len(job_cards)} jobs.")

    # Apply to jobs
    applied = apply_to_jobs(driver, job_cards)
    print(f"🎉 Applied {applied} jobs today!")

    driver.quit()
