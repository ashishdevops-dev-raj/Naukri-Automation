import os
import time
import base64
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def load_cookies(driver):
    cookies_b64 = os.getenv("NAUKRI_COOKIES_B64")
    cookies = json.loads(base64.b64decode(cookies_b64).decode())
    for cookie in cookies:
        driver.add_cookie(cookie)

def login_with_cookies(driver):
    driver.get("https://www.naukri.com/")
    load_cookies(driver)
    driver.refresh()
    time.sleep(3)

def search_jobs(driver, keywords, location):
    search_url = (
        f"https://www.naukri.com/{keywords.replace(' ', '-')}-jobs-in-{location.replace(' ', '-')}"
    )
    print("🔎 Searching:", search_url)
    driver.get(search_url)

    try:
        # Wait until jobs appear
        job_cards = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article.jobTuple"))
        )
        return job_cards
    except:
        return []

def apply_to_jobs(driver, job_cards):
    applied = 0
    for job in job_cards:
        try:
            job.click()
            time.sleep(2)

            driver.switch_to.window(driver.window_handles[-1])
            time.sleep(3)

            try:
                apply_btn = driver.find_element(By.XPATH, "//button[contains(text(),'Apply')]")
                apply_btn.click()
                applied += 1
                print("Applied 👍")
            except:
                pass

            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        except Exception as e:
            print("Error:", e)
            pass

    return applied

if __name__ == "__main__":
    print("🔐 Logging using encoded cookies....")

    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--headless=new")

    driver = webdriver.Chrome(options=chrome_options)

    login_with_cookies(driver)
    print("🎯 Cookie login success!")

    KEYWORDS = os.getenv("KEYWORDS", "devops engineer")
    LOCATION = os.getenv("LOCATION", "bangalore")

    job_cards = search_jobs(driver, KEYWORDS, LOCATION)
    print(f"📌 Found {len(job_cards)} jobs.")

    applied = apply_to_jobs(driver, job_cards)
    print(f"🎉 Applied {applied} jobs today!")

    driver.quit()
