import tkinter as tk
import ttkbootstrap as ttkbs
from tkinter import scrolledtext
from ttkbootstrap.constants import SUCCESS
from functools import partial
from hbc import (
    set_motor_fan_controls,
)
from common_utilities import common_ui_info, constants
from common_utilities.log_config import logger
from model.ilink_model import set_hardware_status
from controller.ilink_controller import run_command_with_spinner_buttons_info


class MotorFanTab:
    def __init__(self, parent):
        self.tab = ttkbs.Frame(parent)
        parent.add(self.tab, text="Motor/Fan Controls")

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
        """Create the button panel and commands for Motor/Fan controls."""
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
        
        # --- Adding 3 text box to get user input for motor movements ---
        tk.Label(button_zone, text=constants.MOVE_MOTORS_X).grid(row=0, column=1, padx=0)
        self.move_x_mm = ttkbs.Entry(button_zone, width=5)
        self.move_x_mm.grid(row=0, column=2, padx=0)
        self.move_x_mm.insert(0, "0")

        tk.Label(button_zone, text=constants.MOVE_MOTORS_Y).grid(row=1, column=1, padx=0)
        self.move_y_mm = ttkbs.Entry(button_zone, width=5)
        self.move_y_mm.grid(row=1, column=2, padx=0)
        self.move_y_mm.insert(0, "0")

        tk.Label(button_zone, text=constants.MOVE_MOTORS_Z).grid(row=2, column=1, padx=0)
        self.move_z_mm = ttkbs.Entry(button_zone, width=5)
        self.move_z_mm.grid(row=2, column=2, padx=0)
        self.move_z_mm.insert(0, "0")

        add_button(constants.MOVE_MOTORS, lambda: run_command_with_spinner_buttons_info(
            partial(set_motor_fan_controls.move_motor_controls, 
                    round(float(self.move_x_mm.get() or 0), 1),  # +/- 0.0 to 10.0mm
                    round(float(self.move_y_mm.get() or 0), 1),  # +/- 0.0 to 10.0mm
                    round(float(self.move_z_mm.get() or 0), 1)), # +/- 0.0 to 10.0mm
            self.output_box, self.toggle_frame, self.tab, self.buttons, set_hardware_status), 2)

        # --- Adding controls to home motors ---
        add_button(constants.HOME_MOTOR_CONTROLS,lambda: run_command_with_spinner_buttons_info(
            partial(set_motor_fan_controls.home_motors),
            self.output_box, self.toggle_frame, self.tab, self.buttons, set_hardware_status),3)
        
        # --- Adding controls to set fan controls ---
        self.uv_fan_var = tk.BooleanVar(value=True)   # default value
        self.head_fan_var = tk.BooleanVar(value=True)

        # UV Fan
        tk.Label(button_zone, text=constants.UV_FAN).grid(row=4, column=1, padx=0)

        tk.Radiobutton(button_zone, text="On", 
                    variable=self.uv_fan_var, value=True).grid(row=4, column=2)

        tk.Radiobutton(button_zone, text="Off", 
                    variable=self.uv_fan_var, value=False).grid(row=4, column=3)

        # Head Fan
        tk.Label(button_zone, text=constants.HEAD_FAN).grid(row=5, column=1, padx=0)

        tk.Radiobutton(button_zone, text="On", 
                    variable=self.head_fan_var, value=True).grid(row=5, column=2)

        tk.Radiobutton(button_zone, text="Off", 
                    variable=self.head_fan_var, value=False).grid(row=5, column=3)

        # Button
        add_button(constants.SET_FAN_CONTROLS,lambda: run_command_with_spinner_buttons_info(
            partial(set_motor_fan_controls.set_fan_controls,
                    self.uv_fan_var.get(),
                    self.head_fan_var.get()
            ),self.output_box, self.toggle_frame, self.tab, self.buttons, set_hardware_status),5)

    def _build_output_area(self):
        """Create output text box + toggle frame."""
        self.output_box = scrolledtext.ScrolledText(self.tab, width=75, height=10)
        self.output_box.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        self.output_box.config(state="disabled")

        self.toggle_frame = tk.Frame(self.tab)
        self.toggle_frame.grid(row=2, column=1, sticky="nsew", padx=10, pady=5)
