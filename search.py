from selenium.webdriver.common.by import By
from urllib.parse import quote
import time

def search_jobs(driver, keywords, location):
    keywords = quote(keywords)
    location = quote(location)

    url = f"https://www.naukri.com/{keywords}-jobs-in-{location}"
    print(f"🔎 Searching: {url}")
    driver.get(url)
    time.sleep(4)

    job_cards = driver.find_elements(By.CSS_SELECTOR, "a.title")

    jobs = []
    for card in job_cards:
        try:
            job = {
                "title": card.text.strip(),
                "link": card.get_attribute("href")
            }
            jobs.append(job)
        except:
            continue

    print(f"📌 Found {len(jobs)} jobs.")
    return jobs
