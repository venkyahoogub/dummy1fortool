import threading
import source.common_utilities.constants as constants
from source.hbc.hbc_utils import get_hbc_instance, logger

# Pulsed treatment
def start_treatment_pulsed(irradiance_mw_per_cm2, treatment_time_ms, pulse_on_time_ms, pulse_off_time_ms, timeout=60):
    response_event = threading.Event()
    result = {}

    def handler(msg_type, from_hbc):
        logger.info("Handler received msg_type: %s", msg_type)
        if msg_type == constants.PROTO_TREATMENTRESULT:
            result['data'] = from_hbc
            response_event.set()

    hbc = get_hbc_instance(handler)
    if not hbc:
        msg = "Cannot start pulsed treatment because HBC is unavailable."
        logger.error(msg)
        return msg

    try:
        # start pulsed treatment
        hbc.start_pulsed_treatment(irradiance_mw_per_cm2, treatment_time_ms, pulse_on_time_ms, pulse_off_time_ms)

        # Wait for our local event to be set by the handler; avoid blocking forever
        if not response_event.wait(timeout):
            err = f"Timed out waiting for {constants.PROTO_TREATMENTRESULT} response after {timeout} second(s)"
            logger.error(err)
            raise TimeoutError(err)

        return str(result.get('data'))

    except TimeoutError as e:
        logger.error("Timeout: %s", e)
        return str(e)

    except Exception:
        logger.exception("Failed to start pulsed treatment")
        return "start pulsed treatment operation failed"

# Continuous treatment  or CW treatment
def start_cw_treatment(irradiance_mw_per_cm2, treatment_time_ms, timeout=60):
    response_event = threading.Event()
    result = {}

    def handler(msg_type, from_hbc):
        logger.info("Handler received msg_type: %s", msg_type)
        if msg_type == constants.PROTO_TREATMENTRESULT:
            result['data'] = from_hbc
            response_event.set()

    hbc = get_hbc_instance(handler)
    if not hbc:
        msg = "Cannot start continuous treatment because HBC is unavailable."
        logger.error(msg)
        return msg

    try:
        # start continuous treatment
        hbc.start_cw_treatment(irradiance_mw_per_cm2, treatment_time_ms)

        # Wait for our local event to be set by the handler; avoid blocking forever
        if not response_event.wait(timeout):
            err = f"Timed out waiting for {constants.PROTO_TREATMENTRESULT} response after {timeout} second(s)"
            logger.error(err)
            raise TimeoutError(err)

        return str(result.get('data'))

    except TimeoutError as e:
        logger.error("Timeout: %s", e)
        return str(e)

    except Exception:
        logger.exception("Failed to start continuous treatment")
        return "start continuous treatment operation failed"

# Demo treatment
def start_demo_treatment(treatment_time_ms, timeout=60):
    response_event = threading.Event()
    result = {}

    def handler(msg_type, from_hbc):
        logger.info("Handler received msg_type: %s", msg_type)
        if msg_type == constants.PROTO_TREATMENTRESULT:
            result['data'] = from_hbc
            response_event.set()

    hbc = get_hbc_instance(handler)
    if not hbc:
        msg = "Cannot start demo treatment because HBC is unavailable."
        logger.error(msg)
        return msg

    try:
        # start continuous treatment
        hbc.start_demo_treatment(treatment_time_ms)

        # Wait for our local event to be set by the handler; avoid blocking forever
        if not response_event.wait(timeout):
            err = f"Timed out waiting for {constants.PROTO_TREATMENTRESULT} response after {timeout} second(s)"
            logger.error(err)
            raise TimeoutError(err)

        return str(result.get('data'))

    except TimeoutError as e:
        logger.error("Timeout: %s", e)
        return str(e)

    except Exception:
        logger.exception("Failed to start demo treatment")
        return "start demo treatment operation failed"