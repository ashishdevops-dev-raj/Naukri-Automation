# Utils package

# Explicitly export key functions to ensure they're available
try:
    from .logger import setup_logger
    from .helpers import handle_popups, take_screenshot, cleanup_driver
    __all__ = ['setup_logger', 'handle_popups', 'take_screenshot', 'cleanup_driver']
except ImportError:
    # If imports fail, define minimal fallbacks
    def setup_logger(name):
        import logging
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(name)
    
    def handle_popups(driver, max_attempts=3):
        pass
    
    def take_screenshot(driver, filename):
        return None
    
    def cleanup_driver(driver):
        try:
            driver.quit()
        except:
            pass
    
    __all__ = ['setup_logger', 'handle_popups', 'take_screenshot', 'cleanup_driver']
