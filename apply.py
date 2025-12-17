import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def apply_to_jobs(driver, job_links, max_applications=10):
    applied = 0
    wait = WebDriverWait(driver, 10)
    
    if not job_links:
        print("⚠️ No job links to apply to")
        return applied
    
    print(f"🔄 Starting to apply to jobs (max {max_applications} per day)...")
    
    for idx, job_link in enumerate(job_links, 1):
        # Stop if we've reached the daily limit
        if applied >= max_applications:
            print(f"✅ Reached daily limit of {max_applications} applications. Stopping.")
            break
        
        try:
            print(f"📋 Processing job {idx}/{len(job_links)}...")
            
            # Navigate to job link
            if not job_link or not isinstance(job_link, str):
                print(f"⚠️ Invalid job link for job {idx}, skipping")
                continue
            
            print(f"🔗 Opening job link: {job_link[:80]}...")
            try:
                driver.get(job_link)
            except Exception as e:
                print(f"⚠️ Could not navigate to job link: {str(e)[:50]}")
                continue
            
            # Wait for page to load
            time.sleep(3)

            # Wait for page to fully load
            try:
                WebDriverWait(driver, 10).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
            except:
                pass
            
            # Scroll to ensure page is loaded
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(1)
            
            # Try multiple ways to find and click Apply button
            apply_success = False
            apply_selectors = [
                # Most common Naukri selectors first
                "button[class*='apply']",
                "a[class*='apply']",
                "button[id*='apply']",
                "a[id*='apply']",
                "button[data-testid*='apply']",
                "a[data-testid*='apply']",
                ".applyBtn",
                ".apply-btn",
                ".btn-apply",
                "#apply-button",
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
                # Additional CSS selectors
                "button.applyBtn",
                "a.applyBtn",
                "button[class*='Apply']",
                "a[class*='Apply']"
            ]
            
            for selector in apply_selectors:
                try:
                    # Try with explicit wait first
                    try:
                        if selector.startswith("//"):
                            apply_btn = wait.until(
                                EC.presence_of_element_located((By.XPATH, selector))
                            )
                        else:
                            apply_btn = wait.until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                            )
                    except:
                        # If explicit wait fails, try direct find
                        try:
                            if selector.startswith("//"):
                                apply_btn = driver.find_element(By.XPATH, selector)
                            else:
                                apply_btn = driver.find_element(By.CSS_SELECTOR, selector)
                        except:
                            continue
                    
                    # Check if element exists and is visible
                    if not apply_btn or not apply_btn.is_displayed():
                        continue
                    
                    # Check if button is enabled (not disabled)
                    try:
                        if not apply_btn.is_enabled():
                            continue
                    except:
                        pass
                    
                    # Scroll to button
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", apply_btn)
                    time.sleep(1)
                    
                    # Try clicking with JavaScript first (more reliable)
                    try:
                        driver.execute_script("arguments[0].click();", apply_btn)
                        time.sleep(2)
                        
                        # Handle any modals or confirmations that might appear
                        try:
                            # Look for confirmation buttons or modals
                            confirm_selectors = [
                                "button[class*='confirm']",
                                "button[class*='submit']",
                                "button[type='submit']",
                                "//button[contains(text(),'Confirm')]",
                                "//button[contains(text(),'Submit')]",
                                "//button[contains(text(),'Yes')]",
                                "//button[contains(text(),'OK')]"
                            ]
                            
                            for confirm_sel in confirm_selectors:
                                try:
                                    if confirm_sel.startswith("//"):
                                        confirm_btn = driver.find_element(By.XPATH, confirm_sel)
                                    else:
                                        confirm_btn = driver.find_element(By.CSS_SELECTOR, confirm_sel)
                                    
                                    if confirm_btn.is_displayed():
                                        driver.execute_script("arguments[0].click();", confirm_btn)
                                        time.sleep(1)
                                        break
                                except:
                                    continue
                        except:
                            pass
                        
                        # Wait a bit to ensure application is processed
                        time.sleep(2)
                        
                        applied += 1
                        print(f"✅ Applied to job {idx} 👍")
                        apply_success = True
                        break
                    except Exception as e:
                        # If JS click fails, try regular click
                        try:
                            apply_btn.click()
                            time.sleep(2)
                            
                            # Handle confirmations
                            try:
                                confirm_selectors = [
                                    "button[class*='confirm']",
                                    "button[class*='submit']",
                                    "//button[contains(text(),'Confirm')]",
                                    "//button[contains(text(),'Submit')]"
                                ]
                                
                                for confirm_sel in confirm_selectors:
                                    try:
                                        if confirm_sel.startswith("//"):
                                            confirm_btn = driver.find_element(By.XPATH, confirm_sel)
                                        else:
                                            confirm_btn = driver.find_element(By.CSS_SELECTOR, confirm_sel)
                                        
                                        if confirm_btn.is_displayed():
                                            driver.execute_script("arguments[0].click();", confirm_btn)
                                            time.sleep(1)
                                            break
                                    except:
                                        continue
                            except:
                                pass
                            
                            time.sleep(2)
                            applied += 1
                            print(f"✅ Applied to job {idx} 👍")
                            apply_success = True
                            break
                        except Exception as e2:
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
                            if not elem.is_displayed():
                                continue
                                
                            text = elem.text.lower().strip()
                            class_attr = elem.get_attribute("class") or ""
                            id_attr = elem.get_attribute("id") or ""
                            
                            if ("apply" in text or "apply" in class_attr.lower() or "apply" in id_attr.lower()):
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
                                time.sleep(1)
                                driver.execute_script("arguments[0].click();", elem)
                                time.sleep(2)
                                
                                # Handle confirmations
                                try:
                                    confirm_selectors = [
                                        "button[class*='confirm']",
                                        "button[class*='submit']",
                                        "//button[contains(text(),'Confirm')]",
                                        "//button[contains(text(),'Submit')]"
                                    ]
                                    
                                    for confirm_sel in confirm_selectors:
                                        try:
                                            if confirm_sel.startswith("//"):
                                                confirm_btn = driver.find_element(By.XPATH, confirm_sel)
                                            else:
                                                confirm_btn = driver.find_element(By.CSS_SELECTOR, confirm_sel)
                                            
                                            if confirm_btn.is_displayed():
                                                driver.execute_script("arguments[0].click();", confirm_btn)
                                                time.sleep(1)
                                                break
                                        except:
                                            continue
                                except:
                                    pass
                                
                                time.sleep(2)
                                applied += 1
                                print(f"✅ Applied to job {idx} (found via text/class search) 👍")
                                apply_success = True
                                break
                        except:
                            continue
                except Exception as e:
                    pass
            
            if not apply_success:
                print(f"⚠️ Could not find Apply button for job {idx}")
                # Print page info for debugging
                try:
                    print(f"   Current URL: {driver.current_url[:100]}")
                    print(f"   Page title: {driver.title[:50]}")
                except:
                    pass
            
            # Wait a bit before moving to next job
            time.sleep(1)

        except Exception as e:
            error_msg = str(e)
            if len(error_msg) > 100:
                error_msg = error_msg[:100]
            print(f"❌ Error applying to job {idx}: {error_msg}")
            continue

    return applied
