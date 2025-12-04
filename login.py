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
        
        # Try multiple selectors for the edit icon
        edit_selectors = [
            "span.edit.icon",
            "span[class*='edit']",
            "i[class*='edit']",
            "button[class*='edit']",
            "a[class*='edit']",
            ".edit-icon",
            "[data-testid*='edit']"
        ]
        
        pencil_icon = None
        for selector in edit_selectors:
            try:
                pencil_icon = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                if pencil_icon:
                    print(f"✏ Edit icon found with selector: {selector}")
                    break
            except:
                continue
        
        if not pencil_icon:
            # Try to find by text or other methods
            try:
                pencil_icon = driver.find_element(By.XPATH, "//span[contains(@class, 'icon') and contains(@class, 'edit')]")
            except:
                try:
                    pencil_icon = driver.find_element(By.XPATH, "//*[contains(@class, 'edit') and contains(@class, 'icon')]")
                except:
                    pass
        
        if not pencil_icon:
            print("⚠️ Could not find edit icon, skipping headline update")
            return False
        
        # Scroll to element
        driver.execute_script("arguments[0].scrollIntoView(true);", pencil_icon)
        time.sleep(1)
        pencil_icon.click()
        time.sleep(2)
        
        # Try multiple selectors for textarea
        textarea_selectors = [
            "textarea",
            "textarea[class*='headline']",
            "textarea[id*='headline']",
            "input[type='text'][class*='headline']"
        ]
        
        textarea = None
        for selector in textarea_selectors:
            try:
                textarea = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
                if textarea:
                    break
            except:
                continue
        
        if not textarea:
            print("⚠️ Could not find textarea, skipping headline update")
            return False
        
        textarea.clear()
        time.sleep(0.5)
        textarea.send_keys(new_headline)
        time.sleep(1)
        
        # Try multiple selectors for save button
        save_selectors = [
            "//button[text()='Save']",
            "//button[contains(text(),'Save')]",
            "//button[@type='submit']",
            "button[class*='save']",
            "button[class*='submit']"
        ]
        
        save_button = None
        for selector in save_selectors:
            try:
                if selector.startswith("//"):
                    save_button = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                else:
                    save_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                if save_button:
                    break
            except:
                continue
        
        if not save_button:
            print("⚠️ Could not find save button, skipping headline update")
            return False
        
        save_button.click()
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
