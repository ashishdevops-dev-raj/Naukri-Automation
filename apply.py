"""
Auto-Apply Module
Automatically applies to jobs if apply button exists
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

try:
    from config import Config
    from utils.logger import setup_logger
    from utils.helpers import handle_popups, take_screenshot
    logger = setup_logger(__name__)
except ImportError as e:
    import logging
    import os
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.warning(f"Import warning: {e}. Using basic logging.")
    try:
        from config import Config
    except ImportError:
        logger.error("Failed to import Config")
        class Config:
            APPLY_LIMIT = int(os.getenv("APPLY_LIMIT", "5"))
            DELAY_BETWEEN_APPLICATIONS = int(os.getenv("DELAY_BETWEEN_APPLICATIONS", "3"))
            SCREENSHOT_DIR = os.getenv("SCREENSHOT_DIR", "screenshots")
    try:
        from utils.helpers import handle_popups, take_screenshot
    except ImportError:
        logger.error("Failed to import helpers")
        def handle_popups(driver, max_attempts=3):
            pass
        def take_screenshot(driver, filename):
            return None
except Exception as e:
    import logging
    import os
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.error(f"Unexpected error during import: {e}")
    class Config:
        APPLY_LIMIT = int(os.getenv("APPLY_LIMIT", "5"))
        DELAY_BETWEEN_APPLICATIONS = int(os.getenv("DELAY_BETWEEN_APPLICATIONS", "3"))
        SCREENSHOT_DIR = os.getenv("SCREENSHOT_DIR", "screenshots")
    def handle_popups(driver, max_attempts=3):
        pass
    def take_screenshot(driver, filename):
        return None


def apply_to_jobs(driver, job_urls):
    """
    Apply to jobs from the provided list
    
    Args:
        driver: Selenium WebDriver instance
        job_urls: List of job URLs to apply to
        
    Returns:
        int: Number of successful applications
    """
    applied_count = 0
    wait = WebDriverWait(driver, 15)
    
    for idx, job_url in enumerate(job_urls, 1):
        if applied_count >= Config.APPLY_LIMIT:
            logger.info(f"Apply limit ({Config.APPLY_LIMIT}) reached. Stopping...")
            break
        
        try:
            logger.info(f"Processing job {idx}/{len(job_urls)}: {job_url}")
            driver.get(job_url)
            
            # Wait for page to load
            time.sleep(3)
            
            # Handle any popups
            handle_popups(driver)
            
            # Verify job is devops related before applying
            try:
                page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
                job_title = ""
                job_description = ""
                
                # Try to get job title
                try:
                    title_selectors = [
                        "//h1[contains(@class, 'title')]",
                        "//h1[contains(@class, 'jobTitle')]",
                        "//div[contains(@class, 'title')]//h1",
                        "//span[contains(@class, 'jobTitle')]",
                    ]
                    for selector in title_selectors:
                        try:
                            title_elem = driver.find_element(By.XPATH, selector)
                            job_title = title_elem.text.lower()
                            break
                        except NoSuchElementException:
                            continue
                except:
                    pass
                
                # Check if job is devops related
                devops_keywords = ['devops', 'dev ops', 'sre', 'site reliability', 'cloud engineer', 
                                 'aws', 'azure', 'gcp', 'kubernetes', 'docker', 'jenkins', 
                                 'ci/cd', 'terraform', 'ansible', 'puppet', 'chef']
                
                is_devops = any(keyword in page_text or keyword in job_title for keyword in devops_keywords)
                
                if not is_devops:
                    logger.info(f"Job {idx} is not devops related. Skipping...")
                    continue
                else:
                    logger.info(f"Job {idx} is devops related. Proceeding to apply...")
            except Exception as e:
                logger.warning(f"Could not verify job role: {str(e)}. Proceeding anyway...")
            
            # Check if apply button exists
            try:
                # Look for various apply button patterns
                apply_button = None
                
                # Try different selectors for apply button
                apply_selectors = [
                    "//button[contains(text(), 'Apply')]",
                    "//a[contains(text(), 'Apply')]",
                    "//div[contains(@class, 'apply')]//button",
                    "//span[contains(text(), 'Apply')]/parent::button",
                ]
                
                for selector in apply_selectors:
                    try:
                        apply_button = driver.find_element(By.XPATH, selector)
                        if apply_button.is_displayed() and apply_button.is_enabled():
                            break
                    except NoSuchElementException:
                        continue
                
                if not apply_button:
                    logger.warning(f"No apply button found for job {idx}")
                    continue
                
                logger.info(f"Apply button found. Clicking...")
                apply_button.click()
                
                # Wait for application form/modal
                time.sleep(2)
                
                # Handle any popups that appear
                handle_popups(driver)
                
                # Check if there's a confirmation/submit button
                try:
                    # Look for submit/confirm button in modal
                    submit_selectors = [
                        "//button[contains(text(), 'Submit')]",
                        "//button[contains(text(), 'Confirm')]",
                        "//button[contains(text(), 'Send Application')]",
                        "//button[@type='submit']",
                    ]
                    
                    for selector in submit_selectors:
                        try:
                            submit_button = wait.until(
                                EC.element_to_be_clickable((By.XPATH, selector))
                            )
                            submit_button.click()
                            logger.info(f"Application submitted for job {idx}")
                            applied_count += 1
                            time.sleep(2)
                            break
                        except (TimeoutException, NoSuchElementException):
                            continue
                    else:
                        # If no submit button, application might be one-click
                        logger.info(f"One-click application completed for job {idx}")
                        applied_count += 1
                        
                except Exception as e:
                    logger.warning(f"Error submitting application: {str(e)}")
                    # Application might still be successful
                    applied_count += 1
                
                # Wait before next application
                time.sleep(Config.DELAY_BETWEEN_APPLICATIONS)
                
            except NoSuchElementException:
                logger.warning(f"Apply button not found for job {idx}")
                continue
            except Exception as e:
                logger.error(f"Error applying to job {idx}: {str(e)}")
                take_screenshot(driver, f"apply_error_job_{idx}")
                continue
                
        except TimeoutException as e:
            logger.error(f"Timeout loading job {idx}: {str(e)}")
            take_screenshot(driver, f"timeout_job_{idx}")
            continue
        except Exception as e:
            logger.error(f"Error processing job {idx}: {str(e)}")
            take_screenshot(driver, f"error_job_{idx}")
            continue
    
    return applied_count