import sys
import os
import time
from source.pbc.pbc import Pbc
from source.pbc.pbc_utils import logger, get_pbc_instance, reset_pbc_instance

parent_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "neo_pbc_api", "source", "python")
)
try:
    if os.path.isdir(parent_dir) and parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
        logger.info(f"Inserted '{parent_dir}' into sys.path")
except Exception as e:
    logger.error(f"Failed to insert '{parent_dir}' into sys.path: {e}")

def rx_msg_handler(msg_type, msg):
    logger.info(f"msg: {msg}")
    logger.info(f"msg_type: {msg_type}")

def update_firmware_from_file(binaryfile):
    current_path = os.getcwd()
    new_path = os.path.join(current_path, "installation")
    os.makedirs(new_path, exist_ok=True)

    abs_binary = os.path.abspath(binaryfile)
    if not os.path.isfile(abs_binary):
        raise FileNotFoundError(f"Error: File '{abs_binary}' does not exist.")

    try:
        pbc = get_pbc_instance(rx_msg_handler)
        pbc.update_firmware(abs_binary)
        # After firmware update, reset the Pbc instance
        reset_pbc_instance()
    except Exception as e:
        logger.error(f"Firmware update failed: {e}")
        raise

if __name__ == '__main__':
    if len(sys.argv) != 2:
        logger.error("Usage: python fw_update.py <fw_image.bin>")
        sys.exit(1)
    try:
        update_firmware_from_file(sys.argv[1])
    except FileNotFoundError as e:
        logger.error(e)
        sys.exit(1)
        