import threading
import source.common_utilities.constants as constants
from source.hbc.hbc_utils import get_hbc_instance, logger

def set_uv_device_settings(pd1_gain_count, pd2_gain_count, pd3_gain_count, pi_gain_count, timeout=5):
    response_event = threading.Event()
    result = {}

    def handler(msg_type, from_hbc):
        logger.info("Handler received msg_type: %s", msg_type)
        if msg_type == constants.PROTO_DEVICE_SETTINGS:
            result['data'] = from_hbc
            response_event.set()

    hbc = get_hbc_instance(handler)
    if not hbc:
        msg = "Cannot set UV device settings because HBC is unavailable."
        logger.error(msg)
        return msg

    try:
        # Set UV device settings
        hbc.set_uv_device_settings(pd1_gain_count, pd2_gain_count, pd3_gain_count, pi_gain_count)

        # Request device settings
        hbc.get_device_settings()

        # Wait for our local event to be set by the handler; avoid blocking forever
        if not response_event.wait(timeout):
            err = f"Timed out waiting for {constants.PROTO_DEVICE_SETTINGS} response after {timeout} second(s)"
            logger.error(err)
            raise TimeoutError(err)

        return str(result.get('data'))

    except TimeoutError as e:
        logger.error("Timeout: %s", e)
        return str(e)

    except Exception:
        logger.exception("Failed to set UV device settings")
        return "UV device settings operation failed"