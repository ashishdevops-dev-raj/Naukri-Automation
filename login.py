"""
Naukri Login Module
Handles secure login using environment variables
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

try:
    from config import Config
    from utils.logger import setup_logger
    from utils.helpers import handle_popups
    logger = setup_logger(__name__)
except ImportError as e:
    import logging
    import os
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.warning(f"Import warning: {e}. Using basic logging.")
    # Try to import Config and helpers separately
    try:
        from config import Config
    except ImportError:
        logger.error("Failed to import Config")
        Config = None
    try:
        from utils.helpers import handle_popups
    except ImportError:
        logger.error("Failed to import handle_popups")
        def handle_popups(driver, max_attempts=3):
            pass
except Exception as e:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.error(f"Unexpected error during import: {e}")


def login_to_naukri(driver):
    """
    Login to Naukri.com using credentials from environment variables
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        bool: True if login successful, False otherwise
    """
    try:
        logger.info("Navigating to Naukri login page...")
        driver.get("https://www.naukri.com/nlogin/login")
        
        # Wait for page to fully load (including JavaScript)
        logger.info("Waiting for page to load...")
        time.sleep(5)
        
        # Check current URL
        current_url = driver.current_url
        logger.info(f"Current URL after navigation: {current_url}")
        
        # Handle any initial popups
        handle_popups(driver)
        time.sleep(2)
        
        # Wait for page to be ready
        wait = WebDriverWait(driver, 30)
        
        # Wait for page to be interactive
        try:
            wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
            logger.info("Page loaded completely")
        except:
            logger.warning("Page ready state check failed, continuing anyway")
        
        # Find and fill email - try multiple selectors with visibility check
        logger.info("Entering email...")
        email_field = None
        email_selectors = [
            (By.ID, "usernameField"),
            (By.NAME, "username"),
            (By.XPATH, "//input[@id='usernameField']"),
            (By.XPATH, "//input[@name='username']"),
            (By.XPATH, "//input[@type='text' and contains(@placeholder, 'Email')]"),
            (By.XPATH, "//input[@type='text' and contains(@placeholder, 'email')]"),
            (By.XPATH, "//input[@type='email']"),
            (By.XPATH, "//input[contains(@class, 'username')]"),
            (By.XPATH, "//input[contains(@class, 'email')]"),
            (By.CSS_SELECTOR, "input[type='text'][name='username']"),
            (By.CSS_SELECTOR, "input#usernameField"),
            (By.CSS_SELECTOR, "input[name='username']"),
        ]
        
        for selector_type, selector_value in email_selectors:
            try:
                # Try visibility check first (more reliable)
                email_field = wait.until(
                    EC.visibility_of_element_located((selector_type, selector_value))
                )
                logger.info(f"Found email field using {selector_type}: {selector_value}")
                break
            except TimeoutException:
                try:
                    # Fallback to presence check
                    email_field = wait.until(
                        EC.presence_of_element_located((selector_type, selector_value))
                    )
                    logger.info(f"Found email field (presence) using {selector_type}: {selector_value}")
                    break
                except TimeoutException:
                    continue
        
        if email_field is None:
            logger.error("Could not find email field with any selector")
            logger.error(f"Page title: {driver.title}")
            logger.error(f"Page URL: {driver.current_url}")
            # Try to find any input fields for debugging
            try:
                all_inputs = driver.find_elements(By.TAG_NAME, "input")
                logger.error(f"Found {len(all_inputs)} input elements on page")
                for i, inp in enumerate(all_inputs[:5]):  # Show first 5
                    try:
                        logger.error(f"  Input {i}: type={inp.get_attribute('type')}, id={inp.get_attribute('id')}, name={inp.get_attribute('name')}, placeholder={inp.get_attribute('placeholder')}")
                    except:
                        pass
            except:
                pass
            return False
        email_field.clear()
        if Config is None:
            raise ImportError("Config module not available")
        email_field.send_keys(Config.NAUKRI_EMAIL)
        
        # Find and fill password - try multiple selectors
        logger.info("Entering password...")
        password_field = None
        password_selectors = [
            (By.ID, "passwordField"),
            (By.NAME, "password"),
            (By.XPATH, "//input[@type='password']"),
            (By.CSS_SELECTOR, "input[type='password']"),
        ]
        
        for selector_type, selector_value in password_selectors:
            try:
                password_field = wait.until(
                    EC.presence_of_element_located((selector_type, selector_value))
                )
                logger.info(f"Found password field using {selector_type}: {selector_value}")
                break
            except TimeoutException:
                continue
        
        if password_field is None:
            logger.error("Could not find password field with any selector")
            return False
        
        password_field.clear()
        password_field.send_keys(Config.NAUKRI_PASSWORD)
        
        # Click login button - try multiple selectors
        logger.info("Clicking login button...")
        login_button = None
        login_selectors = [
            (By.XPATH, "//button[contains(text(), 'Login')]"),
            (By.XPATH, "//button[@type='submit']"),
            (By.CSS_SELECTOR, "button[type='submit']"),
            (By.XPATH, "//input[@type='submit']"),
        ]
        
        for selector_type, selector_value in login_selectors:
            try:
                login_button = driver.find_element(selector_type, selector_value)
                if login_button.is_displayed() and login_button.is_enabled():
                    logger.info(f"Found login button using {selector_type}: {selector_value}")
                    break
            except:
                continue
        
        if login_button is None:
            logger.error("Could not find login button")
            return False
        
        login_button.click()
        
        # Wait for navigation after login
        time.sleep(5)
        
        # Handle any popups that appear after login
        logger.info("Checking for popups...")
        handle_popups(driver)
        
        # Verify login success by checking for dashboard elements
        try:
            wait.until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'myHome')]"))
            )
            logger.info("Login verification successful")
            return True
        except TimeoutException:
            # Check if still on login page (login failed)
            if "nlogin" in driver.current_url:
                logger.error("Login failed - still on login page")
                return False
            # Might have logged in but different page structure
            logger.warning("Could not verify login, but URL changed")
            return True
            
    except TimeoutException as e:
        logger.error(f"Timeout during login: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error during login: {str(e)}", exc_info=True)
        return False