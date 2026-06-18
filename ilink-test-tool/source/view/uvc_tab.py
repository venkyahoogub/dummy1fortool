import tkinter as tk
import ttkbootstrap as ttkbs
from tkinter import scrolledtext
from ttkbootstrap.constants import SUCCESS
from model.ilink_model import set_hardware_status
from controller.ilink_controller import run_command_with_spinner_buttons_info
from source.common_utilities.log_config import logger
from uvc.client import UvcClient
from common_utilities import common_ui_info, constants


class UvcTab:
    def __init__(self, parent):
        self.tab = ttkbs.Frame(parent)
        parent.add(self.tab, text="UVC")

        # UVC client (not connected yet)
        self.uvc_client = None  

        # Layout
        self.tab.rowconfigure(0, weight=0)
        self.tab.rowconfigure(1, weight=1)
        self.tab.rowconfigure(2, weight=0)
        self.tab.columnconfigure(0, weight=0)
        self.tab.columnconfigure(1, weight=1)

        self.buttons = []
        self._build_buttons()
        self._build_output_area()

        # Register tab (if you still want this)
        common_ui_info.register_tab(self)

    def _connect_to_uvc(self):
        try:
            if not hasattr(self, "uvc_client") or self.uvc_client is None:
                self.uvc_client = UvcClient()

            if self.uvc_client.is_connected():
                logger.info("UVC already connected.")
                return

            self.uvc_client.connect()
            logger.info("UVC connected successfully.")
            self._write("UVC connected successfully.")

        except Exception as e:
            logger.error(f"UVC connection failed: {e}")
            self._write(f"UVC connection failed: {e}")

    def _write(self, message):
        self.output_box.config(state="normal")
        self.output_box.insert("end", message + "\n")
        self.output_box.see("end")
        self.output_box.config(state="disabled")

    def _build_buttons(self):
        button_zone = ttkbs.Frame(self.tab)
        button_zone.grid(row=0, column=0, rowspan=3, sticky="nw", padx=10, pady=10)

        def add_button(text, command, row, bootstyle=SUCCESS):
            btn = ttkbs.Button(
                button_zone,
                text=text,
                width=17,
                bootstyle=bootstyle,
                command=command,
            )
            btn.grid(row=row, column=0, pady=5, sticky="ew")
            self.buttons.append(btn)

        # Connect to UVC
        add_button(constants.CONNECT_UVC, self._connect_to_uvc, 0)

        # Helper: ensure connection exists
        def guard(fn):
            return lambda: (
                self._write("Not connected. Click 'Connect to UVC' first.")
                if self.uvc_client is None else fn()
            )

        # Add functional buttons
        add_button(
            constants.ABOUT,
            guard(lambda: run_command_with_spinner_buttons_info(
                self.uvc_client.get_about,
                self.output_box, self.toggle_frame, self.tab, self.buttons, set_hardware_status)),
            1,
        )

        add_button(
            constants.IS_CAL_VALID,
            guard(lambda: run_command_with_spinner_buttons_info(
                self.uvc_client.is_calibration_data_valid,
                self.output_box, self.toggle_frame, self.tab, self.buttons, set_hardware_status)),
            2,
        )

        add_button(
            constants.IS_CAMERA_WORKING,
            guard(lambda: run_command_with_spinner_buttons_info(
                self.uvc_client.is_camera_working,
                self.output_box, self.toggle_frame, self.tab, self.buttons, set_hardware_status)),
            3,
        )

        add_button(
            constants.CHECK_UVC_ERRORS,
            guard(lambda: run_command_with_spinner_buttons_info(
                self.uvc_client.get_errors,
                self.output_box, self.toggle_frame, self.tab, self.buttons, set_hardware_status)),
            4,
        )

        add_button(
            constants.UVC_START_TREATMENT,
            guard(lambda: run_command_with_spinner_buttons_info(
                self.uvc_client.start_treatment,
                self.output_box, self.toggle_frame, self.tab, self.buttons, set_hardware_status)),
            5,
        )

        add_button(
            constants.UVC_GET_TREATMENT_DATA,
            guard(lambda: run_command_with_spinner_buttons_info(
                self.uvc_client.get_treatment_data,
                self.output_box, self.toggle_frame, self.tab, self.buttons, set_hardware_status)),
            6,
        )

        tk.Label(button_zone, text=constants.UVC_PAUSE_TIME).grid(row=7, column=1, padx=0)
        self.pause_time = ttkbs.Entry(button_zone, width=5)
        self.pause_time.grid(row=7, column=2, padx=0)
        self.pause_time.insert(0, "0")

        add_button(
            constants.UVC_START_PAUSE_RESUME_TREATMENT,
            guard(lambda: run_command_with_spinner_buttons_info(
                lambda: self.uvc_client.start_treatment_with_pause_and_resume(self.pause_time.get()),
                self.output_box, self.toggle_frame, self.tab, self.buttons, set_hardware_status)),
            7,
        )

    def _build_output_area(self):
        self.output_box = scrolledtext.ScrolledText(self.tab, width=75, height=10)
        self.output_box.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        self.output_box.config(state="disabled")

        self.toggle_frame = tk.Frame(self.tab)
        self.toggle_frame.grid(row=2, column=1, sticky="nsew", padx=10, pady=5)
