import os
import json
import gzip
import base64
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def login_with_cookies(driver):
    print("🔐 Logging using encoded cookies....")

    encoded = os.environ.get("NAUKRI_COOKIES_B64")
    if not encoded:
        raise Exception("❌ NAUKRI_COOKIES_B64 environment variable not set")
    
    decoded = base64.b64decode(encoded)
    
    # Try to decompress with gzip, if it fails, assume it's plain JSON
    try:
        cookies = json.loads(gzip.decompress(decoded))
        print("✅ Cookies decompressed with gzip")
    except (gzip.BadGzipFile, OSError):
        # If not gzipped, try to decode as plain JSON
        try:
            cookies = json.loads(decoded.decode('utf-8'))
            print("✅ Cookies decoded as plain JSON")
        except Exception as e:
            raise Exception(f"❌ Failed to decode cookies: {e}")

    driver.get("https://www.naukri.com/")
    time.sleep(2)
    driver.delete_all_cookies()

    for cookie in cookies:
        cookie.pop('sameSite', None)
        driver.add_cookie(cookie)

    driver.get("https://www.naukri.com/mnjuser/homepage")
    time.sleep(3)

    if "homepage" in driver.current_url.lower():
        print("🎯 Cookie login success!")
        return driver

    raise Exception("❌ Cookie login failed — Refresh cookies manually")

def update_resume_headline(driver, wait, new_headline):
    """Update resume headline on Naukri profile page"""
    try:
        print("🔍 Looking for pencil icon to edit headline...")
        
        # Wait for page to load
        time.sleep(2)
        
        # Scroll to top to ensure we see the headline section
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        
        # Try multiple selectors for the edit icon (prioritized)
        edit_selectors = [
            "span.edit.icon",
            "i[class*='edit']",
            "span[class*='edit']",
            "button[class*='edit']",
            "a[class*='edit']",
            ".edit-icon",
            "[data-testid*='edit']",
            "//span[contains(@class, 'icon') and contains(@class, 'edit')]",
            "//i[contains(@class, 'edit')]",
            "//*[contains(@class, 'edit') and contains(@class, 'icon')]"
        ]
        
        pencil_icon = None
        for selector in edit_selectors:
            try:
                if selector.startswith("//"):
                    # Try direct find first (faster)
                    try:
                        pencil_icon = driver.find_element(By.XPATH, selector)
                        if pencil_icon and pencil_icon.is_displayed():
                            print(f"✏ Edit icon found with selector: {selector}")
                            break
                    except:
                        continue
                else:
                    # Try direct find first (faster)
                    try:
                        pencil_icon = driver.find_element(By.CSS_SELECTOR, selector)
                        if pencil_icon and pencil_icon.is_displayed():
                            print(f"✏ Edit icon found with selector: {selector}")
                            break
                    except:
                        continue
            except:
                continue
        
        if not pencil_icon:
            print("⚠️ Could not find edit icon, skipping headline update")
            return False
        
        # Scroll to element and try to click
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", pencil_icon)
        time.sleep(2)
        
        # Try JavaScript click first (avoids click interception)
        try:
            driver.execute_script("arguments[0].click();", pencil_icon)
            time.sleep(2)
        except:
            # If JS click fails, try regular click
            try:
                # Wait a bit more and try again
                time.sleep(1)
                pencil_icon.click()
                time.sleep(2)
            except Exception as e:
                print(f"⚠️ Could not click edit icon: {str(e)[:100]}")
                return False
        
        # Wait a bit for the edit form to appear
        time.sleep(2)
        
        # Try multiple selectors for textarea (prioritized)
        textarea_selectors = [
            "textarea[class*='headline']",
            "textarea[id*='headline']",
            "textarea",
            "input[type='text'][class*='headline']",
            "input[class*='headline']"
        ]
        
        textarea = None
        for selector in textarea_selectors:
            try:
                # Try direct find first (faster)
                try:
                    textarea = driver.find_element(By.CSS_SELECTOR, selector)
                    if textarea and textarea.is_displayed():
                        print(f"📝 Found textarea with selector: {selector}")
                        break
                except:
                    # If direct find fails, try with wait
                    try:
                        textarea = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
                        if textarea:
                            break
                    except:
                        continue
            except:
                continue
        
        if not textarea:
            print("⚠️ Could not find textarea, skipping headline update")
            return False
        
        textarea.clear()
        time.sleep(0.5)
        textarea.send_keys(new_headline)
        time.sleep(1)
        
        # Try multiple selectors for save button (prioritized)
        save_selectors = [
            "//button[contains(text(),'Save')]",
            "//button[text()='Save']",
            "button[class*='save']",
            "button[class*='submit']",
            "//button[@type='submit']",
            "button[type='submit']"
        ]
        
        save_button = None
        for selector in save_selectors:
            try:
                if selector.startswith("//"):
                    # Try direct find first
                    try:
                        save_button = driver.find_element(By.XPATH, selector)
                        if save_button and save_button.is_displayed():
                            print(f"💾 Found save button with selector: {selector}")
                            break
                    except:
                        # If direct find fails, try with wait
                        try:
                            save_button = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                            if save_button:
                                break
                        except:
                            continue
                else:
                    # Try direct find first
                    try:
                        save_button = driver.find_element(By.CSS_SELECTOR, selector)
                        if save_button and save_button.is_displayed():
                            print(f"💾 Found save button with selector: {selector}")
                            break
                    except:
                        # If direct find fails, try with wait
                        try:
                            save_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                            if save_button:
                                break
                        except:
                            continue
            except:
                continue
        
        if not save_button:
            print("⚠️ Could not find save button, skipping headline update")
            return False
        
        # Scroll to save button and click
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", save_button)
        time.sleep(1)
        
        # Try JavaScript click first
        try:
            driver.execute_script("arguments[0].click();", save_button)
            print("💾 Clicked save button (JS)")
        except:
            # If JS click fails, try regular click
            try:
                save_button.click()
                print("💾 Clicked save button (regular)")
            except Exception as e:
                print(f"⚠️ Could not click save button: {str(e)[:50]}")
                return False
        
        time.sleep(2)
        
        # Wait for textarea to disappear (confirmation it saved)
        try:
            wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "textarea")))
        except:
            pass  # Don't fail if we can't confirm
        
        print("✅ Resume headline updated successfully.")
        return True
    except Exception as e:
        error_msg = str(e)
        if len(error_msg) > 200:
            error_msg = error_msg[:200]
        print(f"❗Failed to update resume headline: {error_msg}")
        return False
