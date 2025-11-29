"""
Configuration Module
Loads configuration from environment variables
"""

import os

try:
    from utils.logger import setup_logger
    logger = setup_logger(__name__)
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
except Exception:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class Config:
    """Configuration class for Naukri Automation Bot"""
    
    # Login credentials (required)
    NAUKRI_EMAIL = os.getenv("NAUKRI_EMAIL", "")
    NAUKRI_PASSWORD = os.getenv("NAUKRI_PASSWORD", "")
    
    # Search parameters
    SEARCH_KEYWORD = os.getenv("SEARCH_KEYWORD", "devops")
    SEARCH_LOCATION = os.getenv("SEARCH_LOCATION", "Bangalore")
    MAX_SEARCH_PAGES = int(os.getenv("MAX_SEARCH_PAGES", "3"))
    MAX_JOBS_TO_APPLY = int(os.getenv("MAX_JOBS_TO_APPLY", "10"))
    
    # Apply settings
    APPLY_LIMIT = int(os.getenv("APPLY_LIMIT", "5"))
    DELAY_BETWEEN_APPLICATIONS = int(os.getenv("DELAY_BETWEEN_APPLICATIONS", "3"))
    
    # Screenshot settings
    SCREENSHOT_DIR = os.getenv("SCREENSHOT_DIR", "screenshots")
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.NAUKRI_EMAIL or not cls.NAUKRI_PASSWORD:
            logger.error("NAUKRI_EMAIL and NAUKRI_PASSWORD must be set")
            return False
        return True