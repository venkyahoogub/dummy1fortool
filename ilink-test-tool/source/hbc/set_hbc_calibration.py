import threading
import source.common_utilities.constants as constants
from source.hbc.hbc_utils import get_hbc_instance, logger

def set_calibration_value(irradiance_mw_per_cm2, dac_count, timeout=10):
    response_event = threading.Event()
    result = {}

    def handler(msg_type, from_hbc):
        logger.info("Handler received msg_type: %s", msg_type)
        if msg_type == constants.PROTO_CALIBRATIONRESULT:
            result['data'] = from_hbc
            response_event.set()

    hbc = get_hbc_instance(handler)
    if not hbc:
        msg = "Cannot set HBC calibration because HBC is unavailable."
        logger.error(msg)
        return msg

    try:
        # Set HBC calibration
        hbc.start_calibration(irradiance_mw_per_cm2, dac_count)

        # Wait for our local event to be set by the handler; avoid blocking forever
        if not response_event.wait(timeout):
            err = f"Timed out waiting for {constants.PROTO_CALIBRATIONRESULT} response after {timeout} second(s)"
            logger.error(err)
            raise TimeoutError(err)

        return str(result.get('data'))

    except TimeoutError as e:
        logger.error("Timeout: %s", e)
        return str(e)

    except Exception:
        logger.exception("Failed to set HBC calibration")
        return "HBC calibration operation failed"