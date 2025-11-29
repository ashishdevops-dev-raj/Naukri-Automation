"""
Naukri Login Module
Handles secure login using environment variables
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from config import Config
from utils.logger import setup_logger
from utils.helpers import handle_popups

try:
    logger = setup_logger(__name__)
except Exception:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


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
        
        # Wait for login form to load
        wait = WebDriverWait(driver, 20)
        
        # Find and fill email
        logger.info("Entering email...")
        email_field = wait.until(
            EC.presence_of_element_located((By.ID, "usernameField"))
        )
        email_field.clear()
        email_field.send_keys(Config.NAUKRI_EMAIL)
        
        # Find and fill password
        logger.info("Entering password...")
        password_field = driver.find_element(By.ID, "passwordField")
        password_field.clear()
        password_field.send_keys(Config.NAUKRI_PASSWORD)
        
        # Click login button
        logger.info("Clicking login button...")
        login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
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