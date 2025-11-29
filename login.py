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
        
        # Check if we got blocked
        page_title = driver.title
        if "Access Denied" in page_title or "blocked" in page_title.lower() or "forbidden" in page_title.lower():
            logger.error(f"Access Denied! Page title: {page_title}")
            logger.error("Naukri is blocking automated access. This might be due to:")
            logger.error("1. Bot detection (headless browser detected)")
            logger.error("2. IP-based blocking")
            logger.error("3. Rate limiting")
            logger.error("Consider running locally with a visible browser or using a proxy/VPN")
            return False
        
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
        
        # Double-check we're not blocked after page load
        page_title_after = driver.title
        if "Access Denied" in page_title_after or "blocked" in page_title_after.lower():
            logger.error(f"Access Denied detected after page load! Page title: {page_title_after}")
            return False
        
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
        
        for i, (selector_type, selector_value) in enumerate(email_selectors):
            try:
                logger.info(f"Trying selector {i+1}/{len(email_selectors)}: {selector_type}={selector_value}")
                # Try with shorter timeout per selector to avoid hanging
                short_wait = WebDriverWait(driver, 5)
                # Try visibility check first (more reliable)
                email_field = short_wait.until(
                    EC.visibility_of_element_located((selector_type, selector_value))
                )
                logger.info(f"Found email field using {selector_type}: {selector_value}")
                break
            except TimeoutException:
                try:
                    # Fallback to presence check
                    email_field = short_wait.until(
                        EC.presence_of_element_located((selector_type, selector_value))
                    )
                    logger.info(f"Found email field (presence) using {selector_type}: {selector_value}")
                    break
                except TimeoutException:
                    logger.debug(f"Selector {selector_type}={selector_value} failed, trying next...")
                    continue
        
        if email_field is None:
            logger.error("Could not find email field with any selector")
            logger.error(f"Page title: {driver.title}")
            logger.error(f"Page URL: {driver.current_url}")
            
            # Check for iframes
            try:
                iframes = driver.find_elements(By.TAG_NAME, "iframe")
                logger.error(f"Found {len(iframes)} iframes on page")
                if iframes:
                    logger.error("Page contains iframes - email field might be inside an iframe")
            except:
                pass
            
            # Try to find any input fields for debugging
            try:
                all_inputs = driver.find_elements(By.TAG_NAME, "input")
                logger.error(f"Found {len(all_inputs)} input elements on page")
                for i, inp in enumerate(all_inputs[:10]):  # Show first 10
                    try:
                        inp_id = inp.get_attribute('id') or 'None'
                        inp_name = inp.get_attribute('name') or 'None'
                        inp_type = inp.get_attribute('type') or 'None'
                        inp_placeholder = inp.get_attribute('placeholder') or 'None'
                        inp_class = inp.get_attribute('class') or 'None'
                        logger.error(f"  Input {i}: id={inp_id}, name={inp_name}, type={inp_type}, placeholder={inp_placeholder}, class={inp_class[:50]}")
                    except Exception as e:
                        logger.error(f"  Input {i}: Error getting attributes - {e}")
            except Exception as e:
                logger.error(f"Error finding inputs: {e}")
            
            # Try to get page source snippet for debugging
            try:
                page_source = driver.page_source
                if 'usernameField' in page_source or 'username' in page_source.lower():
                    logger.error("Page source contains 'usernameField' or 'username' - element might be hidden or in iframe")
                else:
                    logger.error("Page source does NOT contain 'usernameField' or 'username' - page structure might have changed")
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
        
        # Try multiple methods to submit the form
        logger.info("Submitting login form...")
        
        # Method 1: Try pressing Enter on password field
        try:
            logger.info("Trying Enter key on password field...")
            password_field.send_keys(Keys.RETURN)
            time.sleep(3)
        except Exception as e:
            logger.warning(f"Enter key method failed: {e}")
        
        # Method 2: Try clicking the button
        try:
            # Scroll to button to ensure it's visible
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", login_button)
            time.sleep(1)
            
            # Check if button is actually clickable
            if login_button.is_displayed() and login_button.is_enabled():
                logger.info("Button is visible and enabled, clicking...")
                login_button.click()
            else:
                logger.warning("Button not clickable, trying JavaScript click...")
                driver.execute_script("arguments[0].click();", login_button)
        except Exception as e:
            logger.warning(f"Button click failed: {e}, trying form submit...")
            # Method 3: Try submitting the form directly
            try:
                form = password_field.find_element(By.XPATH, "./ancestor::form")
                driver.execute_script("arguments[0].submit();", form)
            except:
                logger.warning("Form submit also failed")
        
        # Wait for navigation or error message
        logger.info("Waiting for login to process...")
        time.sleep(5)  # Increased wait time
        
        # Check for error messages first - be more thorough
        error_found = False
        error_messages = []
        
        error_selectors = [
            "//div[contains(@class, 'error')]",
            "//span[contains(@class, 'error')]",
            "//div[contains(@class, 'alert')]",
            "//div[contains(@class, 'warning')]",
            "//div[contains(@class, 'message')]",
            "//span[contains(@class, 'message')]",
            "//div[contains(text(), 'Invalid')]",
            "//div[contains(text(), 'incorrect')]",
            "//div[contains(text(), 'wrong')]",
            "//div[contains(text(), 'failed')]",
            "//div[contains(text(), 'error')]",
            "//*[contains(@id, 'error')]",
            "//*[contains(@class, 'invalid')]",
        ]
        
        for error_selector in error_selectors:
            try:
                error_elems = driver.find_elements(By.XPATH, error_selector)
                for error_elem in error_elems:
                    try:
                        error_text = error_elem.text.strip()
                        if error_text and len(error_text) > 0:
                            error_messages.append(error_text)
                            logger.error(f"Login error detected: {error_text}")
                            error_found = True
                    except:
                        continue
            except:
                continue
        
        # Also check page source for common error keywords
        try:
            page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
            error_keywords = ['invalid', 'incorrect', 'wrong password', 'wrong email', 'login failed', 'authentication failed']
            for keyword in error_keywords:
                if keyword in page_text:
                    logger.error(f"Error keyword found in page: '{keyword}'")
                    error_found = True
                    break
        except:
            pass
        
        if error_found:
            logger.error(f"Login failed with errors: {error_messages}")
            return False
        
        # Check for CAPTCHA
        try:
            captcha_elements = driver.find_elements(By.XPATH, "//*[contains(@class, 'captcha') or contains(@id, 'captcha') or contains(text(), 'CAPTCHA')]")
            if captcha_elements:
                logger.error("CAPTCHA detected! Manual intervention required.")
                return False
        except:
            pass
        
        # Handle any popups that appear after login
        logger.info("Checking for popups...")
        handle_popups(driver)
        time.sleep(2)
        
        # Wait longer for navigation
        time.sleep(3)
        
        # Check current URL
        current_url_after = driver.current_url
        logger.info(f"URL after login attempt: {current_url_after}")
        
        # Verify login success by checking for dashboard elements or URL change
        login_success = False
        
        # Check if URL changed (not on login page anymore)
        if "nlogin" not in current_url_after and "login" not in current_url_after.lower():
            logger.info("URL changed - likely logged in successfully")
            login_success = True
        else:
            # Try to find dashboard elements
            dashboard_selectors = [
                (By.XPATH, "//a[contains(@href, 'myHome')]"),
                (By.XPATH, "//a[contains(@href, 'dashboard')]"),
                (By.XPATH, "//a[contains(text(), 'My Profile')]"),
                (By.XPATH, "//a[contains(text(), 'Profile')]"),
                (By.XPATH, "//div[contains(@class, 'dashboard')]"),
            ]
            
            for selector_type, selector_value in dashboard_selectors:
                try:
                    short_wait = WebDriverWait(driver, 5)
                    short_wait.until(
                        EC.presence_of_element_located((selector_type, selector_value))
                    )
                    logger.info(f"Found dashboard element: {selector_type}={selector_value}")
                    login_success = True
                    break
                except TimeoutException:
                    continue
        
        if login_success:
            logger.info("Login verification successful")
            return True
        else:
            # Check if still on login page (login failed)
            if "nlogin" in current_url_after or "login" in current_url_after.lower():
                logger.error("Login failed - still on login page")
                # Try to get any error message
                try:
                    page_text = driver.find_element(By.TAG_NAME, "body").text
                    if "invalid" in page_text.lower() or "incorrect" in page_text.lower():
                        logger.error("Credentials might be incorrect")
                except:
                    pass
                return False
            # Might have logged in but different page structure
            logger.warning("Could not verify login, but URL changed - assuming success")
            return True
            
    except TimeoutException as e:
        logger.error(f"Timeout during login: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error during login: {str(e)}", exc_info=True)
        return False