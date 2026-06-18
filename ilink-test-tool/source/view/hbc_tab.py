import tkinter as tk
import ttkbootstrap as ttkbs
from tkinter import scrolledtext
from ttkbootstrap.constants import SUCCESS, DANGER
from functools import partial
from hbc import (
    get_about,
    get_status,
    get_calibration_table,
    get_controls,
    get_device_limits,
    get_device_settings,
    start_self_test_and_get_results,
    set_and_get_nir_led_controls,
    set_and_get_fixation_led_controls,
    set_and_get_camera_triggers,
    set_serial_number,
    start_uv_diagnostics,
    set_hbc_calibration,
    reset_to_default,
)
from common_utilities import common_ui_info, constants
from common_utilities.log_config import logger
from model.ilink_model import set_hardware_status
from controller.ilink_controller import run_command_with_spinner_buttons_info


class HbcTab:
    def __init__(self, parent):
        self.tab = ttkbs.Frame(parent)
        parent.add(self.tab, text="HBC")

        # Layout
        self.tab.rowconfigure(0, weight=0)
        self.tab.rowconfigure(1, weight=1)
        self.tab.rowconfigure(2, weight=0)
        self.tab.columnconfigure(0, weight=0)
        self.tab.columnconfigure(1, weight=1)

        self.buttons = []
        self._build_buttons()
        self._build_output_area()

        # Register this tab globally
        common_ui_info.register_tab(self)

    def _build_buttons(self):
        """Create the button panel and commands for HBC."""
        button_zone = ttkbs.Frame(self.tab)
        button_zone.grid(row=0, column=0, rowspan=3, sticky="nw", padx=10, pady=10)

        def add_button(text, command, row, bootstyle=SUCCESS):
            btn = ttkbs.Button(
                button_zone,
                text=text,
                width=15,
                bootstyle=bootstyle,
                command=command,
            )
            btn.grid(row=row, column=0, pady=5, sticky="ew")
            self.buttons.append(btn)
        
        # --- Adding 1 text box to get user input for device serial number ---
        tk.Label(button_zone, text="Serial #").grid(row=0, column=1, padx=0)
        self.serial_number_entry = ttkbs.Entry(button_zone, width=9)
        self.serial_number_entry.grid(row=0, column=2, padx=0)

        add_button(constants.SET_DEVICE_SERIAL_NUMBER, lambda: run_command_with_spinner_buttons_info(
            partial(set_serial_number.set_serial_number, str(self.serial_number_entry.get() or "NEO000000")), 
            self.output_box, self.toggle_frame, self.tab, self.buttons, set_hardware_status), 0)

        add_button(constants.ABOUT, lambda: run_command_with_spinner_buttons_info(
            get_about.get_about_info, self.output_box, self.toggle_frame, self.tab, self.buttons, set_hardware_status), 1)
        
        add_button(constants.STATUS, lambda: run_command_with_spinner_buttons_info(
            get_status.get_status_info, self.output_box, self.toggle_frame, self.tab, self.buttons, set_hardware_status), 2)
        
        add_button(constants.CONTROLS, lambda: run_command_with_spinner_buttons_info(
            get_controls.get_controls_info, self.output_box, self.toggle_frame, self.tab, self.buttons, set_hardware_status), 3)
        
        add_button(constants.DEVICE_SETTINGS, lambda: run_command_with_spinner_buttons_info(
            get_device_settings.get_device_settings_info, self.output_box, self.toggle_frame, self.tab, self.buttons, set_hardware_status), 4)
        
        add_button(constants.DEVICE_LIMITS, lambda: run_command_with_spinner_buttons_info(
            get_device_limits.get_device_limits_info, self.output_box, self.toggle_frame, self.tab, self.buttons, set_hardware_status), 5)
        
        add_button(constants.CAL_TABLE, lambda: run_command_with_spinner_buttons_info(
            get_calibration_table.get_calibration_table_info, self.output_box, self.toggle_frame, self.tab, self.buttons, set_hardware_status), 6)
        
        add_button(constants.HBC_SELF_TEST, lambda: run_command_with_spinner_buttons_info(
            start_self_test_and_get_results.start_self_test, self.output_box, self.toggle_frame, self.tab, self.buttons, set_hardware_status), 7)

	    # --- Adding 2 text boxes to get user input for top, bot nir LED values ---
        tk.Label(button_zone, text="Top %").grid(row=8, column=1, padx=0)
        self.top_entry = ttkbs.Entry(button_zone, width=3)
        self.top_entry.grid(row=8, column=2, padx=0)
        self.top_entry.insert(0, "0")

        tk.Label(button_zone, text="Bot %").grid(row=8, column=3, padx=0)
        self.bot_entry = ttkbs.Entry(button_zone, width=3)
        self.bot_entry.grid(row=8, column=4, padx=0)
        self.bot_entry.insert(0, "0")

        add_button(constants.SET_GET_NIR_LED, lambda: run_command_with_spinner_buttons_info(
            partial(set_and_get_nir_led_controls.set_get_nir_led, 
                    int(self.top_entry.get() or 0), 
                    int(self.bot_entry.get() or 0)
                ),
            self.output_box,
            self.toggle_frame,
            self.tab,
            self.buttons,
            set_hardware_status), 8)

        # --- Adding 1 text box to get user input for fixation LED values ---
        tk.Label(button_zone, text="Fix").grid(row=9, column=1, padx=0)
        self.fixation_entry = ttkbs.Entry(button_zone, width=3)
        self.fixation_entry.grid(row=9, column=2, padx=0)
        self.fixation_entry.insert(0, "10")

        add_button(constants.SET_GET_FIXATION_LED, lambda: run_command_with_spinner_buttons_info(
            partial(set_and_get_fixation_led_controls.set_get_fixation_led, 
                    int(self.fixation_entry.get() or 10)
                ),
            self.output_box,
            self.toggle_frame,
            self.tab,
            self.buttons,
            set_hardware_status), 9)

        # --- Adding 2 text boxes to get user input for frequency_hz, duration_ms camera trigger values ---
        tk.Label(button_zone, text="Frequency(hz)").grid(row=10, column=1, padx=0)
        self.frequency = ttkbs.Entry(button_zone, width=3)
        self.frequency.grid(row=10, column=2, padx=0)
        self.frequency.insert(0, "7")

        tk.Label(button_zone, text="Duration(ms)").grid(row=10, column=3, padx=0)
        self.duration_c = ttkbs.Entry(button_zone, width=3)
        self.duration_c.grid(row=10, column=4, padx=0)
        self.duration_c.insert(0, "30")

        add_button(constants.SET_GET_CAMERA_TRIGGERS, lambda: run_command_with_spinner_buttons_info(
            partial(set_and_get_camera_triggers.set_get_camera_trigger_controls, 
                    int(self.frequency.get() or 7), 
                    int(self.duration_c.get() or 30)
                ),
            self.output_box,
            self.toggle_frame,
            self.tab,
            self.buttons,
            set_hardware_status), 10)
        
        # --- Adding 2 text boxes to get user input for dac_counts, duration_ms UV diagnostics ---
        tk.Label(button_zone, text="DAC counts").grid(row=11, column=1, padx=0)
        self.dac = ttkbs.Entry(button_zone, width=3)
        self.dac.grid(row=11, column=2, padx=0)
        self.dac.insert(0, "5000")

        tk.Label(button_zone, text="Duration(ms)").grid(row=11, column=3, padx=0)
        self.duration = ttkbs.Entry(button_zone, width=3)
        self.duration.grid(row=11, column=4, padx=0)
        self.duration.insert(0, "3000")

        add_button(constants.START_UV_DIAGNOSTIC, lambda: run_command_with_spinner_buttons_info(
            partial(start_uv_diagnostics.start_uv_diagnostics, 
                    int(self.dac.get() or 5000), 
                    int(self.duration.get() or 3000)
                ),
            self.output_box,
            self.toggle_frame,
            self.tab,
            self.buttons,
            set_hardware_status), 11)

        # --- Adding 2 text boxes to get user input for irradiance, dac_counts for HBC calibration ---
        tk.Label(button_zone, text="Irradiance (3-45)").grid(row=12, column=1, padx=0)
        self.irr = ttkbs.Entry(button_zone, width=3)
        self.irr.grid(row=12, column=2, padx=0)
        self.irr.insert(0, constants.PROTO_DEFAULT_IRR)

        tk.Label(button_zone, text="DAC Counts").grid(row=12, column=3, padx=0)
        self.dac_c = ttkbs.Entry(button_zone, width=3)
        self.dac_c.grid(row=12, column=4, padx=0)
        self.dac_c.insert(0, constants.PROTO_DEFAULT_DAC)

        add_button(constants.START_HBC_CALIBRATION, lambda: run_command_with_spinner_buttons_info(
            partial(set_hbc_calibration.set_calibration_value, 
                    int(self.irr.get() or constants.PROTO_DEFAULT_IRR), 
                    int(self.dac_c.get() or constants.PROTO_DEFAULT_DAC)
                ),
            self.output_box,
            self.toggle_frame,
            self.tab,
            self.buttons,
            set_hardware_status), 12)
    
        # --- Reset to default ---
        add_button(constants.RESET_HBC_TO_DEFAULT, lambda: run_command_with_spinner_buttons_info(
            partial(reset_to_default.reset_to_default),
            self.output_box, self.toggle_frame, self.tab, self.buttons, set_hardware_status), 13, bootstyle=DANGER)
        
    def _build_output_area(self):
        """Create output text box + toggle frame."""
        self.output_box = scrolledtext.ScrolledText(self.tab, width=75, height=10)
        self.output_box.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        self.output_box.config(state="disabled")

        self.toggle_frame = tk.Frame(self.tab)
        self.toggle_frame.grid(row=2, column=1, sticky="nsew", padx=10, pady=5)
