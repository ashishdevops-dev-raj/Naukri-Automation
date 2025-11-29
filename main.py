"""
Naukri Automation Bot - Main Entry Point
Handles orchestration of login, search, and apply operations
"""

import os
import sys
import glob
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, WebDriverException

try:
    from login import login_to_naukri
    from search import search_jobs
    from apply import apply_to_jobs
    from config import Config
    from utils.logger import setup_logger
    from utils.helpers import take_screenshot, cleanup_driver
    logger = setup_logger(__name__)
except ImportError as e:
    import logging
    import sys
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.error(f"Critical import error: {e}")
    logger.error("Cannot proceed without required modules")
    sys.exit(1)
except Exception as e:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.error(f"Unexpected error during import: {e}")
    import sys
    sys.exit(1)


def setup_driver():
    """Initialize and configure Chrome WebDriver"""
    try:
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Enable headless mode for CI environments (GitHub Actions)
        if os.getenv("CI") == "true" or os.getenv("GITHUB_ACTIONS") == "true":
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
        
        # Get ChromeDriver path and ensure we use the correct executable
        driver_path = ChromeDriverManager().install()
        
        # Fix for webdriver-manager issue: find the actual chromedriver executable
        # webdriver-manager sometimes returns a directory instead of the executable
        if os.path.isdir(driver_path):
            # Look for chromedriver executable in the directory
            possible_paths = [
                os.path.join(driver_path, "chromedriver"),
                os.path.join(driver_path, "chromedriver-linux64", "chromedriver"),
                os.path.join(driver_path, "chromedriver.exe"),
            ]
            
            # Also search recursively
            chromedriver_files = glob.glob(os.path.join(driver_path, "**/chromedriver"), recursive=True)
            possible_paths.extend(chromedriver_files)
            
            # Find the first existing file that's not a directory and doesn't have unwanted extensions
            for path in possible_paths:
                if os.path.isfile(path) and not path.endswith('.txt') and not path.endswith('.md') and 'NOTICES' not in path:
                    driver_path = path
                    break
            else:
                # If we still haven't found it, try to find any executable file
                all_files = glob.glob(os.path.join(driver_path, "**/*"), recursive=True)
                for file_path in all_files:
                    if os.path.isfile(file_path) and 'chromedriver' in file_path.lower() and 'NOTICES' not in file_path and not file_path.endswith('.txt'):
                        driver_path = file_path
                        break
        
        # Ensure the driver is executable (Linux/Mac)
        if os.path.isfile(driver_path) and os.name != 'nt':
            try:
                os.chmod(driver_path, 0o755)
            except Exception as e:
                logger.warning(f"Could not set executable permissions: {e}")
        
        logger.info(f"Using ChromeDriver at: {driver_path}")
        
        # Verify the file exists and is not a directory
        if not os.path.isfile(driver_path):
            raise FileNotFoundError(f"ChromeDriver executable not found at: {driver_path}")
        
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Remove webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        logger.info("WebDriver initialized successfully")
        return driver
    except Exception as e:
        logger.error(f"Failed to initialize WebDriver: {str(e)}")
        raise


def main():
    """Main execution function"""
    driver = None
    try:
        logger.info("=" * 60)
        logger.info("Naukri Automation Bot - Starting")
        logger.info(f"Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)
        
        # Validate environment variables
        if not Config.NAUKRI_EMAIL or not Config.NAUKRI_PASSWORD:
            logger.error("Missing required environment variables: NAUKRI_EMAIL or NAUKRI_PASSWORD")
            sys.exit(1)
        
        # Setup driver
        driver = setup_driver()
        
        # Step 1: Login
        logger.info("Step 1: Logging in to Naukri...")
        if not login_to_naukri(driver):
            logger.error("Login failed. Exiting...")
            take_screenshot(driver, "login_failed")
            sys.exit(1)
        
        logger.info("Login successful!")
        
        # Step 2: Search for jobs
        logger.info("Step 2: Searching for jobs...")
        job_urls = search_jobs(driver)
        
        if not job_urls:
            logger.warning("No jobs found matching criteria")
            sys.exit(0)
        
        logger.info(f"Found {len(job_urls)} jobs")
        
        # Step 3: Apply to jobs
        logger.info("Step 3: Applying to jobs...")
        applied_count = apply_to_jobs(driver, job_urls)
        
        logger.info("=" * 60)
        logger.info(f"Execution completed successfully!")
        logger.info(f"Jobs applied: {applied_count}/{len(job_urls)}")
        logger.info("=" * 60)
        
    except TimeoutException as e:
        logger.error(f"Timeout error: {str(e)}")
        if driver:
            take_screenshot(driver, "timeout_error")
        sys.exit(1)
    except WebDriverException as e:
        logger.error(f"WebDriver error: {str(e)}")
        if driver:
            take_screenshot(driver, "webdriver_error")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        if driver:
            take_screenshot(driver, "unexpected_error")
        sys.exit(1)
    finally:
        if driver:
            cleanup_driver(driver)
            logger.info("WebDriver closed")


if __name__ == "__main__":
    main()