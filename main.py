from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

from config import Config
from login import login
from search import search_jobs
from apply import apply_jobs

def main():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])


    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    driver = login(driver, Config.EMAIL, Config.PASSWORD)
    jobs = search_jobs(driver, Config.KEYWORDS, Config.LOCATION)
    applied = apply_jobs(driver, jobs, Config.APPLY_LIMIT)

    print(f"🎉 Applied {applied} jobs today!")

    driver.quit()

if __name__ == "__main__":
    main()
