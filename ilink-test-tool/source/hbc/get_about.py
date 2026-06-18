import threading
from source.hbc.hbc_utils import get_hbc_instance, wait_for_response, logger
import source.common_utilities.constants as constants

def get_about_info():
    response_event = threading.Event()
    result = {}

    def handler(msg_type, from_hbc):
        if msg_type == constants.PROTO_ABOUT:
            result['data'] = from_hbc
            response_event.set()

    hbc = get_hbc_instance(handler)
    if not hbc:
        msg = "Cannot retrieve about info because HBC is unavailable."
        logger.error(msg)
        return str(msg)

    try:
        hbc.get_about()
        wait_for_response()         
        return_data = str(result.get('data'))
        logger.info(return_data)
        return return_data
        
    except Exception:
        logger.exception("Failed to get about information using get_about_info")