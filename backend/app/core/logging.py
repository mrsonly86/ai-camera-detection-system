"""
Logging configuration for the AI Camera Detection System
"""
import os
import sys
from loguru import logger
from backend.app.core.config import get_settings

settings = get_settings()


def setup_logging():
    """Configure logging for the application"""
    
    # Remove default handler
    logger.remove()
    
    # Ensure log directory exists
    log_dir = os.path.dirname(settings.log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # Console handler
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>",
        level=settings.log_level,
        colorize=True
    )
    
    # File handler
    logger.add(
        settings.log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level=settings.log_level,
        rotation="1 day",
        retention="30 days",
        compression="zip"
    )
    
    # Error file handler
    error_log_file = settings.log_file.replace(".log", "_error.log")
    logger.add(
        error_log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level="ERROR",
        rotation="1 day",
        retention="30 days",
        compression="zip"
    )
    
    logger.info("Logging configured successfully")
    return logger


# Initialize logging
app_logger = setup_logging()