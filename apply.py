import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def apply_to_jobs(driver, job_cards, max_applications=7):
    applied = 0
    wait = WebDriverWait(driver, 10)
    
    if not job_cards:
        print("⚠️ No job cards to apply to")
        return applied
    
    print(f"🔄 Starting to apply to jobs (max {max_applications} per day)...")
    
    for idx, job in enumerate(job_cards, 1):
        # Stop if we've reached the daily limit
        if applied >= max_applications:
            print(f"✅ Reached daily limit of {max_applications} applications. Stopping.")
            break
        try:
            print(f"📋 Processing job {idx}/{len(job_cards)}...")
            
            # Scroll to job element
            driver.execute_script("arguments[0].scrollIntoView(true);", job)
            time.sleep(1)
            
            # Get job link if it's an anchor tag
            job_link = None
            try:
                if job.tag_name == 'a':
                    job_link = job.get_attribute('href')
                else:
                    # Try to find link within the job card
                    try:
                        link_elem = job.find_element(By.CSS_SELECTOR, "a")
                        job_link = link_elem.get_attribute('href')
                    except:
                        pass
            except Exception as e:
                print(f"⚠️ Could not get job link: {str(e)[:50]}")
                continue
            
            # Navigate to job link
            if job_link:
                print(f"🔗 Opening job link: {job_link[:80]}...")
                try:
                    driver.get(job_link)
                except:
                    # If direct navigation fails, try opening in new window
                    try:
                        driver.execute_script(f"window.open('{job_link}', '_blank');")
                        if len(driver.window_handles) > 1:
                            driver.switch_to.window(driver.window_handles[-1])
                    except:
                        print(f"⚠️ Could not navigate to job link")
                        continue
            else:
                print(f"⚠️ No job link found for job {idx}, skipping")
                continue
            
            # Wait for page to load
            time.sleep(4)

            # Wait for page to fully load
            try:
                WebDriverWait(driver, 10).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
            except:
                pass
            
            # Scroll to top first, then down to ensure page is loaded
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(2)
            
            # Try multiple ways to find and click Apply button
            apply_success = False
            apply_selectors = [
                # XPath selectors
                "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'apply')]",
                "//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'apply')]",
                "//button[contains(text(),'Apply')]",
                "//a[contains(text(),'Apply')]",
                "//button[contains(text(),'APPLY')]",
                "//a[contains(text(),'APPLY')]",
                "//span[contains(text(),'Apply')]/parent::button",
                "//span[contains(text(),'Apply')]/parent::a",
                "//span[contains(text(),'APPLY')]/parent::button",
                "//span[contains(text(),'APPLY')]/parent::a",
                "//button[contains(@class,'apply')]",
                "//a[contains(@class,'apply')]",
                "//button[contains(@id,'apply')]",
                "//a[contains(@id,'apply')]",
                "//button[contains(@data-testid,'apply')]",
                "//a[contains(@data-testid,'apply')]",
                # CSS selectors
                "button.applyBtn",
                "a.applyBtn",
                "button[class*='apply']",
                "a[class*='apply']",
                "button[class*='Apply']",
                "a[class*='Apply']",
                "button[id*='apply']",
                "a[id*='apply']",
                ".apply-button",
                "#apply-button",
                "button.btn-apply",
                "a.btn-apply"
            ]
            
            for selector in apply_selectors:
                try:
                    # Try with explicit wait first
                    try:
                        if selector.startswith("//"):
                            apply_btn = wait.until(
                                EC.element_to_be_clickable((By.XPATH, selector))
                            )
                        else:
                            apply_btn = wait.until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                            )
                    except:
                        # If explicit wait fails, try direct find
                        if selector.startswith("//"):
                            apply_btn = driver.find_element(By.XPATH, selector)
                        else:
                            apply_btn = driver.find_element(By.CSS_SELECTOR, selector)
                    
                    # Check if element is visible and enabled
                    if not apply_btn.is_displayed() or not apply_btn.is_enabled():
                        continue
                    
                    # Scroll to button
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", apply_btn)
                    time.sleep(1)
                    
                    # Try clicking with JavaScript first (more reliable)
                    try:
                        driver.execute_script("arguments[0].click();", apply_btn)
                        time.sleep(3)
                        applied += 1
                        print(f"✅ Applied to job {idx} 👍")
                        apply_success = True
                        break
                    except:
                        # If JS click fails, try regular click
                        try:
                            apply_btn.click()
                            time.sleep(3)
                            applied += 1
                            print(f"✅ Applied to job {idx} 👍")
                            apply_success = True
                            break
                        except:
                            continue
                except Exception as e:
                    continue
            
            # If still not found, try to find any button/link with "apply" in it
            if not apply_success:
                try:
                    all_buttons = driver.find_elements(By.TAG_NAME, "button")
                    all_links = driver.find_elements(By.TAG_NAME, "a")
                    all_elements = all_buttons + all_links
                    
                    for elem in all_elements:
                        try:
                            text = elem.text.lower()
                            class_attr = elem.get_attribute("class") or ""
                            id_attr = elem.get_attribute("id") or ""
                            
                            if ("apply" in text or "apply" in class_attr.lower() or "apply" in id_attr.lower()) and elem.is_displayed():
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
                                time.sleep(1)
                                driver.execute_script("arguments[0].click();", elem)
                                time.sleep(3)
                                applied += 1
                                print(f"✅ Applied to job {idx} (found via text/class search) 👍")
                                apply_success = True
                                break
                        except:
                            continue
                except:
                    pass
            
            if not apply_success:
                print(f"⚠️ Could not find Apply button for job {idx}")
            
            # Go back to search results page
            try:
                driver.back()
                time.sleep(2)
            except:
                # If back fails, navigate to search URL
                try:
                    # Try to get the search URL from the original page
                    driver.get("https://www.naukri.com/devops-engineer-jobs-in-bangalore")
                    time.sleep(2)
                except:
                    pass

        except Exception as e:
            error_msg = str(e)
            if len(error_msg) > 100:
                error_msg = error_msg[:100]
            print(f"❌ Error applying to job {idx}: {error_msg}")
            
            # Try to go back to search results
            try:
                driver.back()
                time.sleep(2)
            except:
                try:
                    driver.get("https://www.naukri.com/devops-engineer-jobs-in-bangalore")
                    time.sleep(2)
                except:
                    pass
            continue

    return applied
