import threading
import source.common_utilities.constants as constants

from source.pbc.pbc_utils import (
    get_pbc_instance,
    wait_for_response,
    logger
)

from source.common_utilities.log_manager import log_manager


def initialize_log_listener():

    def worker():

        def handler(msg_type, from_pbc):

            if msg_type == constants.PROTO_LOG_ENTRY:
                timestamp = from_pbc.log_entry.timestamp_ms
                text = from_pbc.log_entry.text

                formatted = f"[{timestamp}] {text}"

                log_manager.add_log(formatted)

        pbc = get_pbc_instance(handler)

        if not pbc:
            logger.error("Unable to initialize log listener")
            return

        logger.info("Log listener initialized")

    threading.Thread(target=worker, daemon=True).start()