from source.hbc.hbc_utils import get_hbc_instance, logger
import source.common_utilities.constants as constants

def _field_text(msg, field_name):
    # If msg is falsy type
    if not msg:
        return f"{field_name}: None"

    # Try HasField if available
    has_field = False
    try:
        if hasattr(msg, "HasField") and callable(getattr(msg, "HasField")):
            has_field = msg.HasField(field_name)
    except Exception:
        # If HasField isn't usable, fall back to getattr presence check below.
        has_field = False

    try:
        value = getattr(msg, field_name)
    except Exception:
        return f"{field_name}: <unavailable>"

    if has_field:
        text = str(value).strip()
        if text:
            return f"{field_name}: {text}"
        else:
            # Present but no set subfields
            return f"{field_name}: (present, no subfields set)"
    else:
        text = str(value).strip()
        if text:
            return f"{field_name}: {text}"
        # No data found
        return f"{field_name}: None"


def start_self_test():
    hbc = get_hbc_instance()
    if not hbc:
        msg = "Cannot run self test because HBC is unavailable."
        logger.error(msg)
        return msg

    try:
        result = hbc.start_self_test(irradiance_mw_per_cm2=constants.UV_MILLIWATT_SELFTEST_VALUE)
        if result is None:
            return "No self-test result returned."

        # List the fields from the self test
        fields = [
            "pd1_error",
            "pd2_error",
            "pd3_error",
            "x_motor_error",
            "y_motor_error",
            "z_motor_error",
        ]

        lines = [_field_text(result, f) for f in fields]
        return "\n".join(lines)

    except TimeoutError as e:
        logger.error(str(e))
        return str(e)

    except Exception:
        logger.exception("Failed to run self test and return results")
        return "Self test failed"