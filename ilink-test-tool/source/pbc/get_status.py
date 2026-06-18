import threading
from source.pbc.pbc_utils import get_pbc_instance, wait_for_response, logger
import source.common_utilities.constants as constants


def get_status_info():
    response_event = threading.Event()
    result = {}

    def handler(msg_type, from_pbc):
        if msg_type == constants.PROTO_STATUS:
            result['data'] = from_pbc
            response_event.set()

    pbc = get_pbc_instance(handler)
    if not pbc:
        msg = "Cannot retrieve about info because PBC is unavailable."
        logger.error(msg)
        return str(msg)

    try:
        pbc.get_status()
        wait_for_response()
        logger.info(str(result.get('data')))
        return str(result.get('data'))
    except Exception:
        logger.exception("Failed to get status information using get_status_info")
