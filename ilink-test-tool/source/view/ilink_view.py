import tkinter as tk
import ttkbootstrap as ttkbs
from tkinter import scrolledtext
from ttkbootstrap.constants import SUCCESS
from pathlib import Path
from source.common_utilities.log_config import logger

# Utility for easy button state management
def set_buttons_state(buttons, state="normal"):
    for btn in buttons:
        btn.config(state=state)


def write_output(box, msg):
    box.config(state="normal")
    box.delete("1.0", tk.END)
    box.insert(tk.END, msg + "\n")
    box.see(tk.END)
    box.config(state="disabled")


def resource_path(relative_path):
    import sys, os
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return Path(base_path) / relative_path


def create_toggle_buttons(status_dict, container_frame, set_hardware_status):
    try:
        # Clear existing widgets
        for widget in container_frame.winfo_children():
            widget.destroy()

        # We want 6 rows per column, to avoid overcrowding and keep it readable.
        ROWS_PER_COLUMN = 6
        
        boolean_items = [(k, v) for k, v in status_dict.items() if isinstance(v, bool)]

        for index, (key, value) in enumerate(boolean_items):
            column, row = divmod(index, ROWS_PER_COLUMN)
            var = tk.BooleanVar(value=value)

            def make_cmd(k, v):
                return lambda v=v: set_hardware_status(k, v.get())

            toggle = tk.Checkbutton(
                container_frame, text=key, variable=var,
                command=make_cmd(key, var)
            )
            toggle.grid(row=row, column=column, sticky="w", padx=5, pady=2)
    except Exception as e:
        logger.error(f"Error creating toggle buttons: {e}")


def show_spinner(frame):
    spinner = ttkbs.Progressbar(frame, mode='indeterminate', bootstyle=SUCCESS, length=150)
    spinner.grid(row=10, column=0, pady=5)
    spinner.start()
    return spinner


def hide_spinner(spinner):
    spinner.stop()
    spinner.destroy()


# Modal Info Box
def show_modal_info_message(parent, text="Waiting for protobuf response"):
    modal = tk.Toplevel(parent)
    modal.title("Response In Progress")
    modal.geometry("300x100")
    modal.transient(parent)
    modal.grab_set()
    modal.resizable(False, False)
    info_label = ttkbs.Label(modal, text=text, bootstyle=SUCCESS)
    info_label.pack(expand=True, fill="both", padx=15, pady=20)
    modal.protocol("WM_DELETE_WINDOW", lambda: None)
    return modal


def hide_modal_info_message(modal):
    modal.grab_release()
    modal.destroy()
