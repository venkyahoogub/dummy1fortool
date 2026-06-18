import sys
import os
import tkinter as tk
from tkinter import simpledialog
import ttkbootstrap as ttkbs
from source.common_utilities.text_redirector import TextRedirector
from source.common_utilities import constants
from source.common_utilities import startup_log_listener
from view.ilink_view import resource_path
from view.pbc_tab import PbcTab
from view.hbc_tab import HbcTab
from view.uvc_tab import UvcTab
from view.uvc_camera_tab import UvcCameraTab
from view.camera_tab import CameraTab
from view.treatment_tab import TreatmentTab
from view.distance_sensor_tab import DistanceSensorTab
from view.motor_fan_tab import MotorFanTab
from view.firmware_update_tab import FirmwareUpdaterTab
from view.log_tab import LoggingTab
from pbc import get_toolversion


class IlinkTestToolGui:
    def __init__(self):
        self.root = ttkbs.Window(themename="cyborg")
        ilink_test_tool_version = get_toolversion.get_toolversion_info()
        self.root.title(f"iLink Engineering Tool - {ilink_test_tool_version}")
        self.root.geometry("1000x1000")

        self._setup_layout()
        self._setup_tabs()
        self._setup_icon()

        # Redirect stdout/stderr to PBC output by default
        sys.stdout = TextRedirector(self.pbc_tab.output_box)
        sys.stderr = TextRedirector(self.pbc_tab.output_box)

        # Init the log listener so its ready from the first time the ilink tool launches.
        startup_log_listener.initialize_log_listener()

    def _setup_layout(self):
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=0)
        self.root.columnconfigure(1, weight=0)

        self.main_frame = ttkbs.Frame(self.root)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)

    def _setup_tabs(self):
        self.tab_control = ttkbs.Notebook(self.main_frame)
        self.tab_control.grid(row=0, column=0, sticky="nsew")

        self.pbc_tab = PbcTab(self.tab_control)
        self.hbc_tab = HbcTab(self.tab_control)
        self.uvc_tab = UvcTab(self.tab_control)
        self.camera_tab = CameraTab(self.tab_control)
        self.uvc_camera_tab = UvcCameraTab(self.tab_control)
        self.treatment_tab = TreatmentTab(self.tab_control)
        self.distance_tab = DistanceSensorTab(self.tab_control)
        self.motor_fan_tab = MotorFanTab(self.tab_control)
        self.log_tab = LoggingTab(self.tab_control)

        self.fw_update_tab = FirmwareUpdaterTab(self.tab_control)

        # Track auth state
        self._fw_authenticated = False

        # Store FW tab index
        self._fw_tab_index = self.tab_control.index("end") - 1

        # Track previous tab
        self._previous_tab_index = 0

        # Bind tab change event
        self.tab_control.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def _on_tab_changed(self, event):
        selected_index = self.tab_control.index(self.tab_control.select())

        # If user clicked Firmware tab and not authenticated
        if selected_index == self._fw_tab_index and not self._fw_authenticated:

            # Revert immediately to previous tab
            self.tab_control.select(self._previous_tab_index)

            # Defer the authentication dialog to the next event loop iteration
            self.root.after(0, self._show_auth_dialog)
            return

        # Update previous tab
        self._previous_tab_index = self.tab_control.index(self.tab_control.select())

    def _show_auth_dialog(self):
        if self._authenticate_fw_tab():
            self._fw_authenticated = True
            self.tab_control.select(self._fw_tab_index)

    def _authenticate_fw_tab(self):
        expected = os.environ.get("FW_ADMIN_PASSWORD")
        if not expected:
            return False

        while True:
            password = simpledialog.askstring(
                constants.FIRMWARE_UPDATER,
                constants.PASSWORD_ENTRY,
                show="*",
                parent=self.root,
            )

            if password is None:
                return False
            if password == expected:
                return True
            

    def _setup_icon(self):
        icon_path = resource_path("resources/GlaukosRLogo.png")
        img = tk.PhotoImage(file=str(icon_path))
        img_small = img.subsample(4, 4)

        image_frame = ttkbs.Frame(self.root)
        image_frame.grid(row=2, column=2, sticky="se")
        image_label = ttkbs.Label(image_frame, image=img_small)
        image_label.image = img_small
        image_label.grid(row=0, column=0, padx=10, pady=10, sticky="se")

    def run(self):
        self.root.mainloop()


def main():
    app = IlinkTestToolGui()
    app.run()


if __name__ == "__main__":
    main()