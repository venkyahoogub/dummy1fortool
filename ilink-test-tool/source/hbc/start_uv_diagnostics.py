import threading
import source.common_utilities.constants as constants
from source.hbc.hbc_utils import get_hbc_instance, logger

def start_uv_diagnostics(dac_counts, duration_ms, timeout=60):
    response_event = threading.Event()
    result = {}

    def handler(msg_type, from_hbc):
        logger.info("Handler received msg_type: %s", msg_type)
        if msg_type == constants.PROTO_DIAGNOSTICRESULT:
            result['data'] = from_hbc
            response_event.set()

    hbc = get_hbc_instance(handler)
    if not hbc:
        msg = "Cannot start UV diagnostics because HBC is unavailable."
        logger.error(msg)
        return msg

    try:
        # Run UV diagnostics with user defined params
        hbc.start_uv_diagnostic(dac_counts, duration_ms)

        # Wait for our local event to be set by the handler; avoid blocking forever
        if not response_event.wait(timeout):
            err = f"Timed out waiting for {constants.PROTO_DIAGNOSTICRESULT} response after {timeout} second(s)"
            logger.error(err)
            raise TimeoutError(err)

        return str(result.get('data'))

    except TimeoutError as e:
        logger.error("Timeout: %s", e)
        return str(e)

    except Exception:
        logger.exception("Failed to run UV diagnostics")
        return "UV diagnostics start operation failed"