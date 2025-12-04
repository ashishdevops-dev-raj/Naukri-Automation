from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def search_jobs(driver, keywords, location):
    from urllib.parse import quote
    keywords = quote(keywords)
    location = quote(location)
    url = f"https://www.naukri.com/{keywords}-jobs-in-{location}"
    print(f"🔎 Searching: {url}")
    driver.get(url)

    try:
        job_cards = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.title"))
        )
    except:
        print("❌ No job cards found")
        return []

    jobs = []
    for card in job_cards:
        try:
            jobs.append({
                "title": card.text.strip(),
                "link": card.get_attribute("href")
            })
        except:
            continue
    print(f"📌 Found {len(jobs)} jobs.")
    return jobs
