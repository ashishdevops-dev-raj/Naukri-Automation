"""
Job Search Module
Searches for jobs based on configured criteria
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

try:
    from config import Config
    from utils.logger import setup_logger
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
        # Create a minimal Config class
        class Config:
            SEARCH_KEYWORD = os.getenv("SEARCH_KEYWORD", "devops")
            SEARCH_LOCATION = os.getenv("SEARCH_LOCATION", "Bangalore")
            MAX_SEARCH_PAGES = int(os.getenv("MAX_SEARCH_PAGES", "3"))
            MAX_JOBS_TO_APPLY = int(os.getenv("MAX_JOBS_TO_APPLY", "10"))
except Exception as e:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.error(f"Unexpected error during import: {e}")
    import os
    class Config:
        SEARCH_KEYWORD = os.getenv("SEARCH_KEYWORD", "devops")
        SEARCH_LOCATION = os.getenv("SEARCH_LOCATION", "Bangalore")
        MAX_SEARCH_PAGES = int(os.getenv("MAX_SEARCH_PAGES", "3"))
        MAX_JOBS_TO_APPLY = int(os.getenv("MAX_JOBS_TO_APPLY", "10"))


def search_jobs(driver):
    """
    Search for jobs on Naukri
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        list: List of job URLs
    """
    try:
        logger.info("Navigating to job search page...")
        driver.get("https://www.naukri.com/jobs")
        
        wait = WebDriverWait(driver, 20)
        
        # Handle any initial popups
        time.sleep(3)
        
        # Wait for search form
        logger.info("Waiting for search form...")
        search_keyword = wait.until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Enter keyword / designation / company']"))
        )
        
        # Enter search keyword if configured
        if Config.SEARCH_KEYWORD:
            logger.info(f"Entering search keyword: {Config.SEARCH_KEYWORD}")
            search_keyword.clear()
            search_keyword.send_keys(Config.SEARCH_KEYWORD)
            time.sleep(1)
        
        # Enter location if configured
        if Config.SEARCH_LOCATION:
            logger.info(f"Entering location: {Config.SEARCH_LOCATION}")
            location_field = driver.find_element(By.XPATH, "//input[@placeholder='Enter location']")
            location_field.clear()
            location_field.send_keys(Config.SEARCH_LOCATION)
            time.sleep(1)
        
        # Click search button
        logger.info("Clicking search button...")
        search_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Search') or contains(@class, 'search')]")
        search_button.click()
        
        # Wait for results to load
        logger.info("Waiting for search results...")
        time.sleep(5)
        
        # Collect job URLs
        job_urls = []
        max_pages = Config.MAX_SEARCH_PAGES
        
        for page in range(1, max_pages + 1):
            logger.info(f"Scraping page {page}...")
            
            # Wait for job listings
            try:
                wait.until(
                    EC.presence_of_element_located((By.XPATH, "//article[contains(@class, 'jobTuple')]"))
                )
            except TimeoutException:
                logger.warning(f"No job listings found on page {page}")
                break
            
            # Find all job links
            job_elements = driver.find_elements(
                By.XPATH, 
                "//article[contains(@class, 'jobTuple')]//a[contains(@href, '/job-listings/')]"
            )
            
            for element in job_elements:
                job_url = element.get_attribute('href')
                if job_url and job_url not in job_urls:
                    job_urls.append(job_url)
            
            logger.info(f"Found {len(job_elements)} jobs on page {page}")
            
            # Try to go to next page
            if page < max_pages:
                try:
                    next_button = driver.find_element(
                        By.XPATH, 
                        "//a[contains(@class, 'next') or contains(text(), 'Next')]"
                    )
                    if next_button.is_enabled():
                        next_button.click()
                        time.sleep(3)
                    else:
                        logger.info("No more pages available")
                        break
                except Exception as e:
                    logger.warning(f"Could not navigate to next page: {str(e)}")
                    break
        
        logger.info(f"Total unique jobs found: {len(job_urls)}")
        return job_urls[:Config.MAX_JOBS_TO_APPLY]
        
    except TimeoutException as e:
        logger.error(f"Timeout during job search: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Error during job search: {str(e)}", exc_info=True)
        return []