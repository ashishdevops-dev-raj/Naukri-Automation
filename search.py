from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def search_jobs(driver, keywords, location):
    driver.get("https://www.naukri.com/")
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Enter skills / designations']"))
    ).send_keys(",".join(keywords))

    loc = driver.find_element(By.XPATH, "//input[@placeholder='Enter location']")
    loc.clear()
    loc.send_keys(location)

    driver.find_element(By.XPATH, "//button[text()='Search']").click()

    WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.XPATH, "//a[@class='title fw500 ellipsis']"))
    )

    job_links = [el.get_attribute("href") for el in driver.find_elements(By.XPATH, "//a[@class='title fw500 ellipsis']")]
    print(f"🔎 Found {len(job_links)} jobs")
    return job_links[:50]
