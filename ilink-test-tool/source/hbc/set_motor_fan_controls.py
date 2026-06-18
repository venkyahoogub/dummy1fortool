import io
import logging
import threading
import time
import source.common_utilities.constants as constants
from source.hbc.hbc_utils import get_hbc_instance, logger

def move_motor_controls(x_pos_mm, y_pos_mm, z_pos_mm, timeout=60):
    def in_range(val):
        return -10 <= val <= 10

    if all(in_range(v) for v in [x_pos_mm, y_pos_mm, z_pos_mm]):
        response_event = threading.Event()
        result = {}

        def handler(msg_type, from_hbc):
            logger.info("Handler received msg_type: %s", msg_type)
            result['data'] = from_hbc
            response_event.set()

        hbc = get_hbc_instance(handler)
        if not hbc:
            msg = "Cannot move motors because HBC is unavailable."
            logger.error(msg)
            return msg

        try:
            # Set motor moves
            hbc.move_motors(x_pos_mm, y_pos_mm, z_pos_mm)
            time.sleep(3)

            # Get the status post motor move
            hbc.get_status()

            # Wait for our local event to be set by the handler; avoid blocking forever
            if not response_event.wait(timeout):
                err = f"Timed out waiting for {constants.PROTO_STATUS} response after {timeout} second(s)"
                logger.error(err)
                raise TimeoutError(err)

            return str(result.get('data'))

        except TimeoutError as e:
            logger.error("Timeout: %s", e)
            return str(e)

        except Exception:
            logger.exception("Failed to set distance sensor settings")
            return "distance sensor settings operation failed"
    else:
        return "The x,y,z motor positions must be within the limits of -10 mm to +10 mm"

def home_motors(timeout=60):
    response_event = threading.Event()
    result = {}

    def handler(msg_type, from_hbc):
        if msg_type == "motors_homed":
            result['data'] = "Motors are Homed"
            response_event.set()
        else:
            logger.info("Handler received msg_type: %s", msg_type)
            result['data'] = from_hbc
            response_event.set()

    hbc = get_hbc_instance(handler)
    if not hbc:
        msg = "Cannot home motors because HBC is unavailable."
        logger.error(msg)
        return msg

    try:
        # Home motors 
        hbc.home_motors()

        # Wait for our local event to be set by the handler; avoid blocking forever
        if not response_event.wait(timeout):
            err = f"Timed out waiting for {constants.PROTO_CONTROLS} response after {timeout} second(s)"
            logger.error(err)
            raise TimeoutError(err)

        return str(result.get('data'))

    except TimeoutError as e:
        logger.error("Timeout: %s", e)
        return str(e)

    except Exception:
        logger.exception("Failed to home motors")
        return "Home motors operation failed"

def set_fan_controls(uv_fan_enable, head_fans_enable, timeout=5):
    response_event = threading.Event()
    result = {}

    def handler(msg_type, from_hbc):
        logger.info("Handler received msg_type: %s", msg_type)
        result['data'] = from_hbc
        response_event.set()

    hbc = get_hbc_instance(handler)
    if not hbc:
        msg = "Cannot set fan controls because HBC is unavailable."
        logger.error(msg)
        return msg

    try:
        # Set fan controls
        hbc.set_fan_controls(uv_fan_enable, head_fans_enable)
        time.sleep(3)

        # Get the controls post fan on/off
        hbc.get_controls()

        # Wait for our local event to be set by the handler; avoid blocking forever
        if not response_event.wait(timeout):
            err = f"Timed out waiting for {constants.PROTO_CONTROLS} response after {timeout} second(s)"
            logger.error(err)
            raise TimeoutError(err)

        return str(result.get('data'))

    except TimeoutError as e:
        logger.error("Timeout: %s", e)
        return str(e)

    except Exception:
        logger.exception("Failed to set fan controls")
        return "Fan controls operation failed"