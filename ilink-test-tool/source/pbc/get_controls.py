import threading
from source.pbc.pbc_utils import get_pbc_instance, wait_for_response, logger
import source.common_utilities.constants as constants

def get_controls_info():
    response_event = threading.Event()
    result = {}

    def handler(msg_type, from_pbc):
        if msg_type == constants.PROTO_CONTROLS:
            result['data'] = from_pbc
            response_event.set()

    pbc = get_pbc_instance(handler)
    if not pbc:
        msg = "Cannot retrieve about info because PBC is unavailable."
        logger.error(msg)
        return str(msg)

    try:
        pbc.get_controls()
        wait_for_response()
        return_data = str(result.get('data'))
        logger.info(return_data)
        return return_data
    except Exception:
        logger.exception("Failed to get controls information using get_controls_info")