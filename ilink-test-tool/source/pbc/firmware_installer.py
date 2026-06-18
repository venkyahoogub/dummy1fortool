import os
import io
import re
import time
import source.pbc.fw_update as fw_update
import source.pbc.get_about as get_about
import source.common_utilities.preload_envfile as preload_envfile
from pathlib import Path
from dotenv import load_dotenv, set_key
from source.pbc.pbc_utils import wait_for_response
from source.common_utilities.log_config import logger, add_capture_handler, remove_capture_handler

# Preload all the environment-based variables.
preload_envfile.preload_envfile()

def check_for_fwinstall_completion():
    """
    Checks that the install is complete and the required value is captured in output.
    """
    try:
        buf = io.StringIO()
        handler = add_capture_handler(buf)

        get_about.get_about_info()
        wait_for_response()

        remove_capture_handler(handler)
        output = buf.getvalue()
        buf.close()

        version = parse_version(output)

        logger.info(f"Completed verification of installed version: {version}")

    except Exception as err:
        logger.error(f"An unexpected error occurred: {err}")
        return None

def parse_version(output):
    """
    Parses version from captured get_about output.
    """
    try:
        # Load existing .env
        base_path = Path(__file__).parent.parent
        dotenv_path = base_path / ".env"
        load_dotenv(dotenv_path)
        version_match = re.search(r'version:\s*"([^"]+)"', output)

        installed_version = version_match.group(1) if version_match else None

        current_version = os.environ["PBC_VERSION"].strip('"')
        if current_version == installed_version:
            logger.info(f"Installed Version: {installed_version} and Current Version: {current_version} match.")
        else:
            logger.info(f"Installed Version: {installed_version} is newer than Current Version: {current_version}.")
            os.environ["PBC_VERSION"] = installed_version
            set_key(dotenv_path, "PBC_VERSION", installed_version)

        return installed_version

    except Exception as err:
        logger.error(f"Error parsing version or updating .env: {err}")
        return None

def install_firmware_updates(binary_file):
    buf = io.StringIO()
    handler = add_capture_handler(buf)
    # attach temporary handler
    logger.addHandler(handler)
    path = Path(binary_file)

    new_version = path.name
    new_version = str(new_version).replace("neo_pbc_fw_bootable_image_OTA_UPGRADE_SIGNED_","")
    new_version = str(new_version).replace(".bin","")
    current_version = os.environ["PBC_VERSION"].strip('"')
    try:
        logger.info("Binary file is: %s", binary_file)
        fw_update.update_firmware_from_file(binary_file)
        check_for_fwinstall_completion()
        handler.flush()
        return f"PBC firmware update complete with v: {new_version}, Previous version was v: {current_version}"
    except Exception as err:
        logger.error(f"An error occurred during firmware update: {err}")
