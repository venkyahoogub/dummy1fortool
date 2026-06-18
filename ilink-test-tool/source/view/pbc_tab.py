import tkinter as tk
import ttkbootstrap as ttkbs
from tkinter import scrolledtext
from ttkbootstrap.constants import SUCCESS, DANGER
from functools import partial
from pbc import ( 
    get_about, 
    get_status, 
    get_controls, 
    get_devicelimits,
    led_controls,
    usb_power_controls,
    set_brake_fan_controls,
    reset_to_default,
)
from common_utilities import common_ui_info, constants
from common_utilities.log_config import logger
from model.ilink_model import set_hardware_status
from controller.ilink_controller import run_command_with_spinner_buttons_info


class PbcTab:
    def __init__(self, parent):
        self.tab = ttkbs.Frame(parent)
        parent.add(self.tab, text="PBC")

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
        """Create the button panel and commands for PBC."""
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

        add_button(constants.ABOUT, lambda: run_command_with_spinner_buttons_info(
            get_about.get_about_info, self.output_box, self.toggle_frame, self.tab, self.buttons, set_hardware_status), 0)

        add_button(constants.STATUS, lambda: run_command_with_spinner_buttons_info(
            get_status.get_status_info, self.output_box, self.toggle_frame, self.tab, self.buttons, set_hardware_status), 1)

        add_button(constants.CONTROLS, lambda: run_command_with_spinner_buttons_info(
            get_controls.get_controls_info, self.output_box, self.toggle_frame, self.tab, self.buttons, set_hardware_status), 3)
        
        add_button(constants.DEVICE_LIMITS, lambda: run_command_with_spinner_buttons_info(
            get_devicelimits.get_devicelimits_info, self.output_box, self.toggle_frame, self.tab, self.buttons, set_hardware_status), 4)
        
        # --- Brake controls ---
        self.brake_var = tk.BooleanVar(value=True)   # default value
        tk.Label(button_zone, text=constants.BRAKE).grid(row=5, column=1, padx=0)

        tk.Radiobutton(button_zone, text="On", 
                    variable=self.brake_var, value=True).grid(row=5, column=2)

        tk.Radiobutton(button_zone, text="Off", 
                    variable=self.brake_var, value=False).grid(row=5, column=3)

        # Button
        add_button(constants.PBC_BRAKE_CONTROLS,lambda: run_command_with_spinner_buttons_info(
            partial(set_brake_fan_controls.brake_controls,
                    self.brake_var.get()
            ),self.output_box, self.toggle_frame, self.tab, self.buttons, set_hardware_status),5)

        # --- Fan controls ---
        self.fan_var = tk.BooleanVar(value=True)   # default value
        tk.Label(button_zone, text=constants.FAN).grid(row=6, column=1, padx=0)

        tk.Radiobutton(button_zone, text="On", 
                    variable=self.fan_var, value=True).grid(row=6, column=2)

        tk.Radiobutton(button_zone, text="Off", 
                    variable=self.fan_var, value=False).grid(row=6, column=3)

        # Button
        add_button(constants.PBC_FAN_CONTROLS,lambda: run_command_with_spinner_buttons_info(
            partial(set_brake_fan_controls.set_fan_controls,
                    self.fan_var.get()
            ),self.output_box, self.toggle_frame, self.tab, self.buttons, set_hardware_status),6)

        # --- LED controls ---
        # --- static
        tk.Label(button_zone, text=constants.LED_RED).grid(row=8, column=1, padx=0)
        self.led_red_s = ttkbs.Entry(button_zone, width=5)
        self.led_red_s.grid(row=8, column=2, padx=0)
        self.led_red_s.insert(0, "0")

        tk.Label(button_zone, text=constants.LED_GREEN).grid(row=9, column=1, padx=0)
        self.led_green_s = ttkbs.Entry(button_zone, width=5)
        self.led_green_s.grid(row=9, column=2, padx=0)
        self.led_green_s.insert(0, "0")

        tk.Label(button_zone, text=constants.LED_BLUE).grid(row=10, column=1, padx=0)
        self.led_blue_s = ttkbs.Entry(button_zone, width=5)
        self.led_blue_s.grid(row=10, column=2, padx=0)
        self.led_blue_s.insert(0, "0")

        add_button(constants.STATIC_COLOR_EFFECT, lambda: run_command_with_spinner_buttons_info(
            partial(led_controls.start_static_color_effect, 
                    int(self.led_red_s.get()),
                    int(self.led_green_s.get()),
                    int(self.led_blue_s.get())),
            self.output_box, self.toggle_frame, self.tab, self.buttons, set_hardware_status), 10)

        # --- pulsed
        tk.Label(button_zone, text=constants.LED_RED).grid(row=12, column=1, padx=0)
        self.led_red_p = ttkbs.Entry(button_zone, width=5)
        self.led_red_p.grid(row=12, column=2, padx=0)
        self.led_red_p.insert(0, "0")

        tk.Label(button_zone, text=constants.LED_GREEN).grid(row=13, column=1, padx=0)
        self.led_green_p = ttkbs.Entry(button_zone, width=5)
        self.led_green_p.grid(row=13, column=2, padx=0)
        self.led_green_p.insert(0, "0")

        tk.Label(button_zone, text=constants.LED_BLUE).grid(row=14, column=1, padx=0)
        self.led_blue_p = ttkbs.Entry(button_zone, width=5)
        self.led_blue_p.grid(row=14, column=2, padx=0)
        self.led_blue_p.insert(0, "0")

        tk.Label(button_zone, text=constants.PULSE_PERIOD).grid(row=15, column=1, padx=0)
        self.pulse_period_ms_p = ttkbs.Entry(button_zone, width=5)
        self.pulse_period_ms_p.grid(row=15, column=2, padx=0)
        self.pulse_period_ms_p.insert(0, "0")

        add_button(constants.PULSED_COLOR_EFFECT, lambda: run_command_with_spinner_buttons_info(
            partial(led_controls.start_pulse_color_effect, 
                    int(self.led_red_p.get()), 
                    int(self.led_green_p.get()),
                    int(self.led_blue_p.get()),
                    int(self.pulse_period_ms_p.get())),
            self.output_box, self.toggle_frame, self.tab, self.buttons, set_hardware_status), 15)
        # --- rainbow
        add_button(constants.RAINBOW_COLOR_EFFECT, lambda: run_command_with_spinner_buttons_info(
            partial(led_controls.start_rainbow_color_effect),
            self.output_box, self.toggle_frame, self.tab, self.buttons, set_hardware_status), 17)

        # --- pulsed rainbow
        add_button(constants.CHASING_RAINBOW_COLOR_EFFECT, lambda: run_command_with_spinner_buttons_info(
            partial(led_controls.start_chasing_rainbow_color_effect),
            self.output_box, self.toggle_frame, self.tab, self.buttons, set_hardware_status), 18)
        
        # --- turn off all leds
        add_button(constants.STOP_ALL_LEDS, lambda: run_command_with_spinner_buttons_info(
            partial(led_controls.start_static_color_effect,0,0,0),
            self.output_box, self.toggle_frame, self.tab, self.buttons, set_hardware_status), 19)


        # --- USB power controls ---
        self.p1_c1 = tk.BooleanVar(value=True)   # default value
        tk.Label(button_zone, text=constants.USB_PORT1_CH1).grid(row=20, column=1, padx=0)
        tk.Radiobutton(button_zone, text="On", 
                    variable=self.p1_c1, value=True).grid(row=20, column=2)
        tk.Radiobutton(button_zone, text="Off", 
                    variable=self.p1_c1, value=False).grid(row=20, column=3)

        self.p2_c1 = tk.BooleanVar(value=True)   # default value
        tk.Label(button_zone, text=constants.USB_PORT2_CH1).grid(row=21, column=1, padx=0)
        tk.Radiobutton(button_zone, text="On", 
                    variable=self.p2_c1, value=True).grid(row=21, column=2)
        tk.Radiobutton(button_zone, text="Off", 
                    variable=self.p2_c1, value=False).grid(row=21, column=3)

        self.p1_c2 = tk.BooleanVar(value=True)   # default value
        tk.Label(button_zone, text=constants.USB_PORT1_CH2).grid(row=22, column=1, padx=0)
        tk.Radiobutton(button_zone, text="On", 
                    variable=self.p1_c2, value=True).grid(row=22, column=2)
        tk.Radiobutton(button_zone, text="Off", 
                    variable=self.p1_c2, value=False).grid(row=22, column=3)

        self.p2_c2 = tk.BooleanVar(value=True)   # default values
        tk.Label(button_zone, text=constants.USB_PORT2_CH2).grid(row=23, column=1, padx=0)
        tk.Radiobutton(button_zone, text="On", 
                    variable=self.p2_c2, value=True).grid(row=23, column=2)
        tk.Radiobutton(button_zone, text="Off", 
                    variable=self.p2_c2, value=False).grid(row=23, column=3)

        add_button(constants.USB_CONTROL, lambda: run_command_with_spinner_buttons_info(
            partial(usb_power_controls.usb_controls, 
                    self.p1_c1.get(),
                    self.p2_c1.get(),
                    self.p1_c2.get(),
                    self.p2_c2.get()),
            self.output_box, self.toggle_frame, self.tab, self.buttons, set_hardware_status), 23)
    
        # --- Reset to default ---
        add_button(constants.RESET_PBC_TO_DEFAULT, lambda: run_command_with_spinner_buttons_info(
            partial(reset_to_default.reset_to_default),
            self.output_box, self.toggle_frame, self.tab, self.buttons, set_hardware_status), 25, bootstyle=DANGER)

    def _build_output_area(self):
        """Create output text box + toggle frame."""
        self.output_box = scrolledtext.ScrolledText(self.tab, width=75, height=10)
        self.output_box.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        self.output_box.config(state="disabled")

        self.toggle_frame = tk.Frame(self.tab)
        self.toggle_frame.grid(row=2, column=1, sticky="nsew", padx=10, pady=5)
