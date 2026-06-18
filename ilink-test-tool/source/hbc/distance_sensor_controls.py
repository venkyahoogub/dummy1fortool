import io
import logging
import threading
import time
import source.common_utilities.constants as constants
from source.hbc.hbc_utils import get_hbc_instance, logger

def set_distance_sensor_settings(gain, offset, timeout=5):
    response_event = threading.Event()
    result = {}

    def handler(msg_type, from_hbc):
        logger.info("Handler received msg_type: %s", msg_type)
        result['data'] = from_hbc
        response_event.set()

    hbc = get_hbc_instance(handler)
    if not hbc:
        msg = "Cannot set distance sensor settings because HBC is unavailable."
        logger.error(msg)
        return msg

    try:
        # Set distance sensor settings
        hbc.set_distance_sensor_settings(gain, offset)

        # Get the newly updated device settings for sensor
        hbc.get_device_settings()

        # Wait for our local event to be set by the handler; avoid blocking forever
        if not response_event.wait(timeout):
            err = f"Timed out waiting for {constants.PROTO_DISTANCE_SETTINGS_RESULT} response after {timeout} second(s)"
            logger.error(err)
            raise TimeoutError(err)

        return str(result.get('data'))

    except TimeoutError as e:
        logger.error("Timeout: %s", e)
        return str(e)

    except Exception:
        logger.exception("Failed to set distance sensor settings")
        return "distance sensor settings operation failed"
    
def distance_sensor_start_stop_ranging(runtime, timeout=5):
    log_stream = io.StringIO()
    stream_handler = logging.StreamHandler(log_stream)
    logger.addHandler(stream_handler)
    
    response_event = threading.Event()
    result = {}

    def handler(msg_type, from_hbc):
        logger.info("Handler received msg_type: %s", msg_type)
        if msg_type == constants.PROTO_DISTANCE_SETTINGS_RESULT:
            result['data'] = from_hbc
            response_event.set()

    hbc = get_hbc_instance(handler)
    if not hbc:
        msg = "Cannot start distance sensor ranging because HBC is unavailable."
        logger.error(msg)
        return log_stream.getvalue()

    try:
        logger.info("---- Start of distance sensor ranging")
        # Start distance sensor ranging
        hbc.distance_sensor_start_ranging()

        # Wait for our local event to be set by the handler; avoid blocking forever
        if not response_event.wait(timeout):
            err = f"Timed out waiting for {constants.PROTO_DISTANCE_SETTINGS_RESULT} response after {timeout} second(s)"
            logger.error(err)
            raise TimeoutError(err)
        
        logger.info(str(result.get('data')))
        time.sleep(runtime)

    except TimeoutError as e:
        logger.error("Timeout: %s", e)
        return str(e)

    except Exception:
        logger.exception("Failed to start distance sensor ranging")
        return "start distance sensor ranging operation failed"
    
    finally:
        # Stop distance sensor ranging after user specified time.
        hbc.distance_sensor_stop_ranging()
        logger.info("End of distance sensor ranging ---- ")
        logger.info(str(result.get('data')))
        return log_stream.getvalue()
        logger.removeHandler(stream_handler)