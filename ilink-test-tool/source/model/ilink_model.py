import re
from source.common_utilities.log_config import logger

# Utility: parse status proto output into dict
def parse_status_proto(proto_str):
    status = {}
    for line in proto_str.splitlines():
        match = re.match(r'\s*([a-zA-Z0-9_]+):\s*(true|false|[-+]?[0-9]*\.?[0-9]+)', line)
        if match:
            key, value = match.groups()
            if value in ['true', 'false']:
                status[key] = value == 'true'
            else:
                try:
                    status[key] = float(value)
                except ValueError:
                    status[key] = value
    return status


# Dummy hardware setter (placeholder for actual hardware control)
def set_hardware_status(key, value):
    logger.info(f"[DUMMY] Set {key} to {value}")
