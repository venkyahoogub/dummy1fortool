import tkinter as tk
import ttkbootstrap as ttkbs
from tkinter import scrolledtext
from ttkbootstrap.constants import SUCCESS
from functools import partial
from hbc import (
    distance_sensor_controls,
)
from common_utilities import common_ui_info, constants
from common_utilities.log_config import logger
from model.ilink_model import set_hardware_status
from controller.ilink_controller import run_command_with_spinner_buttons_info


class DistanceSensorTab:
    def __init__(self, parent):
        self.tab = ttkbs.Frame(parent)
        parent.add(self.tab, text="Distance Sensor")

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
        """Create the button panel and commands for Distance sensor."""
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
        
        # --- Adding 2 text box to get user input for setting distance sensors ---
        tk.Label(button_zone, text=constants.GAIN).grid(row=0, column=1, padx=0)
        self.gain = ttkbs.Entry(button_zone, width=5)
        self.gain.grid(row=0, column=2, padx=0)
        self.gain.insert(0, "1")

        tk.Label(button_zone, text=constants.OFFSET).grid(row=0, column=3, padx=0)
        self.offset = ttkbs.Entry(button_zone, width=5)
        self.offset.grid(row=0, column=4, padx=0)
        self.offset.insert(0, "0")

        add_button(constants.SET_DISTANCE_SENSOR_SETTINGS, lambda: run_command_with_spinner_buttons_info(
            partial(distance_sensor_controls.set_distance_sensor_settings, 
                    int(self.gain.get() or 1), 
                    int(self.offset.get() or 0)), 
            self.output_box, self.toggle_frame, self.tab, self.buttons, set_hardware_status), 0)
        
        # --- Adding 1 text box to get user input for distance sensor ranging runtime ---
        tk.Label(button_zone, text=constants.RUNTIME).grid(row=2, column=1, padx=0)
        self.runtime = ttkbs.Entry(button_zone, width=5)
        self.runtime.grid(row=2, column=2, padx=0)
        self.runtime.insert(0, "5")

        add_button(constants.START_DISTANCE_SENSOR_RANGING, lambda: run_command_with_spinner_buttons_info(
            partial(distance_sensor_controls.distance_sensor_start_stop_ranging,
            int(self.runtime.get() or 5)), 
            self.output_box, self.toggle_frame, self.tab, self.buttons, set_hardware_status), 2)
        
    def _build_output_area(self):
        """Create output text box + toggle frame."""
        self.output_box = scrolledtext.ScrolledText(self.tab, width=75, height=10)
        self.output_box.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        self.output_box.config(state="disabled")

        self.toggle_frame = tk.Frame(self.tab)
        self.toggle_frame.grid(row=2, column=1, sticky="nsew", padx=10, pady=5)
