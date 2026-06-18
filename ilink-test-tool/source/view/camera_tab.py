import tkinter as tk
import ttkbootstrap as ttkbs
import threading
import cv2
import os, sys
import struct
import numpy as np
from PIL import Image, ImageTk
from common_utilities.log_config import logger
from common_utilities import constants
from ttkbootstrap.constants import SUCCESS, DANGER, SECONDARY, NORMAL, DISABLED

# Add path for calibration protobuf
pb2_path = os.path.join(os.path.dirname(__file__), '..', '..', 'neo-calibration-server-api', 'source', 'python')
sys.path.insert(0, pb2_path)
import calibration_server_api_pb2



class CameraTab:
    def __init__(self, parent):
        self.tab = ttkbs.Frame(parent)
        parent.add(self.tab, text="Camera")

        # Layout configuration
        self.tab.rowconfigure(0, weight=0)
        self.tab.rowconfigure(1, weight=1)
        self.tab.rowconfigure(2, weight=0)
        self.tab.columnconfigure(0, weight=1)

        # Button frame
        self.button_frame = ttkbs.Frame(self.tab)
        self.button_frame.grid(row=0, column=0, pady=10, sticky="w", padx=10)

        self.start_btn = ttkbs.Button(
            self.button_frame,
            text="START STREAM",
            width=20,
            bootstyle=SUCCESS,
            command=self.start_calibration_stream
        )
        self.start_btn.pack(side="left", padx=5)

        self.stop_btn = ttkbs.Button(
            self.button_frame,
            text="STOP STREAM",
            width=20,
            bootstyle=DANGER,
            command=self.stop_stream
        )
        self.stop_btn.pack(side="left", padx=5)

        # Status label
        self.status_label = ttkbs.Label(self.button_frame, text="Ready", font=("Arial", 10))
        self.status_label.pack(side="left", padx=20)

        # Video frame container
        video_container = ttkbs.Frame(self.tab)
        video_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        video_container.rowconfigure(0, weight=0)
        video_container.rowconfigure(1, weight=1)
        video_container.columnconfigure(0, weight=1)
        video_container.columnconfigure(1, weight=1)

        # Left camera
        left_label = ttkbs.Label(video_container, text="Left Camera", font=("Arial", 12, "bold"))
        left_label.grid(row=0, column=0, sticky="n", pady=5)

        # Left camera frame with border
        left_frame = tk.Frame(video_container, border=2, relief=tk.RAISED, bg="white")
        left_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        self.left_image_label = tk.Label(left_frame, background="black")
        self.left_image_label.pack(fill=tk.BOTH, expand=True)

        # Right camera
        right_label = ttkbs.Label(video_container, text="Right Camera", font=("Arial", 12, "bold"))
        right_label.grid(row=0, column=1, sticky="n", pady=5)

        # Right camera frame with border
        right_frame = tk.Frame(video_container, border=2, relief=tk.RAISED, bg="white")
        right_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

        self.right_image_label = tk.Label(right_frame, background="black")
        self.right_image_label.pack(fill=tk.BOTH, expand=True)

        # Streaming state
        self.cal_socket = None
        self.cal_streaming = False
        self.cal_thread = None

    def update_status(self, message):
        """Update status label"""
        self.status_label.config(text=message)
        self.tab.update()

    def start_calibration_stream(self):
        """Start streaming from calibration server"""
        if self.cal_streaming:
            self.update_status("Stream already running!")
            return

        self.start_btn.config(state=DISABLED)
        self.update_status("Connecting...")

        thread = threading.Thread(target=self._cal_stream_thread, daemon=True)
        thread.start()

    def _cal_stream_thread(self):
        """Connect and start calibration stream"""
        try:
            # Connect
            self.cal_socket = self._cal_connect("10.10.10.1", 50051)
            if not self.cal_socket:
                self.left_image_label.after(0, lambda: self.update_status("Failed to connect to calibration server"))
                self.left_image_label.after(0, lambda: self.start_btn.config(state=NORMAL))
                return

            self.update_status("Sending START_VIDEO_STREAM command...")

            # Send START_VIDEO_STREAM
            request = calibration_server_api_pb2.ToServer()
            request.start_video_stream.CopyFrom(calibration_server_api_pb2.StartVideoStream())
            self._cal_send_message(request)

            self.cal_streaming = True
            self.left_image_label.after(0, lambda: self.update_status("✓ Stream started!"))

            # Receive frames
            self._cal_receive_frames()

        except Exception as e:
            logger.error(f"Calibration stream error: {e}")
            self.left_image_label.after(0, lambda: self.update_status(f"Error: {e}"))
        finally:
            self.cal_streaming = False
            self.left_image_label.after(0, lambda: self.start_btn.config(state=NORMAL))

    def _cal_connect(self, host, port):
        """Connect to calibration server"""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
            logger.info(f"Connected to calibration server at {host}:{port}")
            return sock
        except Exception as e:
            logger.error(f"Failed to connect to calibration server: {e}")
            return None

    def _cal_send_message(self, message):
        """Send protobuf message"""
        serialized = message.SerializeToString()
        length = struct.pack('>I', len(serialized))
        self.cal_socket.sendall(length + serialized)

    def _cal_receive_message(self):
        """Receive protobuf message"""
        length_data = self.cal_socket.recv(4)
        if not length_data:
            return None
        length = struct.unpack('>I', length_data)[0]

        data = b''
        while len(data) < length:
            chunk = self.cal_socket.recv(length - len(data))
            if not chunk:
                return None
            data += chunk

        message = calibration_server_api_pb2.FromServer()
        message.ParseFromString(data)
        return message

    def _cal_receive_frames(self):
        """Receive and display frames"""
        frame_count = 0
        try:
            while self.cal_streaming:
                message = self._cal_receive_message()
                if not message:
                    break

                if message.HasField('stream_frame'):
                    frame_count += 1
                    frame = message.stream_frame.frame

                    # Convert and display left
                    left_img = self._raw_to_image(frame.left.image, frame.left.width, frame.left.height)
                    self.left_image_label.after(0, lambda img=left_img: self._display_frame(img, 'left'))

                    # Convert and display right
                    right_img = self._raw_to_image(frame.right.image, frame.right.width, frame.right.height)
                    self.right_image_label.after(0, lambda img=right_img: self._display_frame(img, 'right'))

                    # Update status
                    self.left_image_label.after(0, lambda: self.update_status(
                        f"Frame {frame_count}: {frame.left.width}x{frame.left.height}"))

        except Exception as e:
            if self.cal_streaming:
                logger.error(f"Error receiving calibration frames: {e}")
        finally:
            self.cal_streaming = False
            if self.cal_socket:
                self.cal_socket.close()
                self.cal_socket = None

    def _raw_to_image(self, raw_data, width, height):
        """Convert raw bytes to PIL Image"""
        try:
            img_array = np.frombuffer(raw_data, dtype=np.uint8).reshape((height, width))
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_GRAY2BGR)
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            return Image.fromarray(img_rgb)
        except Exception as e:
            logger.error(f"Error converting image: {e}")
            return None

    def _display_frame(self, pil_img, side):
        """Display frame on the appropriate label"""
        if pil_img is None:
            return

        try:
            lbl = self.left_image_label if side == 'left' else self.right_image_label
            lbl_w = lbl.winfo_width()
            lbl_h = lbl.winfo_height()

            if lbl_w > 10 and lbl_h > 10:
                pil_img = pil_img.resize((lbl_w, lbl_h), Image.LANCZOS)

            photo = ImageTk.PhotoImage(pil_img)
            lbl.config(image=photo)
            lbl.image = photo

        except Exception as e:
            logger.error(f"Error displaying frame: {e}")

    def stop_stream(self):
        """Stop streaming"""
        if not self.cal_streaming:
            self.update_status("Stream not running!")
            return

        self.cal_streaming = False
        self.update_status("Stopping stream...")

        try:
            if self.cal_socket:
                request = calibration_server_api_pb2.ToServer()
                request.stop_video_stream.CopyFrom(calibration_server_api_pb2.StopVideoStream())
                self._cal_send_message(request)

            if self.cal_socket:
                self.cal_socket.close()
                self.cal_socket = None

            self.update_status("✓ Stream stopped!")

        except Exception as e:
            logger.error(f"Error stopping stream: {e}")
            self.update_status(f"Error: {e}")
        finally:
            self.start_btn.config(state=NORMAL)
