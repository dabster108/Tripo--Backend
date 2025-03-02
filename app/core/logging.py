import logging
import sys
from pathlib import Path
import os

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Configure logging
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(os.path.join("logs", "app.log"))
        ]
    )
    
    # Setup specific loggers
    logger = logging.getLogger("lanceraa")
    logger.setLevel(logging.DEBUG)
    
    return logger

# Create logger instance
logger = setup_logging()