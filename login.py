"""
Naukri Login Module
Handles secure login using environment variables
"""

import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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
        
        # Wait a bit more for page to fully load
        time.sleep(3)
        
        # Check if we got blocked
        page_title = driver.title
        page_source = driver.page_source.lower()
        
        if "Access Denied" in page_title or "blocked" in page_title.lower() or "forbidden" in page_title.lower():
            logger.error(f"Access Denied! Page title: {page_title}")
            logger.error("Naukri is blocking automated access. This might be due to:")
            logger.error("1. Bot detection (headless browser detected)")
            logger.error("2. IP-based blocking")
            logger.error("3. Rate limiting")
            logger.error("Attempting to bypass with additional stealth measures...")
            
            # Try to navigate again with a delay
            time.sleep(5)
            try:
                driver.delete_all_cookies()
                driver.get("https://www.naukri.com")
                time.sleep(3)
                driver.get("https://www.naukri.com/nlogin/login")
                time.sleep(5)
                
                # Check again
                page_title_retry = driver.title
                if "Access Denied" not in page_title_retry and "blocked" not in page_title_retry.lower():
                    logger.info("Successfully bypassed access denied on retry")
                else:
                    logger.error("Still blocked after retry. Consider using cookies or running locally first.")
                    return False
            except Exception as e:
                logger.error(f"Retry failed: {e}")
                return False
        
        # Also check page source for blocking messages
        if "access denied" in page_source or "blocked" in page_source or "forbidden" in page_source:
            logger.warning("Detected blocking message in page source, but continuing...")
        
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
        # Fill email field with proper events
        email_field.clear()
        if Config is None:
            raise ImportError("Config module not available")
        
        # Click on field first to focus
        email_field.click()
        time.sleep(0.5)
        
        # Type email character by character to simulate human typing
        email = Config.NAUKRI_EMAIL
        for char in email:
            email_field.send_keys(char)
            time.sleep(0.05)  # Small delay between characters
        
        # Trigger input events
        driver.execute_script("arguments[0].dispatchEvent(new Event('input', {bubbles: true}));", email_field)
        driver.execute_script("arguments[0].dispatchEvent(new Event('change', {bubbles: true}));", email_field)
        time.sleep(1)
        
        logger.info(f"Email entered: {email[:3]}***{email[-5:]}")
        
        # Find and fill password - try multiple selectors (simplified approach)
        logger.info("Entering password...")
        password_field = None
        password_selectors = [
            (By.XPATH, "//input[@placeholder='Enter Password']"),  # Try this first (matches working code)
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
        
        # Fill password field - simpler approach that works locally
        password = Config.NAUKRI_PASSWORD
        password_field.clear()
        password_field.send_keys(password)
        
        # Try submitting with Keys.RETURN first (simpler and works better)
        logger.info("Submitting login form with Enter key...")
        try:
            password_field.send_keys(Keys.RETURN)
            logger.info("Login submitted using Enter key")
            time.sleep(3)
            
            # Check if login was successful by checking URL
            current_url = driver.current_url
            if "nlogin" not in current_url and "login" not in current_url.lower():
                logger.info("Login successful - URL changed!")
                return True
            
            # Also check for dashboard elements
            try:
                wait.until(EC.url_contains("naukri.com"))
                # Additional check - make sure we're not on login page
                if "nlogin" not in driver.current_url and "login" not in driver.current_url.lower():
                    logger.info("Login successful - verified with URL check!")
                    return True
            except:
                pass
        except Exception as e:
            logger.warning(f"Enter key submission failed: {e}, trying button click...")
        
        logger.info("Password entered, will try button click method...")
        
        # Check for "Remember this device" or "Trust this device" checkbox BEFORE submitting
        # This might help bypass OTP requirement
        logger.info("Checking for 'Remember this device' or 'Trust this device' checkbox...")
        remember_checkbox = None
        remember_selectors = [
            (By.XPATH, "//input[@type='checkbox' and contains(@id, 'remember')]"),
            (By.XPATH, "//input[@type='checkbox' and contains(@name, 'remember')]"),
            (By.XPATH, "//input[@type='checkbox' and contains(@class, 'remember')]"),
            (By.XPATH, "//input[@type='checkbox' and contains(@id, 'trust')]"),
            (By.XPATH, "//input[@type='checkbox' and contains(@name, 'trust')]"),
            (By.XPATH, "//input[@type='checkbox' and contains(@class, 'trust')]"),
            (By.XPATH, "//input[@type='checkbox' and contains(@id, 'device')]"),
            (By.XPATH, "//input[@type='checkbox' and contains(@name, 'device')]"),
            (By.XPATH, "//label[contains(text(), 'Remember')]/input[@type='checkbox']"),
            (By.XPATH, "//label[contains(text(), 'Trust')]/input[@type='checkbox']"),
            (By.XPATH, "//label[contains(text(), 'remember')]/input[@type='checkbox']"),
            (By.XPATH, "//label[contains(text(), 'trust')]/input[@type='checkbox']"),
            (By.XPATH, "//input[@type='checkbox' and following-sibling::text()[contains(., 'Remember')]]"),
            (By.XPATH, "//input[@type='checkbox' and following-sibling::text()[contains(., 'Trust')]]"),
            (By.XPATH, "//input[@type='checkbox' and preceding-sibling::text()[contains(., 'Remember')]]"),
            (By.XPATH, "//input[@type='checkbox' and preceding-sibling::text()[contains(., 'Trust')]]"),
        ]
        
        for selector_type, selector_value in remember_selectors:
            try:
                checkboxes = driver.find_elements(selector_type, selector_value)
                for checkbox in checkboxes:
                    if checkbox.is_displayed():
                        remember_checkbox = checkbox
                        logger.info(f"Found remember/trust checkbox: {selector_type}={selector_value}")
                        break
                if remember_checkbox:
                    break
            except:
                continue
        
        if remember_checkbox:
            try:
                # Check if it's already checked
                if not remember_checkbox.is_selected():
                    logger.info("Checking 'Remember this device' checkbox...")
                    # Scroll into view
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", remember_checkbox)
                    time.sleep(0.5)
                    # Click the checkbox
                    remember_checkbox.click()
                    time.sleep(1)
                    logger.info("Remember device checkbox checked successfully")
                else:
                    logger.info("Remember device checkbox already checked")
            except Exception as e:
                logger.warning(f"Could not check remember device checkbox: {e}")
        else:
            logger.info("No 'Remember this device' checkbox found on login form")
        
        # Check if form is valid before submitting
        try:
            form_valid = driver.execute_script("""
                var form = arguments[0].closest('form');
                if (form) {
                    return form.checkValidity();
                }
                return true;
            """, password_field)
            logger.info(f"Form validity check: {form_valid}")
        except:
            pass
        
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
        
        # Wait a bit for any validation to complete
        time.sleep(2)
        
        # Method 1: Try clicking the button with multiple approaches
        submission_success = False
        try:
            # Scroll to button to ensure it's visible
            driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", login_button)
            time.sleep(1)
            
            # Check if button is actually clickable
            if login_button.is_displayed() and login_button.is_enabled():
                logger.info("Button is visible and enabled, trying click...")
                # Try regular click
                try:
                    login_button.click()
                    submission_success = True
                    logger.info("Regular click succeeded")
                except Exception as e:
                    logger.warning(f"Regular click failed: {e}, trying JavaScript click...")
                    # Try JavaScript click
                    try:
                        driver.execute_script("arguments[0].click();", login_button)
                        submission_success = True
                        logger.info("JavaScript click succeeded")
                    except Exception as e2:
                        logger.warning(f"JavaScript click failed: {e2}")
            else:
                logger.warning("Button not clickable, trying JavaScript click...")
                driver.execute_script("arguments[0].click();", login_button)
                submission_success = True
        except Exception as e:
            logger.warning(f"Button click failed: {e}")
        
        # Method 2: If button click didn't work, try form submit
        if not submission_success:
            try:
                logger.info("Trying form submit...")
                form = password_field.find_element(By.XPATH, "./ancestor::form")
                driver.execute_script("arguments[0].submit();", form)
                submission_success = True
                logger.info("Form submit succeeded")
            except Exception as e:
                logger.warning(f"Form submit failed: {e}")
        
        # Method 3: Try pressing Enter on password field
        if not submission_success:
            try:
                logger.info("Trying Enter key on password field...")
                password_field.send_keys(Keys.RETURN)
                submission_success = True
                logger.info("Enter key succeeded")
            except Exception as e:
                logger.warning(f"Enter key method failed: {e}")
        
        if not submission_success:
            logger.error("All submission methods failed!")
            return False
        
        # Wait for navigation or error message
        logger.info("Waiting for login to process...")
        
        # Wait and check multiple times for URL change or errors
        max_wait_time = 10
        check_interval = 1
        waited = 0
        url_changed = False
        error_found = False
        error_messages = []
        
        while waited < max_wait_time:
            time.sleep(check_interval)
            waited += check_interval
            
            current_url = driver.current_url
            logger.info(f"Checking after {waited}s - URL: {current_url}")
            
            # Check if URL changed (login successful)
            if "nlogin" not in current_url and "login" not in current_url.lower():
                url_changed = True
                logger.info("URL changed - login likely successful!")
                break
            
            # Check for error messages
            error_selectors = [
                "//div[contains(@class, 'error')]",
                "//span[contains(@class, 'error')]",
                "//div[contains(@class, 'alert')]",
                "//div[contains(@class, 'warning')]",
                "//div[contains(@class, 'message')]",
                "//span[contains(@class, 'message')]",
                "//div[contains(@class, 'invalid')]",
                "//span[contains(@class, 'invalid')]",
                "//*[contains(@id, 'error')]",
                "//*[contains(@id, 'Error')]",
                "//*[contains(@class, 'error-msg')]",
                "//*[contains(@class, 'errorMsg')]",
                "//*[contains(@class, 'errormsg')]",
            ]
            
            for error_selector in error_selectors:
                try:
                    error_elems = driver.find_elements(By.XPATH, error_selector)
                    for error_elem in error_elems:
                        try:
                            if error_elem.is_displayed():
                                error_text = error_elem.text.strip()
                                if error_text and len(error_text) > 0 and error_text not in error_messages:
                                    error_messages.append(error_text)
                                    logger.error(f"Login error detected: {error_text}")
                                    error_found = True
                        except:
                            continue
                except:
                    continue
            
            # Check page text for error keywords
            try:
                page_text = driver.find_element(By.TAG_NAME, "body").text
                page_text_lower = page_text.lower()
                error_keywords = [
                    'invalid email', 'invalid password', 'incorrect', 'wrong password', 
                    'wrong email', 'login failed', 'authentication failed', 'invalid credentials',
                    'please enter valid', 'try again', 'account locked', 'suspended'
                ]
                for keyword in error_keywords:
                    if keyword in page_text_lower:
                        # Extract the error message
                        lines = page_text.split('\n')
                        for line in lines:
                            if keyword in line.lower():
                                if line.strip() not in error_messages:
                                    error_messages.append(line.strip())
                                    logger.error(f"Error keyword found: '{line.strip()}'")
                                    error_found = True
                        break
            except:
                pass
            
            if error_found:
                break
        
        if error_found:
            logger.error(f"Login failed with errors: {error_messages}")
            # Log all visible text on the page for debugging
            try:
                page_text = driver.find_element(By.TAG_NAME, "body").text
                logger.error("Page content after login attempt:")
                logger.error(page_text[:500])  # First 500 chars
            except:
                pass
            return False
        
        # Check for CAPTCHA
        try:
            captcha_elements = driver.find_elements(By.XPATH, "//*[contains(@class, 'captcha') or contains(@id, 'captcha') or contains(text(), 'CAPTCHA') or contains(text(), 'captcha')]")
            if captcha_elements:
                for cap in captcha_elements:
                    if cap.is_displayed():
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
        
        # If URL already changed, we're good
        if url_changed:
            logger.info("Login successful - URL changed!")
            return True
        
        # Check current URL
        current_url_after = driver.current_url
        logger.info(f"Final URL after login attempt: {current_url_after}")
        
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
                (By.XPATH, "//a[contains(@href, 'mnjuser')]"),  # Naukri user menu
                (By.XPATH, "//*[contains(@class, 'userProfile')]"),
            ]
            
            for selector_type, selector_value in dashboard_selectors:
                try:
                    short_wait = WebDriverWait(driver, 3)
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
                # Get page source to see what's there
                try:
                    page_text = driver.find_element(By.TAG_NAME, "body").text
                    page_text_lower = page_text.lower()
                    
                    # Check for OTP requirement
                    if "otp" in page_text_lower or "enter the otp" in page_text_lower or "verify" in page_text_lower:
                        logger.warning("OTP (One-Time Password) verification required!")
                        logger.info("Credentials are correct, but Naukri requires OTP verification")
                        
                        # Wait a bit more for the OTP page to fully load
                        logger.info("Waiting for OTP page to fully load...")
                        time.sleep(3)
                        
                        # Refresh page content after wait
                        try:
                            page_text = driver.find_element(By.TAG_NAME, "body").text
                            page_text_lower = page_text.lower()
                        except:
                            pass
                        
                        # First, try to find and click "Skip" or "Remember this device" options
                        # Also check for links/buttons that might allow bypassing OTP
                        skip_options = [
                            (By.XPATH, "//a[contains(text(), 'Skip')]"),
                            (By.XPATH, "//button[contains(text(), 'Skip')]"),
                            (By.XPATH, "//a[contains(text(), 'skip')]"),
                            (By.XPATH, "//button[contains(text(), 'skip')]"),
                            (By.XPATH, "//a[contains(text(), 'Later')]"),
                            (By.XPATH, "//button[contains(text(), 'Later')]"),
                            (By.XPATH, "//a[contains(text(), 'Remember')]"),
                            (By.XPATH, "//button[contains(text(), 'Remember')]"),
                            (By.XPATH, "//a[contains(text(), 'Trust')]"),
                            (By.XPATH, "//button[contains(text(), 'Trust')]"),
                            (By.XPATH, "//a[contains(text(), 'Not Now')]"),
                            (By.XPATH, "//button[contains(text(), 'Not Now')]"),
                            (By.XPATH, "//*[contains(@class, 'skip')]"),
                            (By.XPATH, "//*[contains(@id, 'skip')]"),
                            (By.XPATH, "//*[contains(@class, 'later')]"),
                            (By.XPATH, "//*[contains(@id, 'later')]"),
                            (By.CSS_SELECTOR, "a[href*='skip']"),
                            (By.CSS_SELECTOR, "button[class*='skip']"),
                        ]
                        
                        skip_clicked = False
                        for selector_type, selector_value in skip_options:
                            try:
                                skip_elems = driver.find_elements(selector_type, selector_value)
                                for elem in skip_elems:
                                    try:
                                        if elem.is_displayed() and elem.is_enabled():
                                            elem_text = elem.text.lower()
                                            logger.info(f"Found potential skip option: '{elem_text}' ({selector_type}={selector_value}), clicking...")
                                            # Scroll into view
                                            driver.execute_script("arguments[0].scrollIntoView(true);", elem)
                                            time.sleep(0.5)
                                            elem.click()
                                            time.sleep(3)
                                            skip_clicked = True
                                            
                                            # Check if we're logged in now
                                            final_url = driver.current_url
                                            page_title = driver.title
                                            logger.info(f"After skip click - URL: {final_url}, Title: {page_title}")
                                            
                                            if "nlogin" not in final_url and "login" not in final_url.lower():
                                                logger.info("Skipped OTP successfully - logged in!")
                                                return True
                                            
                                            # Also check page content to see if OTP requirement is gone
                                            try:
                                                new_page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
                                                if "otp" not in new_page_text or "enter the otp" not in new_page_text:
                                                    logger.info("OTP requirement seems to be gone, checking login status...")
                                                    time.sleep(2)
                                                    final_url = driver.current_url
                                                    if "nlogin" not in final_url and "login" not in final_url.lower():
                                                        logger.info("Login successful after skipping OTP!")
                                                        return True
                                            except:
                                                pass
                                            break
                                    except Exception as e:
                                        logger.debug(f"Error clicking skip element: {e}")
                                        continue
                            except Exception as e:
                                logger.debug(f"Error finding skip element {selector_value}: {e}")
                                continue
                        
                        if skip_clicked:
                            logger.info("Skip option was clicked, but login status unclear. Waiting and rechecking...")
                            time.sleep(5)
                            final_url = driver.current_url
                            page_title = driver.title
                            logger.info(f"Final check - URL: {final_url}, Title: {page_title}")
                            
                            # Check if we're actually logged in by looking for dashboard elements
                            try:
                                dashboard_indicators = [
                                    "//a[contains(@href, '/mnjuser/homepage')]",
                                    "//a[contains(@href, '/myNaukri')]",
                                    "//*[contains(text(), 'My Naukri')]",
                                    "//*[contains(text(), 'Profile')]",
                                ]
                                for indicator in dashboard_indicators:
                                    try:
                                        elem = driver.find_element(By.XPATH, indicator)
                                        if elem.is_displayed():
                                            logger.info("Found dashboard indicator - login successful!")
                                            return True
                                    except:
                                        continue
                            except:
                                pass
                            
                            if "nlogin" not in final_url and "login" not in final_url.lower():
                                logger.info("Login successful after skipping OTP!")
                                return True
                        
                        # Log all clickable elements on the page for debugging
                        logger.info("Logging all clickable elements on OTP page for debugging...")
                        try:
                            all_links = driver.find_elements(By.TAG_NAME, "a")
                            all_buttons = driver.find_elements(By.TAG_NAME, "button")
                            all_clickables = driver.find_elements(By.XPATH, "//*[@onclick or @role='button' or contains(@class, 'btn') or contains(@class, 'link')]")
                            
                            logger.info(f"Found {len(all_links)} links, {len(all_buttons)} buttons, {len(all_clickables)} clickable elements")
                            
                            # Log visible clickable elements
                            visible_elements = []
                            for elem in all_links + all_buttons + all_clickables:
                                try:
                                    if elem.is_displayed() and elem.text.strip():
                                        visible_elements.append(f"  - {elem.tag_name}: '{elem.text.strip()}' (id={elem.get_attribute('id')}, class={elem.get_attribute('class')})")
                                except:
                                    pass
                            
                            if visible_elements:
                                logger.info("Visible clickable elements on OTP page:")
                                for elem_info in visible_elements[:20]:  # Show first 20
                                    logger.info(elem_info)
                        except Exception as e:
                            logger.debug(f"Error logging clickable elements: {e}")
                        
                        logger.info("No skip option found, attempting to handle OTP...")
                        
                        # Try to find OTP input field
                        otp_field = None
                        otp_selectors = [
                            (By.XPATH, "//input[@type='text' and contains(@placeholder, 'OTP')]"),
                            (By.XPATH, "//input[@type='text' and contains(@placeholder, 'otp')]"),
                            (By.XPATH, "//input[@type='text' and contains(@placeholder, 'Enter')]"),
                            (By.XPATH, "//input[@type='number']"),
                            (By.XPATH, "//input[contains(@class, 'otp')]"),
                            (By.XPATH, "//input[contains(@id, 'otp')]"),
                            (By.XPATH, "//input[contains(@name, 'otp')]"),
                        ]
                        
                        for selector_type, selector_value in otp_selectors:
                            try:
                                otp_field = driver.find_element(selector_type, selector_value)
                                if otp_field.is_displayed():
                                    logger.info(f"Found OTP field: {selector_type}={selector_value}")
                                    break
                            except:
                                continue
                        
                        # Check if OTP is provided via environment variable
                        if Config is None:
                            otp_code = os.getenv("NAUKRI_OTP", "")
                        else:
                            otp_code = Config.NAUKRI_OTP
                        
                        if otp_code and otp_field:
                            logger.info("OTP code provided via environment variable, entering...")
                            otp_field.clear()
                            otp_field.send_keys(otp_code)
                            time.sleep(1)
                            
                            # Find and click verify button
                            verify_selectors = [
                                (By.XPATH, "//button[contains(text(), 'Verify')]"),
                                (By.XPATH, "//button[contains(text(), 'Submit')]"),
                                (By.XPATH, "//button[@type='submit']"),
                            ]
                            
                            for selector_type, selector_value in verify_selectors:
                                try:
                                    verify_button = driver.find_element(selector_type, selector_value)
                                    if verify_button.is_displayed() and verify_button.is_enabled():
                                        verify_button.click()
                                        logger.info("OTP verification submitted")
                                        time.sleep(5)
                                        
                                        # Check if verification succeeded
                                        final_url = driver.current_url
                                        if "nlogin" not in final_url and "login" not in final_url.lower():
                                            logger.info("OTP verification successful!")
                                            return True
                                        break
                                except:
                                    continue
                            
                            logger.warning("OTP verification may have failed or is still processing")
                        else:
                            logger.error("OTP required but not provided!")
                            logger.error("To enable OTP handling, set NAUKRI_OTP environment variable")
                            logger.error("Note: OTP is sent to your email and expires quickly")
                            return False
                    
                    # Check for specific error patterns
                    elif "invalid" in page_text_lower or "incorrect" in page_text_lower:
                        logger.error("ERROR: Credentials appear to be incorrect!")
                    elif "captcha" in page_text_lower:
                        logger.error("ERROR: CAPTCHA required!")
                    elif "blocked" in page_text_lower or "suspended" in page_text_lower:
                        logger.error("ERROR: Account might be blocked or suspended!")
                    else:
                        logger.error("ERROR: Unknown login failure reason")
                        logger.error("Page content when login failed:")
                        logger.error(page_text[:1000])  # First 1000 chars for debugging
                except Exception as e:
                    logger.error(f"Error getting page content: {e}")
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