# get_toolversion.py

import os
import sys
import dotenv
from source.pbc.pbc_utils import logger
from pathlib import Path


# Determine base path depending on if running as PyInstaller bundle or normal script
try:
    if getattr(sys, "frozen", False):
        # Running as PyInstaller bundle
        base_path = Path(sys._MEIPASS)
    else:
        # Add base path to have env file access inside the executable
        base_path = Path(__file__).parent.parent  # go one folder up to find .env

    dotenv_path = base_path / ".env"
    if dotenv_path.exists():
        dotenv.load_dotenv(dotenv_path)
    else:
        logger.warning(f".env file not found at {dotenv_path}, environment variables may be missing") 
except Exception as e:
    logger.error(f"Error loading .env: {e}")


def get_toolversion_info():
    """
    This function retrieves static metadata information about the tools version.
    When TeamCity builds the linux executable, the .env file's ILINK_TEST_TOOL_VERSION
    gets updated. This value is retrieved when the user requests for the tool's version.
    """

    try:
        version = os.environ["ILINK_TEST_TOOL_VERSION"].strip('"').strip("'")
        if not version:
            raise ValueError("ILINK_TEST_TOOL_VERSION is empty or not set")
        msg = f"v {version}"
        logger.info(msg)
        return str(msg)
    except Exception:
        logger.exception("Failed to get about information using ilink test tool's version")


def update_toolversion_teamcity(teamcity_build_version: str):
    try:
        if not teamcity_build_version or not isinstance(teamcity_build_version, str):
            raise ValueError("Invalid teamcity_build_version: must be a non-empty string")

        # Set env var with surrounding quotes
        os.environ["ILINK_TEST_TOOL_VERSION"] = f'"{teamcity_build_version}"'

        # Locate .env file
        dotenv_file = dotenv.find_dotenv()
        if not dotenv_file:
            raise FileNotFoundError(".env file not found")

        # Load and update .env
        dotenv.load_dotenv(dotenv_file)
        dotenv.set_key(dotenv_file, "ILINK_TEST_TOOL_VERSION", os.environ["ILINK_TEST_TOOL_VERSION"])

        logger.info(f"ILINK_TEST_TOOL_VERSION successfully set to {os.environ['ILINK_TEST_TOOL_VERSION']}")

    except Exception as e:
        logger.error(f"Error updating ILINK_TEST_TOOL_VERSION: {e}")
