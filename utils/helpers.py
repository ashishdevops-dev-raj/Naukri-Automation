# utils/helpers.py
import os
import json
import time
from datetime import datetime
from typing import List, Dict

from selenium.webdriver.remote.webdriver import WebDriver

from utils.logger import setup_logger
logger = setup_logger(__name__)

SCREENSHOTS_DIR = "screenshots"
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

def take_screenshot(driver: WebDriver, name: str):
    """Save screenshot to screenshots/ with timestamp."""
    try:
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{ts}.png"
        path = os.path.join(SCREENSHOTS_DIR, filename)
        try:
            driver.get_screenshot_as_file(path)
        except Exception:
            driver.save_screenshot(path)
        logger.info(f"Screenshot saved: {path}")
        return path
    except Exception as e:
        logger.warning(f"Failed to take screenshot: {e}")
        return None

def cleanup_driver(driver: WebDriver, quit_driver: bool = True):
    """Close/quits driver safely."""
    if not driver:
        return
    try:
        try:
            driver.execute_script("window.open('');")
            tabs = driver.window_handles
            for handle in tabs:
                try:
                    driver.switch_to.window(handle)
                    driver.close()
                except:
                    continue
        except Exception:
            pass
        if quit_driver:
            try:
                driver.quit()
            except Exception:
                try:
                    driver.close()
                except Exception:
                    pass
        logger.info("WebDriver cleaned up")
    except Exception as e:
        logger.warning(f"Error during driver cleanup: {e}")

def sanitize_cookie_for_selenium(cookie: Dict) -> Dict:
    """
    Selenium's add_cookie expects a dict with:
    {'name': ..., 'value': ..., 'domain': (optional), 'path': '/', 'expiry': int (optional), 'secure': True/False}
    Remove invalid keys and correct types.
    """
    valid = {}
    if not isinstance(cookie, dict):
        return valid
    if 'name' not in cookie or 'value' not in cookie:
        return valid
    valid['name'] = cookie['name']
    valid['value'] = cookie['value']
    for key in ['domain', 'path', 'secure', 'expiry', 'httpOnly']:
        if key in cookie:
            if key == 'expiry':
                try:
                    valid['expiry'] = int(cookie[key])
                except:
                    continue
            else:
                valid[key] = cookie[key]
    if 'path' not in valid:
        valid['path'] = '/'
    return valid

def sanitize_and_load_cookies(driver, cookies_file_path: str) -> bool:
    """
    Read cookie file, sanitize cookies, load into current driver session.
    Returns True if cookies likely logged in, False otherwise.
    """
    if not os.path.exists(cookies_file_path):
        logger.info("No cookies file found at %s", cookies_file_path)
        return False

    try:
        with open(cookies_file_path, "r") as f:
            cookies = json.load(f)
        logger.info("Navigating to site root to set cookies")
        driver.get("https://www.naukri.com")
        time.sleep(2)

        loaded_any = False
        for c in cookies:
            try:
                sanitized = sanitize_cookie_for_selenium(c)
                if not sanitized:
                    continue
                if 'domain' in sanitized:
                    sanitized['domain'] = sanitized['domain'].lstrip('.')
                try:
                    driver.add_cookie(sanitized)
                    loaded_any = True
                except Exception as e:
                    logger.debug(f"add_cookie failed for {sanitized.get('name')}: {e}")
                    try:
                        temp = dict(sanitized)
                        if 'domain' in temp: temp.pop('domain')
                        driver.add_cookie(temp)
                        loaded_any = True
                    except Exception as e2:
                        logger.debug(f"add_cookie fallback also failed: {e2}")
                        continue
            except Exception as e:
                logger.debug(f"Sanitize/load cookie error: {e}")
                continue

        if not loaded_any:
            logger.warning("No cookies were loaded (all failed).")
            return False

        driver.refresh()
        time.sleep(3)

        current_url = driver.current_url.lower()
        if "nlogin" not in current_url and "login" not in current_url:
            logger.info("Cookies loaded and URL does not indicate login page: %s", current_url)
            return True

        try:
            from selenium.webdriver.common.by import By
            elements = driver.find_elements(By.XPATH, "//a[contains(@href,'mnjuser') or contains(@href,'myHome') or contains(@href,'logout')]")
            if elements:
                logger.info("Dashboard elements found after loading cookies")
                return True
        except Exception:
            pass

        logger.warning("Cookies loaded, but user not recognized (may be expired).")
        return False
    except Exception as e:
        logger.warning(f"Failed to read or apply cookies: {e}")
        return False
