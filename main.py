"""
Naukri Automation Bot - Main Entry Point
Handles orchestration of login, search, and apply operations
"""

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
    logger_temp = None
    try:
        import logging
        logging.basicConfig(level=logging.INFO)
        logger_temp = logging.getLogger(__name__)
        logger_temp.warning("undetected_chromedriver not available, using regular selenium")
    except:
        pass

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

COOKIES_FILE = "cookies.json"

def load_cookies(driver):
    """Load saved cookies to bypass login"""
    if not os.path.exists(COOKIES_FILE):
        logger.info("⚠️ No cookies.json found, login will be required")
        return False
    
    try:
        with open(COOKIES_FILE, "r") as f:
            cookies = json.load(f)
        
        # Navigate to Naukri first to set cookies
        driver.get("https://www.naukri.com")
        time.sleep(2)
        
        # Add cookies
        for cookie in cookies:
            try:
                driver.add_cookie(cookie)
            except Exception as e:
                logger.debug(f"Could not add cookie: {e}")
        
        # Refresh to apply cookies
        driver.refresh()
        time.sleep(3)
        
        # Check if we're logged in by checking URL or page content
        current_url = driver.current_url
        if "nlogin" not in current_url and "login" not in current_url.lower():
            logger.info("✅ Logged in using saved cookies!")
            return True
        
        # Also check for dashboard elements
        try:
            from selenium.webdriver.common.by import By
            dashboard_indicators = driver.find_elements(By.XPATH, "//a[contains(@href, 'myHome') or contains(@href, 'mnjuser')]")
            if dashboard_indicators:
                logger.info("✅ Logged in using saved cookies!")
                return True
        except:
            pass
        
        logger.warning("❌ Cookies expired or invalid")
        return False
    except Exception as e:
        logger.warning(f"Error loading cookies: {e}")
        return False

def save_cookies(driver):
    """Save cookies after successful login"""
    try:
        cookies = driver.get_cookies()
        with open(COOKIES_FILE, "w") as f:
            json.dump(cookies, f)
        logger.info("✅ Cookies saved successfully!")
    except Exception as e:
        logger.warning(f"Error saving cookies: {e}")

def setup_driver():
    """Initialize and configure Chrome WebDriver using undetected_chromedriver if available"""
    try:
        # Initialize chrome_options for fallback
        chrome_options = Options()
        
        # Use undetected_chromedriver if available (better bot detection bypass)
        if UC_AVAILABLE:
            logger.info("Using undetected_chromedriver for better bot detection bypass")
            try:
                options = uc.ChromeOptions()
                
                # Basic options - minimal to avoid detection
                options.add_argument("--start-maximized")
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_argument("--disable-infobars")
                options.add_argument("--no-first-run")
                options.add_argument("--no-default-browser-check")
                options.add_argument("--disable-dev-shm-usage")
                
                # For CI environments, use headless but with better stealth
                if os.getenv("CI") == "true" or os.getenv("GITHUB_ACTIONS") == "true":
                    logger.info("Running in CI environment - using headless mode with stealth")
                    options.add_argument("--headless=new")
                    options.add_argument("--no-sandbox")
                    options.add_argument("--disable-gpu")
                    options.add_argument("--window-size=1920,1080")
                    options.add_argument("--disable-extensions")
                
                # Additional preferences (undetected_chromedriver handles these differently)
                prefs = {
                    "credentials_enable_service": False,
                    "profile.password_manager_enabled": False,
                    "profile.default_content_setting_values.notifications": 2
                }
                options.add_experimental_option("prefs", prefs)
                
                # Note: Don't use excludeSwitches with undetected_chromedriver - it handles this internally
                # options.add_experimental_option("excludeSwitches", ["enable-automation"])  # Not compatible
                
                # Create driver with undetected_chromedriver
                driver = uc.Chrome(options=options, use_subprocess=True, version_main=None)
                
                # Additional stealth measures after driver creation
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
                    pass  # CDP commands may not work in all environments
                
                logger.info("WebDriver initialized successfully with undetected_chromedriver")
                return driver
            except Exception as e:
                logger.warning(f"Failed to create undetected_chromedriver: {e}, falling back to regular selenium")
                # Continue to regular selenium fallback
        
        # Fallback to regular Selenium WebDriver
        logger.info("Using regular Selenium WebDriver")
        
        # Anti-detection measures
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--no-default-browser-check")
        chrome_options.add_argument("--disable-default-apps")
        
        # Set a realistic user agent
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Additional anti-detection preferences
        prefs = {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.default_content_setting_values.notifications": 2
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # Enable headless mode for CI environments (GitHub Actions)
        if os.getenv("CI") == "true" or os.getenv("GITHUB_ACTIONS") == "true":
            chrome_options.add_argument("--headless=new")  # Use new headless mode
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
        
        # Get ChromeDriver path and ensure we use the correct executable
        initial_path = ChromeDriverManager().install()
        logger.info(f"ChromeDriverManager returned: {initial_path} (isdir: {os.path.isdir(initial_path)}, isfile: {os.path.isfile(initial_path)})")
        
        # Fix for webdriver-manager issue: find the actual chromedriver executable
        # webdriver-manager sometimes returns a directory or the wrong file
        driver_path = initial_path
        
        # If it's a file but contains NOTICES, it's the wrong file - need to search
        if os.path.isfile(initial_path) and ('NOTICES' in initial_path or 'THIRD_PARTY' in initial_path):
            logger.warning(f"ChromeDriverManager returned wrong file: {initial_path}, searching for correct executable...")
            # Get the parent directory to search in
            search_dir = os.path.dirname(initial_path)
            driver_path = None
        elif os.path.isdir(initial_path):
            search_dir = initial_path
            driver_path = None
        else:
            # It's a file and seems correct, use it
            search_dir = None
        
        # If we need to search for the correct executable
        if search_dir:
            logger.info(f"Searching for ChromeDriver in: {search_dir}")
            
            # Look for chromedriver executable in the directory - be very specific
            possible_paths = [
                os.path.join(search_dir, "chromedriver-linux64", "chromedriver"),
                os.path.join(search_dir, "chromedriver"),
            ]
            
            # Check each path - must be a file, executable, and NOT contain NOTICES
            found = False
            for path in possible_paths:
                if os.path.isfile(path) and 'NOTICES' not in path and 'THIRD_PARTY' not in path and 'LICENSE' not in path and os.path.basename(path) == "chromedriver":
                    try:
                        # Make it executable first
                        if os.name != 'nt':
                            os.chmod(path, 0o755)
                        # Check if it's now executable (or on Windows, just verify it exists)
                        if os.name == 'nt' or os.access(path, os.X_OK):
                            driver_path = path
                            found = True
                            logger.info(f"Found ChromeDriver at: {driver_path}")
                            break
                    except Exception as e:
                        logger.warning(f"Error checking path {path}: {e}")
            
            # If still not found, search recursively but be very careful
            if not found:
                logger.info("Searching recursively for chromedriver...")
                all_files = glob.glob(os.path.join(search_dir, "**/*"), recursive=True)
                for file_path in all_files:
                    basename = os.path.basename(file_path)
                    # Must be a file, named exactly "chromedriver" (no extension, no prefix)
                    if (os.path.isfile(file_path) and 
                        basename == "chromedriver" and  # Exact match, no extensions
                        'NOTICES' not in file_path and
                        'THIRD_PARTY' not in file_path and
                        'LICENSE' not in file_path and
                        not file_path.endswith('.txt') and
                        not file_path.endswith('.md')):
                        try:
                            # Make it executable if it's not already
                            if os.name != 'nt':
                                os.chmod(file_path, 0o755)
                            # Check if it's now executable (or on Windows, just verify it exists)
                            if os.name == 'nt' or os.access(file_path, os.X_OK):
                                driver_path = file_path
                                found = True
                                logger.info(f"Found ChromeDriver recursively at: {driver_path}")
                                break
                        except Exception as e:
                            logger.warning(f"Error checking file {file_path}: {e}")
            
            if not found:
                # List all files for debugging
                all_files = glob.glob(os.path.join(search_dir, "**/*"), recursive=True)
                logger.error(f"Available files in {search_dir}:")
                for f in all_files[:20]:  # Show first 20 files
                    logger.error(f"  - {f} (basename: {os.path.basename(f)}, isfile: {os.path.isfile(f)})")
                raise FileNotFoundError(f"Could not find ChromeDriver executable in {search_dir}")
        
        # Final validation - ensure we don't have the wrong file
        if 'NOTICES' in driver_path or 'THIRD_PARTY' in driver_path:
            raise ValueError(f"Invalid ChromeDriver path detected: {driver_path}")
        
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
        
        # Advanced anti-detection measures
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
        
        # Step 1: Try to load cookies first (bypass login)
        logger.info("Step 1: Attempting to load saved cookies...")
        if load_cookies(driver):
            logger.info("✅ Login bypassed using saved cookies!")
        else:
            # Step 2: Login required
            logger.info("Step 2: Logging in to Naukri...")
            if not login_to_naukri(driver):
                logger.error("Login failed. Exiting...")
                take_screenshot(driver, "login_failed")
                sys.exit(1)
            
            # Save cookies after successful login
            logger.info("Saving cookies for future use...")
            save_cookies(driver)
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