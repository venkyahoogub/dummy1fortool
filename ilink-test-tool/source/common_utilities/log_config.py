import logging
import sys

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)

logger = logging.getLogger("ilink")  # name it consistently across project
logger.setLevel(logging.DEBUG)

# Adding helper to add/remove a capture handler
def add_capture_handler(buffer):
    handler = logging.StreamHandler(buffer)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return handler

def remove_capture_handler(handler):
    logger.removeHandler(handler)
