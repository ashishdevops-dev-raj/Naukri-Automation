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
