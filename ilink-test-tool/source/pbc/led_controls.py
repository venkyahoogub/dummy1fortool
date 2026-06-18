import io
import logging
import threading
from source.pbc.pbc_utils import get_pbc_instance, wait_for_response, logger
import source.common_utilities.constants as constants

# --- static color effect ---
def start_static_color_effect(red, green, blue):
    log_stream = io.StringIO()
    stream_handler = logging.StreamHandler(log_stream)
    logger.addHandler(stream_handler)

    response_event = threading.Event()
    result = {}

    def handler(msg_type, from_pbc):
        result['data'] = from_pbc
        response_event.set()

    pbc = get_pbc_instance(handler)
    if not pbc:
        msg = "Cannot retrieve about info because PBC is unavailable."
        logger.error(msg)
        return log_stream.getvalue()

    try:
        pbc.start_led_strip_static_color_effect(red, green, blue)
        logger.info("Red: %s", red)
        logger.info("Green: %s", green)
        logger.info("Blue: %s", blue)
        return log_stream.getvalue()
    except Exception:
        logger.exception("Failed to get status information using start_static_color_effect")

# --- pulsed color effect ---
def start_pulse_color_effect(red, green, blue, pulse_period_ms):
    log_stream = io.StringIO()
    stream_handler = logging.StreamHandler(log_stream)
    logger.addHandler(stream_handler)

    response_event = threading.Event()
    result = {}

    def handler(msg_type, from_pbc):
        logger.info("msg_type is %s",msg_type)
        result['data'] = from_pbc
        response_event.set()

    pbc = get_pbc_instance(handler)
    if not pbc:
        msg = "Cannot retrieve about info because PBC is unavailable."
        logger.error(msg)
        return log_stream.getvalue()

    try:
        pbc.start_led_strip_pulse_effect(red, green, blue, pulse_period_ms)
        logger.info("Red: %s", red)
        logger.info("Green: %s", green)
        logger.info("Blue: %s", blue)
        logger.info("Pulse period: %s", pulse_period_ms)
        return log_stream.getvalue()
    except Exception:
        logger.exception("Failed to get status information using start_pulse_color_effect")

# --- raibnow color effect ---
def start_rainbow_color_effect():
    log_stream = io.StringIO()
    stream_handler = logging.StreamHandler(log_stream)
    logger.addHandler(stream_handler)

    response_event = threading.Event()
    result = {}

    def handler(msg_type, from_pbc):
        result['data'] = from_pbc
        response_event.set()

    pbc = get_pbc_instance(handler)
    if not pbc:
        msg = "Cannot retrieve about info because PBC is unavailable."
        logger.error(msg)
        return log_stream.getvalue()

    try:
        pbc.start_led_strip_rainbow_effect()
        logger.info("Static rainbow effect")
        return log_stream.getvalue()
    except Exception:
        logger.exception("Failed to get status information using start_rainbow_color_effect")

# --- chasing rainbow color effect ---
def start_chasing_rainbow_color_effect():
    log_stream = io.StringIO()
    stream_handler = logging.StreamHandler(log_stream)
    logger.addHandler(stream_handler)

    response_event = threading.Event()
    result = {}

    def handler(msg_type, from_pbc):
        result['data'] = from_pbc
        response_event.set()

    pbc = get_pbc_instance(handler)
    if not pbc:
        msg = "Cannot retrieve about info because PBC is unavailable."
        logger.error(msg)
        return log_stream.getvalue()

    try:
        pbc.start_led_strip_chasing_rainbow_effect()
        logger.info("Chasing rainbow effect")
        return log_stream.getvalue()
    except Exception:
        logger.exception("Failed to get status information using start_chasing_rainbow_color_effect")
