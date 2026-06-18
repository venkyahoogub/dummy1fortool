import io
import logging
import threading
import time
import source.common_utilities.constants as constants
from source.pbc.pbc_utils import get_pbc_instance, wait_for_response, logger

def brake_controls(brake_enable, timeout=60):
    response_event = threading.Event()
    result = {}

    def handler(msg_type, from_pbc):
        logger.info("Handler received msg_type: %s", msg_type)
        result['data'] = from_pbc
        response_event.set()

    pbc = get_pbc_instance(handler)
    if not pbc:
        msg = "Cannot move motors because pbc is unavailable."
        logger.error(msg)
        return msg

    try:
        # Set brake control
        pbc.set_brake_controls(brake_enable)
        time.sleep(2)

        # Get the status post brake set/unset
        pbc.get_controls()
        wait_for_response()
        
        # Wait for our local event to be set by the handler; avoid blocking forever
        if not response_event.wait(timeout):
            err = f"Timed out waiting for {constants.PROTO_CONTROLS} response after {timeout} second(s)"
            logger.error(err)
            raise TimeoutError(err)

        logger.info(str(result.get('data')))
        return str(result.get('data'))

    except TimeoutError as e:
        logger.error("Timeout: %s", e)
        return str(e)

    except Exception:
        logger.exception("Failed to set brake settings")
        return "brake setting operation failed"
    
def set_fan_controls(fans_enable, timeout=5):
    response_event = threading.Event()
    result = {}

    def handler(msg_type, from_pbc):
        logger.info("Handler received msg_type: %s", msg_type)
        result['data'] = from_pbc
        response_event.set()

    pbc = get_pbc_instance(handler)
    if not pbc:
        msg = "Cannot set fan controls because pbc is unavailable."
        logger.error(msg)
        return msg

    try:
        # Set fan controls
        pbc.set_fan_controls(fans_enable)
        time.sleep(2)

        # Get the controls post fan on/off
        pbc.get_controls()
        wait_for_response()

        # Wait for our local event to be set by the handler; avoid blocking forever
        if not response_event.wait(timeout):
            err = f"Timed out waiting for {constants.PROTO_CONTROLS} response after {timeout} second(s)"
            logger.error(err)
            raise TimeoutError(err)

        logger.info(str(result.get('data')))
        return str(result.get('data'))

    except TimeoutError as e:
        logger.error("Timeout: %s", e)
        return str(e)

    except Exception:
        logger.exception("Failed to set fan controls")
        return "Fan controls operation failed"