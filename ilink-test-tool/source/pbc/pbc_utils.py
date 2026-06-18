# pbc_utils.py contains common code to be used across other functions.

import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from common_utilities.log_config import logger

# Append sys.path so that Python can find the neo_pbc_api package
try:
    parent_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "neo_pbc_api", "source", "python")
    )
    sys.path.insert(0, parent_dir)
except Exception:
    logger.exception("Failed to configure sys.path for neo_pbc_api.")

try:
    from source.pbc.pbc import Pbc
except ImportError:
    logger.exception("Failed to import Pbc from pbc module.")
    Pbc = None


def rx_msg_handler(msg_type, msg):
    logger.info(f"Received message (type {msg_type}): {msg}")


_pbc_instance = None

def get_pbc_instance(handler=None):
    global _pbc_instance
    if not _pbc_instance:
        _pbc_instance = Pbc(handler)
    else:
        _pbc_instance.rx_msg_handler = handler  # update the handler for this request
    return _pbc_instance


def wait_for_response(seconds=1):
    time.sleep(seconds)

def reset_pbc_instance():
    global _pbc_instance
    if _pbc_instance:
        try:
            # Try to close socket/thread if implemented, else just drop ref
            if hasattr(_pbc_instance, "socket") and hasattr(_pbc_instance.socket, "sock"):
                try:
                    _pbc_instance.socket.sock.close()
                except Exception:
                    pass
        except Exception:
            logger.exception("Error while closing Pbc socket")
        _pbc_instance = None