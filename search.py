import time
from urllib.parse import quote

def search_jobs(driver, keywords, location):
    print("🔎 Searching jobs...")

    keywords = str(keywords or "")
    location = str(location or "")

    kw = quote(keywords)
    loc = quote(location)

    url = f"https://www.naukri.com/{kw}-jobs-in-{loc}"
    driver.get(url)
    time.sleep(4)

    job_cards = driver.find_elements("css selector", "a.title")

    jobs = []
    for job in job_cards[:50]:
        jobs.append({
            "title": job.text,
            "link": job.get_attribute("href")
        })

    print(f"📌 Found {len(jobs)} jobs.")
    return jobs
