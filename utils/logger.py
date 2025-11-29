"""
Logging Module
Configures logging for the application
"""

import logging
import os
from datetime import datetime

# Create logs directory if it doesn't exist
try:
    os.makedirs("logs", exist_ok=True)
except Exception:
    pass  # If we can't create logs directory, continue anyway


def setup_logger(name):
    """
    Setup logger with file and console handlers
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    try:
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        
        # Avoid duplicate handlers
        if logger.handlers:
            return logger
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
        
        # Try to add file handler
        try:
            log_filename = f"logs/naukri_bot_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_filename, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(detailed_formatter)
            logger.addHandler(file_handler)
        except Exception:
            # If file logging fails, continue with console only
            pass
        
        # Console handler (always add this)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        return logger
    except Exception:
        # If everything fails, return a basic logger
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(name)