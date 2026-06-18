import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from common_utilities.log_config import logger

try:
    parent_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "neo_hbc_api", "source", "python")
    )
    sys.path.insert(0, parent_dir)
except Exception:
    logger.exception("Failed to configure sys.path for neo_hbc_api.")

try:
    from source.hbc.hbc import Hbc
except ImportError:
    logger.exception("Failed to import Hbc from hbc module.")
    Hbc = None

def rx_msg_handler(msg_type, msg):
    logger.info(f"Received message (type {msg_type}): {msg}")

_hbc_instance = None

def get_hbc_instance(handler=None):
    global _hbc_instance
    if not _hbc_instance:
        if Hbc is None:
             logger.error("Hbc class is not available due to import error.")
             return None
        _hbc_instance = Hbc(handler if handler is not None else rx_msg_handler)
    else:
        if handler is not None:
            _hbc_instance.rx_msg_handler = handler
    return _hbc_instance


def wait_for_response(seconds=1):
    time.sleep(seconds)

def reset_hbc_instance():
    global _hbc_instance
    if _hbc_instance:
        try:
            if hasattr(_hbc_instance, "socket") and hasattr(_hbc_instance.socket, "sock"):
                try:
                    _hbc_instance.socket.sock.close()
                except Exception:
                    pass
        except Exception:
            logger.exception("Error while closing Hbc socket")
        _hbc_instance = None