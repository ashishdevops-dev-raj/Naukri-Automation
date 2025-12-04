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

# ------------------------------------------
# UPDATE RESUME HEADLINE
# ------------------------------------------
def update_resume_headline(driver, wait, new_headline):
    try:
        print("🔍 Looking for pencil icon to edit headline...")
        pencil_icon = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "span.edit.icon")))
        print("✏ Pencil icon found, clicking...")
        pencil_icon.click()
        textarea = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "textarea")))
        textarea.clear()
        textarea.send_keys(new_headline)
        save_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Save']")))
        save_button.click()
        wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "textarea")))
        print("✅ Resume headline updated successfully.")
        return True
    except Exception as e:
        print("❗Failed to update resume headline:", e)
        return False

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

def apply_to_jobs(driver, job_cards):
    applied = 0
    wait = WebDriverWait(driver, 10)
    
    if not job_cards:
        print("⚠️ No job cards to apply to")
        return applied
    
    print(f"🔄 Starting to apply to {len(job_cards)} jobs...")
    
    for idx, job in enumerate(job_cards, 1):
        try:
            print(f"📋 Processing job {idx}/{len(job_cards)}...")
            
            # Scroll to job element
            driver.execute_script("arguments[0].scrollIntoView(true);", job)
            time.sleep(1)
            
            # Get job link if it's an anchor tag
            job_link = None
            if job.tag_name == 'a':
                job_link = job.get_attribute('href')
            else:
                # Try to find link within the job card
                try:
                    link_elem = job.find_element(By.CSS_SELECTOR, "a")
                    job_link = link_elem.get_attribute('href')
                except:
                    pass
            
            # Click on job or navigate to link
            if job_link:
                print(f"🔗 Opening job link: {job_link[:80]}...")
                driver.execute_script(f"window.open('{job_link}', '_blank');")
            else:
                job.click()
            
            time.sleep(2)
            
            # Switch to new window
            if len(driver.window_handles) > 1:
                driver.switch_to.window(driver.window_handles[-1])
                time.sleep(3)
            else:
                time.sleep(3)  # If no new window, wait for page to load

            # Try multiple ways to find and click Apply button
            apply_success = False
            apply_selectors = [
                "//button[contains(text(),'Apply')]",
                "//a[contains(text(),'Apply')]",
                "//button[contains(@class,'apply')]",
                "//a[contains(@class,'apply')]",
                "//span[contains(text(),'Apply')]/parent::button",
                "//span[contains(text(),'Apply')]/parent::a"
            ]
            
            for selector in apply_selectors:
                try:
                    apply_btn = wait.until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    driver.execute_script("arguments[0].scrollIntoView(true);", apply_btn)
                    time.sleep(1)
                    apply_btn.click()
                    time.sleep(2)
                    applied += 1
                    print(f"✅ Applied to job {idx} 👍")
                    apply_success = True
                    break
                except Exception as e:
                    continue
            
            if not apply_success:
                print(f"⚠️ Could not find Apply button for job {idx}")
            
            # Close current window and switch back
            if len(driver.window_handles) > 1:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            else:
                # If no new window was opened, go back
                driver.back()
                time.sleep(2)

        except Exception as e:
            print(f"❌ Error applying to job {idx}: {str(e)[:100]}")
            # Make sure we're back on the main window
            try:
                if len(driver.window_handles) > 1:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                else:
                    driver.back()
            except:
                pass
            continue

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

    # Update resume headline
    new_headline = (
        "With over +2 years of experience in Application Support and a Master's degree in Computer Applications, "
        "I am proficient in technologies such as Unix, SQL, Jenkins, Docker, Git, ITIL, and Shell Scripting, "
        "along with additional exposure to DevOps."
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

    KEYWORDS = os.getenv("KEYWORDS", "devops engineer")
    LOCATION = os.getenv("LOCATION", "bangalore")

    job_cards = search_jobs(driver, KEYWORDS, LOCATION)
    print(f"📌 Found {len(job_cards)} jobs.")

    applied = apply_to_jobs(driver, job_cards)
    print(f"🎉 Applied {applied} jobs today!")

    driver.quit()
