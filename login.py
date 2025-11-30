# login.py
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.logger import setup_logger
logger = setup_logger(__name__)

def login_to_naukri(driver, timeout=30):
    """
    Try interactive login (email/password) on Naukri.
    Returns True on success, False otherwise.
    """
    try:
        logger.info("Navigating to Naukri login page...")
        driver.get("https://www.naukri.com/nlogin/login")
        wait = WebDriverWait(driver, timeout)

        # Detect immediate Access Denied
        title = (driver.title or "").lower()
        page_text = ""
        try:
            page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        except Exception:
            page_text = ""

        if "access denied" in title or "access denied" in page_text:
            logger.error("Access Denied detected on arrival. Page title/summary: %s", title)
            return False

        # Wait for email input to appear
        try:
            email_el = wait.until(EC.presence_of_element_located((By.ID, "email")))
        except Exception:
            try:
                email_el = driver.find_element(By.XPATH, "//input[contains(@placeholder,'Email') or contains(@name,'email')]")
            except Exception as e:
                logger.error("Email input not found: %s", e)
                try:
                    logger.error("Page snapshot (first 400 chars): %s", driver.page_source[:400])
                except:
                    pass
                return False

        import os
        email = os.getenv("NAUKRI_EMAIL")
        password = os.getenv("NAUKRI_PASSWORD")
        if not email or not password:
            logger.error("NAUKRI_EMAIL or NAUKRI_PASSWORD environment variables missing.")
            return False

        try:
            email_el.clear()
            email_el.send_keys(email)
        except Exception:
            try:
                email_el.send_keys(email)
            except:
                pass

        try:
            pwd_el = driver.find_element(By.ID, "password")
        except Exception:
            try:
                pwd_el = driver.find_element(By.XPATH, "//input[@type='password' or contains(@placeholder,'Password')]")
            except Exception as e:
                logger.error("Password input not found: %s", e)
                return False

        try:
            pwd_el.clear()
            pwd_el.send_keys(password)
        except Exception:
            pwd_el.send_keys(password)

        # Submit login
        try:
            login_btn = driver.find_element(By.XPATH, "//button[contains(.,'Login') or contains(.,'Sign in') or @type='submit']")
            login_btn.click()
        except Exception:
            try:
                pwd_el.send_keys("\n")
            except:
                pass

        # Wait for either dashboard or OTP prompt or error
        time.sleep(2)
        try:
            for _ in range(int(timeout / 1)):
                time.sleep(1)
                current_url = driver.current_url.lower()
                if "nlogin" not in current_url and "login" not in current_url:
                    logger.info("URL changed after login attempt: %s", current_url)
                    return True
                body_text = ""
                try:
                    body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
                except:
                    body_text = ""
                if "otp" in body_text or "one time" in body_text or "verification code" in body_text or "enter the code" in body_text:
                    logger.warning("OTP / verification required - interactive manual input needed.")
                    return False
                if "access denied" in body_text:
                    logger.error("Access denied detected after login submission.")
                    return False
            logger.warning("Timed out waiting for post-login page state.")
            return False
        except Exception as e:
            logger.error("Error waiting for login completion: %s", e)
            return False
    except Exception as e:
        logger.error(f"Exception in login_to_naukri: {e}", exc_info=True)
        return False
