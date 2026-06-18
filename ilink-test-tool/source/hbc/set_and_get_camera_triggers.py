import threading
import source.common_utilities.constants as constants
from source.hbc.hbc_utils import get_hbc_instance, logger

def set_get_camera_trigger_controls(frequency_hz, duration_ms, timeout=5):
    response_event = threading.Event()
    result = {}

    def handler(msg_type, from_hbc):
        logger.info("Handler received msg_type: %s", msg_type)
        if msg_type == constants.PROTO_CONTROLS:
            result['data'] = from_hbc
            response_event.set()

    hbc = get_hbc_instance(handler)
    if not hbc:
        msg = "Cannot set camera trigger controls because HBC is unavailable."
        logger.error(msg)
        return msg

    try:
        # Set camera trigger controls
        hbc.set_camera_trigger_controls(frequency_hz, duration_ms)

        # Request updated controls
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
        logger.exception("Failed to set/get camera trigger controls")
        return "Camera trigger controls operation failed"