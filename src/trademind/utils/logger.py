"""
Logging utilities for TradeMind
"""
import logging
import sys
from pathlib import Path
from typing import Optional

def setup_logger(name: str = "trademind", 
                level: str = "INFO",
                log_file: Optional[Path] = None,
                console_output: bool = True) -> logging.Logger:
    """Setup logger with file and console handlers"""
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger