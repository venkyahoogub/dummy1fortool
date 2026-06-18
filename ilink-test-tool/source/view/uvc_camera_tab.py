import tkinter as tk
import ttkbootstrap as ttkbs
import threading
import cv2
import os, sys
import queue
from PIL import Image, ImageTk
from common_utilities.log_config import logger
from common_utilities import constants
from ttkbootstrap.constants import SUCCESS, SECONDARY, PRIMARY, INDETERMINATE, DANGER, INFO, NORMAL, DISABLED
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uvc")))
from uvc.CameraService import CameraService
from uvc.ConnectToUVCNetcat import NetcatClient


class UvcCameraTab:
    def __init__(self, parent):
        self.tab = ttkbs.Frame(parent)
        parent.add(self.tab, text="UVC Camera")

        # Layout configuration
        self.tab.rowconfigure(0, weight=0)
        self.tab.rowconfigure(1, weight=1)
        self.tab.rowconfigure(2, weight=0)
        self.tab.rowconfigure(3, weight=0)  # Row for progress bar
        self.tab.columnconfigure(0, weight=1)

        # Video area
        self.video_outer = tk.Frame(self.tab, bg=constants.BG_COLOR_GREEN, bd=0)
        self.video_outer.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.video_outer.rowconfigure(0, weight=10)
        self.video_outer.columnconfigure(0, weight=10)

        # Inner frame holds the actual video label
        self.video_frame = tk.Frame(self.video_outer, bg=constants.BG_COLOR_BLACK)
        self.video_frame.grid(row=0, column=0, padx=3, pady=3, sticky="nsew")  # 3px inner padding to show green border
        self.video_frame.rowconfigure(0, weight=1)
        self.video_frame.columnconfigure(0, weight=1)

        # Label for displaying frames or default image
        self.video_label = tk.Label(self.video_frame, bg=constants.BG_COLOR_BLACK)
        self.video_label.grid(row=0, column=0, sticky="nsew")

        # Button row (Connect / Left / Right / Wide / Stop)
        self.button_frame = ttkbs.Frame(self.tab)
        self.button_frame.grid(row=0, column=0, pady=10, sticky="w")

        # UVC Netcat Connect button and status
        self.connect_button = ttkbs.Button(
            self.button_frame,
            text=constants.UVC_NETCAT,
            width=10,
            bootstyle=INFO,
            command=self.on_connect_pressed,
        )
        self.connect_button.grid(row=0, column=0, padx=(0, 4))

        # Camera selection buttons (disabled until netcat connected)
        self.left_button = ttkbs.Button(
            self.button_frame,
            text=constants.CAMERA_STRING_LEFT,
            width=10,
            bootstyle=PRIMARY,
            command=lambda: self.on_camera_cmd_pressed(constants.CAMERA_STRING_LEFT),
            state=DISABLED,
        )
        self.left_button.grid(row=1, column=0, padx=(0, 2), pady=(10, 0))
        
        self.right_button = ttkbs.Button(
            self.button_frame,
            text=constants.CAMERA_STRING_RIGHT,
            width=10,
            bootstyle=PRIMARY,
            command=lambda: self.on_camera_cmd_pressed(constants.CAMERA_STRING_RIGHT),
            state=DISABLED,
        )
        self.right_button.grid(row=1, column=1, padx=(0, 2), pady=(10, 0))

        self.wide_button = ttkbs.Button(
            self.button_frame,
            text=constants.CAMERA_STRING_WIDE,
            width=10,
            bootstyle=PRIMARY,
            command=lambda: self.on_camera_cmd_pressed(constants.CAMERA_STRING_WIDE),
            state=DISABLED,
        )
        self.wide_button.grid(row=1, column=2, padx=(0, 2), pady=(10, 0))

        self.uv_on_button = ttkbs.Button(
            self.button_frame,
            text=constants.UV_ON,
            width=10,
            bootstyle=PRIMARY,
            command=lambda: self.on_netcat_cmd_pressed(constants.TURN_UV_ON),
            state=DISABLED,
        )
        self.uv_on_button.grid(row=2, column=1, padx=(0, 2), pady=(10, 0))

        self.uv_off_button = ttkbs.Button(
            self.button_frame,
            text=constants.UV_OFF,
            width=10,
            bootstyle=PRIMARY,
            command=lambda: self.on_netcat_cmd_pressed(constants.TURN_UV_OFF),
            state=DISABLED,
        )
        self.uv_off_button.grid(row=2, column=2, padx=(0, 2), pady=(10, 0))


        self.stop_button = ttkbs.Button(
            self.button_frame,
            text=constants.STOP_STREAM,
            width=10,
            bootstyle=SECONDARY,
            command=self.stop_stream,
        )
        self.stop_button.grid(row=3, column=0, padx=(0, 2), pady=(10, 0))

        # Indeterminate progress bar for connect / command activity
        self.netcat_progress = ttkbs.Progressbar(
            self.button_frame, 
            mode=INDETERMINATE, 
            length=80
        )
        # Initially hidden
        self.netcat_progress.grid(row=0, column=5, padx=(0, 2), pady=(10, 0))

        # Status label for netcat connection/command feedback
        self.netcat_status_label = ttkbs.Label(self.button_frame, text="", bootstyle=SECONDARY)
        self.netcat_status_label.grid(row=0, column=1, padx=(8, 12))

        # Camera client state
        self.client = None
        self.thread = None
        self.running = False

        # Netcat client state
        self.netcat_client = None
        self.netcat_lock = threading.Lock()

        self.frame_queue = queue.Queue(maxsize=2)
        self.current_photo = None  # keep PhotoImage reference
        self.default_pil = None    # PIL Image for the default idle image
        self.default_photo = None  # PhotoImage currently shown as default (resized)

        # Poll interval
        self.poll_interval = 30  # ms (Based on neo_uic polling)

        # Load default image for idle state
        self._load_default_image()
        self._show_default_image()

        # Bind resize so default image can be resized to fit when the widget changes size
        self.video_label.bind("<Configure>", self._on_label_configure)

    def on_connect_pressed(self):
        """User clicked 'UVC 11003' to connect to the Netcat UVC CLI."""
        try:
            if NetcatClient is None:
                self._set_netcat_status("Netcat client not available", error=True)
                return
            self.connect_button.config(state=DISABLED)
            self._start_progress("Waiting to connect to the UVC netcat client...")
            thr = threading.Thread(target=self._connect_netcat_thread, daemon=True)
            thr.start()
        except Exception as e:
                logger.error(f"on_connect_pressed error: {e}")

    def _connect_netcat_thread(self):
        try:
            with self.netcat_lock:
                if self.netcat_client is None:
                    self.netcat_client = NetcatClient(
                        host=constants.UVC_IP,
                        port=constants.UVC_CLI_PORT,
                        timeout=5 * 60
                    )
            ok = self.netcat_client.connect()
        except Exception as e:
            logger.error(f"UvcCameraTab: Netcat connect thread error: {e}")
            ok = False
        self.video_label.after(0, lambda: self._on_netcat_connected(ok))

    def _on_netcat_connected(self, success):
        try:
            self._stop_progress()
            if success:
                self._set_netcat_status("Connected to UVC", success=True)
                self._enable_camera_buttons(True)
            else:
                self._set_netcat_status("Failed to connect to UVC", error=True)
                self._enable_camera_buttons(False)
                self.connect_button.config(state=NORMAL)
        except Exception as e:
            logger.error(f"Error occured with netcat connection: {e}")

    def _enable_camera_buttons(self, enable):
        try:
            state = NORMAL if enable else DISABLED
            self.left_button.config(state=state)
            self.right_button.config(state=state)
            self.wide_button.config(state=state)
            self.uv_on_button.config(state=state)
            self.uv_off_button.config(state=state)
        except Exception as e:
            logger.error(f"Error occured button enablement: {e}")

    def _start_progress(self, text=""):
        try:
            self.netcat_status_label.config(text=text)
            self.netcat_progress.grid(row=0, column=5, padx=(0, 2), pady=(10, 0))
            self.netcat_progress.start(10)
        except Exception as e:
            logger.error(f"UvcCameraTab: start_progress failed: {e}")

    def _stop_progress(self):
        try:
            self.netcat_progress.stop()
        except Exception as e:
            logger.error(f"UvcCameraTab: stop_progress failed: {e}")

    def _set_netcat_status(self, text, success=False, error=False):
        style = SECONDARY
        if success:
            style = SUCCESS
        if error:
            style = DANGER
        try:
            self.netcat_status_label.config(text=text, bootstyle=style)
        except Exception as e:
            self.netcat_status_label.config(text=text)
            logger.error(f"Error occured: _set_netcat_status {e}")

    def on_netcat_cmd_pressed(self, cmd):
        """
        Called when user presses uv on/off buttons.
        """
        try:
            if self.netcat_client is None:
                self._set_netcat_status("Not connected", error=True)
                return
            self.netcat_status_label.config(text=f"Sending '{cmd}' to UVC...", bootstyle=SECONDARY)
            thr = threading.Thread(target=lambda: self._camera_cmd_thread(cmd), daemon=True)
            thr.start()
        except Exception as e:
            logger.error(f"Exeception occured with netcat press button: {e}")

    def on_camera_cmd_pressed(self, cmd):
        """
        Called when user presses left/right/wide buttons.
        """
        try:
            if self.netcat_client is None:
                self._set_netcat_status("Not connected", error=True)
                return
            self._enable_camera_buttons(False)
            self._start_progress(f"Sending '{cmd}' to UVC...")
            thr = threading.Thread(target=lambda: self._camera_cmd_thread(cmd), daemon=True)
            thr.start()
        except Exception as e:
            logger.error(f"Exeception occured with camera press button: {e}")

    def _camera_cmd_thread(self, cmd):
        ok = False
        try:
            with self.netcat_lock:
                nc = self.netcat_client
                if not nc or not nc.connected:
                    ok = False
                else:
                    if cmd == constants.CAMERA_STRING_LEFT:
                        ok = nc.left_no_reconnect()
                    elif cmd == constants.CAMERA_STRING_RIGHT:
                        ok = nc.right_no_reconnect()
                    elif cmd == constants.CAMERA_STRING_WIDE:
                        ok = nc.wide_no_reconnect()
                    else:
                        ok = nc.send_command(cmd, expected_response="", reconnect_if_needed=False)
        except Exception as e:
            logger.error(f"UvcCameraTab: error sending camera cmd '{cmd}': {e}")
            ok = False
        self.video_label.after(0, lambda: self._on_camera_cmd_result(cmd, ok))

    def _cmd_to_camera_side(self, cmd):
        """Map clicked command to CameraService camera_side constant."""
        if cmd == constants.CAMERA_STRING_LEFT:
            return constants.CAMERA_STRING_LEFT
        if cmd == constants.CAMERA_STRING_RIGHT:
            return constants.CAMERA_STRING_RIGHT
        # Default is auto
        return constants.CAMERA_STRING_AUTO

    def _on_camera_cmd_result(self, cmd, success):
        try:
            self._stop_progress()
            if success:
                self._set_netcat_status(f"'{cmd}' acknowledged", success=True)
                try:
                    camera_side = self._cmd_to_camera_side(cmd)
                    self.start_stream(camera_side=camera_side)
                except Exception as e:
                    logger.error(f"UvcCameraTab: start_stream after '{cmd}' failed: {e}")
            else:
                self._set_netcat_status(f"'{cmd}' failed", error=True)
            still_connected = getattr(self.netcat_client, "connected", False)
            self._enable_camera_buttons(still_connected)
            if not still_connected:
                # allow reconnect attempts
                self.connect_button.config(state=NORMAL)
        except Exception as e:
            logger.error(f"Exeception occured with camera streaming: {e}")

    def _load_default_image(self):
        try:
            candidates = [
                os.path.join(os.path.dirname(__file__), "..", "resources", "noVideoStreaming.png")
            ]
            pil_img = None
            for p in candidates:
                try:
                    p_abs = os.path.abspath(p)
                    if os.path.exists(p_abs):
                        pil_img = Image.open(p_abs).convert("RGBA")
                        logger.info(f"UvcCameraTab: loaded default image from {p_abs}")
                        break
                except Exception:
                    logger.error(f"UvcCameraTab: failed to open image at {p}")

            if pil_img is None:
                logger.warning("UvcCameraTab: default resource image not found; using generated placeholder.")
                pil_img = Image.new("RGBA", (500, 500), (60, 60, 60, 255))

            self.default_pil = pil_img
            self.default_photo = None
        except Exception as e:
            logger.error(f"Image loading failed due to: {e}")

    def _show_default_image(self):
        """Resize the default_pil to the label size (if available) and show it."""
        if self.default_pil is None:
            self.video_label.config(image="", bg=constants.BG_COLOR_BLACK)
            self.current_photo = None
            return
        target_size = (178, 178)

        try:
            pil_resized = self.default_pil.resize(target_size)
            photo = ImageTk.PhotoImage(pil_resized)
            self.default_photo = photo
            self.current_photo = photo
            self.video_label.config(image=photo)
        except Exception as e:
            logger.error(f"UvcCameraTab: failed to resize/create PhotoImage for default image {e}")
            # fallback: show no image
            self.video_label.config(image="")
            self.current_photo = None

    def _on_label_configure(self):
        """Called when the label is resized; update default image size if not streaming."""
        try:
            if not self.running:
                self._show_default_image()
        except Exception as e:
            logger.error(f"Label configuration failed: {e}")

    def _frame_callback(self, img_bgr):
        """
        Called from CameraService thread. Enqueue the frame for the GUI thread to consume.
        """
        try:
            if self.frame_queue.full():
                try:
                    self.frame_queue.get_nowait()
                except Exception:
                    pass
            self.frame_queue.put_nowait(img_bgr)
        except Exception:
            logger.error("UvcCameraTab: Failed to enqueue frame")

    def start_stream(self, camera_side=constants.CAMERA_STRING_LEFT):
        try:
            if self.running:
                # Already running: if you want to restart for a different side, implement stop+start here.
                return

            self.client = CameraService(
                constants.UVC_IP,
                constants.UVC_VIDEO_STREAM_PORT,
                constants.CAMERA_COMMAND_LEFT,
                frame_callback=self._frame_callback
            )

            self.thread = threading.Thread(
                target=lambda: self.client.run_blocking(camera_side=camera_side),
                daemon=True
            )
            self.thread.start()
            self._wait_for_client_running()

        except Exception:
            logger.error("UvcCameraTab: error starting stream")

    def _wait_for_client_running(self, timeout_ms=5000, check_interval=100):
        max_checks = max(1, timeout_ms // check_interval) # to avoid infinite loop

        def _check(count=0):
            try:
                if self.client is None:
                    self._show_default_image()
                    return
                
                if getattr(self.client, "running", False):
                    self.running = True
                    self._schedule_frame_poll()
                    logger.info("UvcCameraTab: camera client connected; started frame polling.")
                    return

                if self.thread and not self.thread.is_alive():
                    logger.warning("UvcCameraTab: camera thread exited before becoming running.")
                    self.client = None
                    self._show_default_image()
                    return

                if count >= max_checks:
                    logger.warning("UvcCameraTab: timeout waiting for camera to become running.")
                    self._show_default_image()
                    return

                self.video_label.after(check_interval, lambda: _check(count + 1))
            except Exception as e:
                logger.error(f"Error while waiting for camera client to start: {e}")
                self._show_default_image()

        # initial check
        _check()

    def _schedule_frame_poll(self):
        self.video_label.after(self.poll_interval, self._poll_frame_queue)

    def _poll_frame_queue(self):
        try:
            updated = False
            while not self.frame_queue.empty():
                img_bgr = self.frame_queue.get_nowait()
                # Convert to RGB
                try:
                    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
                except Exception:
                    img_rgb = img_bgr[..., ::-1]

                pil_img = Image.fromarray(img_rgb)

                lbl_w = self.video_label.winfo_width()
                lbl_h = self.video_label.winfo_height()
                if lbl_w > 10 and lbl_h > 10:
                    try:
                        pil_img = pil_img.resize((lbl_w, lbl_h), Image.ANTIALIAS)
                    except Exception:
                        pass

                photo = ImageTk.PhotoImage(pil_img)
                self.current_photo = photo
                self.video_label.config(image=photo)
                updated = True

        except Exception:
            logger.error("UvcCameraTab: Error updating video frame")
        finally:
            if self.running:
                self._schedule_frame_poll()
            else:
                self._show_default_image()

    def stop_stream(self):
        """
        Stops the CameraService and returns to idle/default image.
        """
        try:
            if not self.running and not self.client:
                self._show_default_image()
                return
            self.running = False
            self._show_default_image()
            try:
                while not self.frame_queue.empty():
                    self.frame_queue.get_nowait()
            except Exception:
                pass

            # Disconnect CameraService if present
            if self.client:
                try:
                    asyncio = __import__("asyncio")
                    try:
                        asyncio.run(self.client.disconnect())
                    except Exception:
                        try:
                            if getattr(self.client, "sock", None):
                                self.client.sock.close()
                        except Exception:
                            pass
                except Exception:
                    pass
                self.client = None

            logger.info("Camera stream stopped and client disconnected.")
        except Exception:
            logger.error("UvcCameraTab: Error stopping camera stream")