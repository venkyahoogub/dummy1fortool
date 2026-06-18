import sys
import os
from pathlib import Path
from source.common_utilities.log_config import logger
from dotenv import load_dotenv

def preload_envfile():
    try:
        if getattr(sys, "frozen", False):
                base_path = Path(sys._MEIPASS)
        else:
                base_path = Path(__file__).parent  # go one folder up to find .env
                
        dotenv_path = base_path / ".env"

        if dotenv_path.exists():
                load_dotenv(dotenv_path)
        else:
                logger.warning(f".env file not found at {dotenv_path}, environment variables may be missing")
    
    except Exception as e:
        logger.error(f"Error loading .env: {e}")