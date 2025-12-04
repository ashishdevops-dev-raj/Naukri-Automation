import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
