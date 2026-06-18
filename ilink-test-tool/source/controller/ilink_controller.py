import threading
import traceback
from model.ilink_model import parse_status_proto
from view.ilink_view import (
    write_output, create_toggle_buttons,
    show_spinner, hide_spinner,
    show_modal_info_message, hide_modal_info_message,
    set_buttons_state
)
from source.common_utilities.log_config import logger
from source.common_utilities.log_manager import log_manager


def _callable_name(fn):
    """Returns a name for a callable so the modal thread works for normal functions and functools.partial."""
    # Normal function
    name = getattr(fn, "__name__", None)
    if name:
        return name
    # functools.partial has .func
    func = getattr(fn, "func", None)
    if func:
        return getattr(func, "__name__", str(fn))
    return str(fn)


# Runs commands with spinner, buttons disabled, and info modal
def run_command_with_spinner_buttons_info(command_fn, output_box, toggle_frame, parent_frame, buttons, set_hardware_status, on_complete=None):
    try:
        set_buttons_state(buttons, "disabled")
        spinner = show_spinner(parent_frame)
        info_modal = show_modal_info_message(parent_frame)  # modal box

        def task():
            result = None
            exc = None
            try:
                cmd_name = _callable_name(command_fn)
                log_manager.add_log(f"Running command: {cmd_name}")
                result = command_fn()
                log_manager.add_log(f"Command completed: {cmd_name}")
            except Exception:
                # Capture exception traceback so we can display it in the UI
                exc = traceback.format_exc()
                logger.exception("Error running command_fn in background thread")

            def _on_complete_ui():
                # Write result or exception to output box
                try:
                    if exc:
                        write_output(output_box, f"Error running command:\n{exc}")
                    else:
                        # Convert result to string for display
                        write_output(output_box, "" if result is None else str(result))
                except Exception:
                    logger.exception("Failed to write output")

                # Handle toggles for parse / create toggle buttons or clear
                try:
                    cmd_name = _callable_name(command_fn)
                    if cmd_name == "get_status_info*":
                        try:
                            status_dict = parse_status_proto(result)
                            create_toggle_buttons(status_dict, toggle_frame, set_hardware_status)
                        except Exception:
                            logger.exception("Failed to create toggle buttons from status")
                            safe_clear_toggle_frame(toggle_frame)
                    else:
                        safe_clear_toggle_frame(toggle_frame)
                except Exception:
                    logger.exception("Toggle handling failed")
                    safe_clear_toggle_frame(toggle_frame)

                # Hide spinner/modal and re-enable buttons
                try:
                    hide_spinner(spinner)
                except Exception:
                    logger.exception("Failed to hide spinner")
                try:
                    hide_modal_info_message(info_modal)
                except Exception:
                    logger.exception("Failed to hide modal info message")
                try:
                    set_buttons_state(buttons, "normal")
                except Exception:
                    logger.exception("Failed to re-enable buttons")

                # Run optional completion callback
                if on_complete:
                    try:
                        on_complete(result)
                    except Exception:
                        logger.exception("on_complete callback raised")

            # Ensure UI updates run on the Tk mainloop
            try:
                output_box.after(0, _on_complete_ui)
            except Exception:
                logger.exception("Failed to schedule UI update with after(); running directly")
                try:
                    _on_complete_ui()
                except Exception:
                    logger.exception("Direct UI update also failed")

        threading.Thread(target=task, daemon=True).start()
    except Exception as e:
        logger.error(f"Error occurred using spinner buttons: {e}")


def safe_clear_toggle_frame(frame):
    try:
        for w in frame.winfo_children():
            w.destroy()
    except Exception as e:
        logger.warning(f"Warning: could not clear toggle_frame: {e}")