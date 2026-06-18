import tkinter as tk
import ttkbootstrap as ttkbs
from tkinter import scrolledtext
from ttkbootstrap.constants import SUCCESS
from functools import partial
from hbc import (
    start_treatment,
    set_uv_device_settings,
)
from common_utilities import common_ui_info, constants
from common_utilities.log_config import logger
from model.ilink_model import set_hardware_status
from controller.ilink_controller import run_command_with_spinner_buttons_info


class TreatmentTab:
    def __init__(self, parent):
        self.tab = ttkbs.Frame(parent)
        parent.add(self.tab, text="Treatment (HBC)")

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
        """Create the button panel and commands for Treatment."""
        button_zone = ttkbs.Frame(self.tab)
        button_zone.grid(row=0, column=0, rowspan=3, sticky="nw", padx=10, pady=10)

        DEFAULT_IRRADIANCE_MW=30
        DEFAULT_TREATMENT_TIME_MS=6000
        DEFAULT_PULSE_ON_MS=1000
        DEFAULT_PULSE_OFF_MS=1000

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
        
        # --- Adding 4 text box to get user input for starting pulsed treatments ---
        tk.Label(button_zone, text=constants.IRRADIANCE).grid(row=0, column=1, padx=0)
        self.irradiance_mw_per_cm_p = ttkbs.Entry(button_zone, width=5)
        self.irradiance_mw_per_cm_p.grid(row=0, column=2, padx=0)
        self.irradiance_mw_per_cm_p.insert(0, str(DEFAULT_IRRADIANCE_MW))

        tk.Label(button_zone, text=constants.TREATMENT_TIME).grid(row=0, column=3, padx=0)
        self.treatment_time_ms_p = ttkbs.Entry(button_zone, width=5)
        self.treatment_time_ms_p.grid(row=0, column=4, padx=0)
        self.treatment_time_ms_p.insert(0, str(DEFAULT_TREATMENT_TIME_MS))

        tk.Label(button_zone, text=constants.PULSE_ON).grid(row=1, column=1, padx=0)
        self.pulse_on_time_ms_p = ttkbs.Entry(button_zone, width=5)
        self.pulse_on_time_ms_p.grid(row=1, column=2, padx=0)
        self.pulse_on_time_ms_p.insert(0, str(DEFAULT_PULSE_ON_MS))

        tk.Label(button_zone, text=constants.PULSE_OFF).grid(row=1, column=3, padx=0)
        self.pulse_off_time_ms_p = ttkbs.Entry(button_zone, width=5)
        self.pulse_off_time_ms_p.grid(row=1, column=4, padx=0)
        self.pulse_off_time_ms_p.insert(0, str(DEFAULT_PULSE_OFF_MS))

        add_button(constants.START_PULSED_TREATMENT, lambda: run_command_with_spinner_buttons_info(
            partial(start_treatment.start_treatment_pulsed, 
                    int(self.irradiance_mw_per_cm_p.get() or DEFAULT_IRRADIANCE_MW), 
                    int(self.treatment_time_ms_p.get() or DEFAULT_TREATMENT_TIME_MS),
                    int(self.pulse_on_time_ms_p.get() or DEFAULT_PULSE_ON_MS), 
                    int(self.pulse_off_time_ms_p.get() or DEFAULT_PULSE_OFF_MS)), 
            self.output_box, self.toggle_frame, self.tab, self.buttons, set_hardware_status), 0)
        

        # --- Adding 2 text box to get user input for starting continuous treatments ---
        tk.Label(button_zone, text=constants.IRRADIANCE).grid(row=4, column=1, padx=0)
        self.irradiance_mw_per_cm2_cw = ttkbs.Entry(button_zone, width=5)
        self.irradiance_mw_per_cm2_cw.grid(row=4, column=2, padx=0)
        self.irradiance_mw_per_cm2_cw.insert(0, str(DEFAULT_IRRADIANCE_MW))

        tk.Label(button_zone, text=constants.TREATMENT_TIME).grid(row=4, column=3, padx=0)
        self.treatment_time_ms_cw = ttkbs.Entry(button_zone, width=5)
        self.treatment_time_ms_cw.grid(row=4, column=4, padx=0)
        self.treatment_time_ms_cw.insert(0, str(DEFAULT_TREATMENT_TIME_MS))

        add_button(constants.START_CONTINUOUS_TREATMENT, lambda: run_command_with_spinner_buttons_info(
            partial(start_treatment.start_cw_treatment, 
                    int(self.irradiance_mw_per_cm2_cw.get() or DEFAULT_IRRADIANCE_MW), 
                    int(self.treatment_time_ms_cw.get() or DEFAULT_TREATMENT_TIME_MS)), 
            self.output_box, self.toggle_frame, self.tab, self.buttons, set_hardware_status), 4)
        
        # --- Adding 1 text box to get user input for demo treatment ---
        tk.Label(button_zone, text=constants.TREATMENT_TIME).grid(row=7, column=1, padx=0)
        self.treatment_time_ms_d = ttkbs.Entry(button_zone, width=5)
        self.treatment_time_ms_d.grid(row=7, column=2, padx=0)
        self.treatment_time_ms_d.insert(0, str(DEFAULT_TREATMENT_TIME_MS))

        add_button(constants.START_DEMO_TREATMENT, lambda: run_command_with_spinner_buttons_info(
            partial(start_treatment.start_demo_treatment, 
                    int(self.treatment_time_ms_d.get() or DEFAULT_TREATMENT_TIME_MS)), 
            self.output_box, self.toggle_frame, self.tab, self.buttons, set_hardware_status), 7)
        
        # --- Adding 4 text box to get user input for UV device settings ---
        tk.Label(button_zone, text=constants.UV_DEVICE_SETTINGS_PD1).grid(row=9, column=1, padx=0)
        self.pd1_gain_count = ttkbs.Entry(button_zone, width=5)
        self.pd1_gain_count.grid(row=9, column=2, padx=0)
        self.pd1_gain_count.insert(0, "0")

        tk.Label(button_zone, text=constants.UV_DEVICE_SETTINGS_PD2).grid(row=9, column=3, padx=0)
        self.pd2_gain_count = ttkbs.Entry(button_zone, width=5)
        self.pd2_gain_count.grid(row=9, column=4, padx=0)
        self.pd2_gain_count.insert(0, "512")

        tk.Label(button_zone, text=constants.UV_DEVICE_SETTINGS_PD3).grid(row=10, column=1, padx=0)
        self.pd3_gain_count = ttkbs.Entry(button_zone, width=5)
        self.pd3_gain_count.grid(row=10, column=2, padx=0)
        self.pd3_gain_count.insert(0, "256")

        tk.Label(button_zone, text=constants.UV_DEVICE_SETTINGS_PI).grid(row=10, column=3, padx=0)
        self.pi_gain_count = ttkbs.Entry(button_zone, width=5)
        self.pi_gain_count.grid(row=10, column=4, padx=0)
        self.pi_gain_count.insert(0, "1023")

        #TODO: Not setting these magic values to defaults as these are DB-5 specific and needs more understanding.
        add_button(constants.UV_DEVICE_SETTINGS, lambda: run_command_with_spinner_buttons_info(
            partial(set_uv_device_settings.set_uv_device_settings, 
                    int(self.pd1_gain_count.get() or 0), 
                    int(self.pd2_gain_count.get() or 512),
                    int(self.pd3_gain_count.get() or 256), 
                    int(self.pi_gain_count.get() or 1023)), 
            self.output_box, self.toggle_frame, self.tab, self.buttons, set_hardware_status), 10)

        
    def _build_output_area(self):
        """Create output text box + toggle frame."""
        self.output_box = scrolledtext.ScrolledText(self.tab, width=75, height=10)
        self.output_box.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        self.output_box.config(state="disabled")

        self.toggle_frame = tk.Frame(self.tab)
        self.toggle_frame.grid(row=2, column=1, sticky="nsew", padx=10, pady=5)
