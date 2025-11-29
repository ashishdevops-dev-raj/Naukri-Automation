"""
Helper Functions
Utility functions for common operations
"""

import os
import time
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

try:
    from config import Config
    from utils.logger import setup_logger
    logger = setup_logger(__name__)
except ImportError:
    import logging
    import os
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    # Create minimal Config if import fails
    class Config:
        SCREENSHOT_DIR = os.getenv("SCREENSHOT_DIR", "screenshots")
except Exception:
    import logging
    import os
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    class Config:
        SCREENSHOT_DIR = os.getenv("SCREENSHOT_DIR", "screenshots")


def handle_popups(driver, max_attempts=3):
    """
    Handle various popups that may appear on Naukri
    
    Args:
        driver: Selenium WebDriver instance
        max_attempts: Maximum number of popup handling attempts
    """
    popup_selectors = [
        "//button[contains(@class, 'close')]",
        "//span[contains(@class, 'close')]",
        "//div[contains(@class, 'modal')]//button[contains(@class, 'close')]",
        "//a[contains(@class, 'close')]",
        "//button[contains(text(), 'Close')]",
        "//button[contains(text(), '×')]",
        "//span[contains(text(), '×')]",
    ]
    
    for attempt in range(max_attempts):
        for selector in popup_selectors:
            try:
                popup = driver.find_element(By.XPATH, selector)
                if popup.is_displayed():
                    popup.click()
                    logger.info(f"Closed popup using selector: {selector}")
                    time.sleep(1)
                    break
            except (NoSuchElementException, Exception):
                continue
        else:
            # No popup found, break
            break


def take_screenshot(driver, filename):
    """
    Take a screenshot and save it
    
    Args:
        driver: Selenium WebDriver instance
        filename: Name for the screenshot file (without extension)
    """
    try:
        # Create screenshots directory if it doesn't exist
        os.makedirs(Config.SCREENSHOT_DIR, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(Config.SCREENSHOT_DIR, f"{filename}_{timestamp}.png")
        
        driver.save_screenshot(filepath)
        logger.info(f"Screenshot saved: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Failed to take screenshot: {str(e)}")
        return None


def cleanup_driver(driver):
    """
    Clean up and close WebDriver
    
    Args:
        driver: Selenium WebDriver instance
    """
    try:
        driver.quit()
        logger.info("WebDriver closed successfully")
    except Exception as e:
        logger.error(f"Error closing WebDriver: {str(e)}")