# main.py
import os
import sys
import glob
import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, WebDriverException

# Try to import undetected_chromedriver, fallback to regular selenium if not available
try:
    import undetected_chromedriver as uc
    UC_AVAILABLE = True
except ImportError:
    UC_AVAILABLE = False

from login import login_to_naukri
from search import search_jobs
from apply import apply_to_jobs
from config import Config
from utils.logger import setup_logger
from utils.helpers import take_screenshot, cleanup_driver, sanitize_and_load_cookies

logger = setup_logger(__name__)

COOKIES_FILE = "cookies.json"

def setup_driver():
    """Initialize and configure Chrome WebDriver using undetected_chromedriver if available"""
    try:
        chrome_options = Options()
        if UC_AVAILABLE:
            logger.info("Using undetected_chromedriver for better bot detection bypass")
            try:
                options = uc.ChromeOptions()
                options.add_argument("--start-maximized")
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_argument("--disable-infobars")
                options.add_argument("--no-first-run")
                options.add_argument("--no-default-browser-check")
                options.add_argument("--disable-dev-shm-usage")
                if os.getenv("CI") == "true" or os.getenv("GITHUB_ACTIONS") == "true":
                    options.add_argument("--headless=new")
                    options.add_argument("--no-sandbox")
                    options.add_argument("--disable-gpu")
                    options.add_argument("--window-size=1920,1080")
                    options.add_argument("--disable-extensions")
                prefs = {
                    "credentials_enable_service": False,
                    "profile.password_manager_enabled": False,
                    "profile.default_content_setting_values.notifications": 2
                }
                options.add_experimental_option("prefs", prefs)
                driver = uc.Chrome(options=options, use_subprocess=True, version_main=None)
                try:
                    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                        'source': '''
                            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                            window.chrome = { runtime: {} };
                        '''
                    })
                except:
                    pass
                logger.info("WebDriver initialized successfully with undetected_chromedriver")
                return driver
            except Exception as e:
                logger.warning(f"Failed to create undetected_chromedriver: {e}, falling back to regular selenium")

        logger.info("Using regular Selenium WebDriver")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--no-default-browser-check")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        prefs = {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.default_content_setting_values.notifications": 2
        }
        chrome_options.add_experimental_option("prefs", prefs)
        if os.getenv("CI") == "true" or os.getenv("GITHUB_ACTIONS") == "true":
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")

        initial_path = ChromeDriverManager().install()
        driver_path = initial_path
        search_dir = None

        if os.path.isfile(initial_path) and ('NOTICES' in initial_path or 'THIRD_PARTY' in initial_path):
            search_dir = os.path.dirname(initial_path)
            driver_path = None
        elif os.path.isdir(initial_path):
            search_dir = initial_path
            driver_path = None
        else:
            search_dir = None

        if search_dir:
            logger.info(f"Searching for ChromeDriver in: {search_dir}")
            possible_paths = [
                os.path.join(search_dir, "chromedriver-linux64", "chromedriver"),
                os.path.join(search_dir, "chromedriver"),
            ]
            found = False
            for path in possible_paths:
                if os.path.isfile(path) and os.path.basename(path) == "chromedriver":
                    try:
                        if os.name != 'nt':
                            os.chmod(path, 0o755)
                        if os.name == 'nt' or os.access(path, os.X_OK):
                            driver_path = path
                            found = True
                            logger.info(f"Found ChromeDriver at: {driver_path}")
                            break
                    except Exception as e:
                        logger.warning(f"Error checking path {path}: {e}")
            if not found:
                logger.info("Searching recursively for chromedriver...")
                all_files = glob.glob(os.path.join(search_dir, "**/*"), recursive=True)
                for file_path in all_files:
                    basename = os.path.basename(file_path)
                    if (os.path.isfile(file_path) and basename == "chromedriver" and
                        'NOTICES' not in file_path and 'THIRD_PARTY' not in file_path and
                        not file_path.endswith('.txt') and not file_path.endswith('.md')):
                        try:
                            if os.name != 'nt':
                                os.chmod(file_path, 0o755)
                            if os.name == 'nt' or os.access(file_path, os.X_OK):
                                driver_path = file_path
                                found = True
                                logger.info(f"Found ChromeDriver recursively at: {driver_path}")
                                break
                        except Exception as e:
                            logger.warning(f"Error checking file {file_path}: {e}")
            if not found:
                all_files = glob.glob(os.path.join(search_dir, "**/*"), recursive=True)
                logger.error(f"Available files in {search_dir}:")
                for f in all_files[:20]:
                    logger.error(f"  - {f} (basename: {os.path.basename(f)}, isfile: {os.path.isfile(f)})")
                raise FileNotFoundError(f"Could not find ChromeDriver executable in {search_dir}")

        if 'NOTICES' in str(driver_path) or 'THIRD_PARTY' in str(driver_path):
            raise ValueError(f"Invalid ChromeDriver path detected: {driver_path}")

        if os.path.isfile(driver_path) and os.name != 'nt':
            try:
                os.chmod(driver_path, 0o755)
            except Exception as e:
                logger.warning(f"Could not set executable permissions: {e}")

        logger.info(f"Using ChromeDriver at: {driver_path}")

        if not os.path.isfile(driver_path):
            raise FileNotFoundError(f"ChromeDriver executable not found at: {driver_path}")

        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)

        try:
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
            driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                    Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                    Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                '''
            })
        except Exception:
            pass

        logger.info("WebDriver initialized successfully")
        return driver
    except Exception as e:
        logger.error(f"Failed to initialize WebDriver: {str(e)}")
        raise

def load_cookies(driver):
    return sanitize_and_load_cookies(driver, COOKIES_FILE)

def save_cookies(driver):
    try:
        cookies = driver.get_cookies()
        with open(COOKIES_FILE, "w") as f:
            json.dump(cookies, f)
        logger.info("✅ Cookies saved successfully!")
    except Exception as e:
        logger.warning(f"Error saving cookies: {e}")

def main():
    driver = None
    try:
        logger.info("=" * 60)
        logger.info("Naukri Automation Bot - Starting")
        logger.info(f"Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)

        if not Config.NAUKRI_EMAIL or not Config.NAUKRI_PASSWORD:
            logger.error("Missing required environment variables: NAUKRI_EMAIL or NAUKRI_PASSWORD")
            sys.exit(1)

        driver = setup_driver()
        logger.info("Step 1: Attempting to load saved cookies...")
        if load_cookies(driver):
            logger.info("✅ Login bypassed using saved cookies!")
        else:
            logger.info("Step 2: Logging in to Naukri...")
            if not login_to_naukri(driver):
                logger.error("Login failed. Exiting...")
                take_screenshot(driver, "login_failed")
                sys.exit(1)
            logger.info("Saving cookies for future use...")
            save_cookies(driver)
            logger.info("Login successful!")

        logger.info("Step 3: Searching for jobs...")
        job_urls = search_jobs(driver)

        if not job_urls:
            logger.warning("No jobs found matching criteria")
            sys.exit(0)

        logger.info(f"Found {len(job_urls)} jobs")
        logger.info("Step 4: Applying to jobs...")
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
