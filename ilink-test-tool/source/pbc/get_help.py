from source.pbc.pbc_utils import get_pbc_instance, wait_for_response, logger


def get_help_info():
    """
    Calls the PBC device's get_help() function.

    This function retrieves all the parameters that can be used for the tool.
    """
    pbc = get_pbc_instance()
    if not pbc:
        logger.error("Cannot retrieve help info because Pbc is unavailable.")
        return

    try:
        msg = pbc.get_help()
        wait_for_response()
        return msg
    except Exception:
        logger.exception("Failed to get help information using get_help")

if __name__ == "__main__":
     get_help_info()