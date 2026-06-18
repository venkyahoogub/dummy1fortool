import tkinter as tk
import ttkbootstrap as ttkbs
from tkinter import scrolledtext
from tkinter import filedialog
from ttkbootstrap.constants import DANGER, WARNING
from functools import partial
from pbc import firmware_installer as pbc_firmware_installer
from hbc import firmware_installer as hbc_firmware_installer
from common_utilities import common_ui_info, constants
from common_utilities.log_config import logger
from model.ilink_model import set_hardware_status
from controller.ilink_controller import run_command_with_spinner_buttons_info


class FirmwareUpdaterTab:
    def __init__(self, parent):
        self.tab = ttkbs.Frame(parent)
        parent.add(self.tab, text=constants.FIRMWARE_UPDATER)

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

        def add_button(text, command, row, bootstyle=DANGER):
            btn = ttkbs.Button(
                button_zone,
                text=text,
                width=20,
                bootstyle=bootstyle,
                command=command,
            )
            btn.grid(row=row, column=0, pady=5, sticky="ew")
            self.buttons.append(btn)

        add_button(
            constants.UPDATE_FW_PBC_FROM_FILE,
            lambda: self._select_and_install(
                pbc_firmware_installer.install_firmware_updates
            ),
            4,
            bootstyle=WARNING
        )

        add_button(
            constants.UPDATE_FW_HBC_FROM_FILE,
            lambda: self._select_and_install(
                hbc_firmware_installer.install_firmware_updates
            ),
            8,
            bootstyle=WARNING
        )

    def _build_output_area(self):
        """Create output text box + toggle frame."""
        self.output_box = scrolledtext.ScrolledText(self.tab, width=75, height=10)
        self.output_box.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        self.output_box.config(state="disabled")

        self.toggle_frame = tk.Frame(self.tab)
        self.toggle_frame.grid(row=2, column=1, sticky="nsew", padx=10, pady=5)

    def _select_and_install(self, install_function):
        file_path = filedialog.askopenfilename(
            title=constants.SELECT_BINARY,
            filetypes=[("Binary Files", "*.bin"), ("All Files", "*.*")]
        )

        if not file_path:
            return  # User cancelled the file selection

        run_command_with_spinner_buttons_info(
            partial(install_function, file_path),
            self.output_box,
            self.toggle_frame,
            self.tab,
            self.buttons,
            set_hardware_status,
        )