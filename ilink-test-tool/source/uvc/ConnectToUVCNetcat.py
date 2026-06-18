import socket
import time
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from common_utilities.log_config import logger
from common_utilities import constants

class NetcatClient:
    def __init__(self, host=constants.UVC_IP, port=constants.UVC_CLI_PORT, timeout=5 * 60):
        self.host = host
        self.port = port
        self.timeout = timeout  # up to 5 minutes
        self.sock = None
        self.buffer_size = 4096 # Similar to UVC buffer
        self.connected = False

    def connect(self):
        if self.connected and self.sock:
            logger.info(f"Already connected to {self.host}:{self.port}")
            return True

        logger.info(f"Connecting to {self.host}:{self.port} ...")

        start_time = time.time()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        except Exception:
            pass
        self.sock.settimeout(5)

        while time.time() - start_time < self.timeout:
            try:
                self.sock.connect((self.host, self.port))
                logger.info("Socket connected. Waiting for UVC confirmation...")
                data = self._recv_until("Connected to UVC", timeout=self.timeout)
                if "Connected to UVC" in data:
                    self.connected = True
                    logger.info("Connected to UVC")
                    return True
                else:
                    # If system didn't get confirmation, keep trying (close and recreate socket)
                    try:
                        self.sock.close()
                    except Exception:
                        pass
                    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    try:
                        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                    except Exception:
                        pass
                    self.sock.settimeout(5)
            except (socket.timeout, ConnectionRefusedError, OSError):
                time.sleep(1)
            except Exception as e:
                logger.error(f"Connection error: {e}")
                time.sleep(1)

        logger.error("Failed to connect to UVC within timeout.")
        self.connected = False
        return False

    def disconnect(self):
        try:
            if self.sock:
                try:
                    self.sock.close()
                except Exception:
                    pass
            self.sock = None
            self.connected = False
        except Exception as e:
            logger.error(f"disconnect error: {e}")

    def _recv_until(self, keyword, timeout=30):
        try:
            self.sock.settimeout(1)
        except Exception:
            pass
        data = b""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                chunk = self.sock.recv(self.buffer_size)
                if not chunk:
                    logger.warning("Remote closed connection while waiting for data.")
                    self.connected = False
                    break
                data += chunk
                text = data.decode(errors="ignore")
                if keyword in text:
                    return text
            except socket.timeout:
                continue
            except Exception as e:
                logger.error(f"Receive error: {e}")
                self.connected = False
                break
        return data.decode(errors="ignore")

    def send_command(self, cmd, expected_response, reconnect_if_needed=True):
        try:
            if not self.connected:
                if reconnect_if_needed:
                    logger.info("Not connected. Attempting to reconnect...")
                    if not self.connect():
                        return False
                else:
                    logger.warning("Not connected to UVC. Skipping command.")
                    return False

            try:
                self.sock.sendall((cmd + "\n").encode())
                response = self._recv_until(expected_response, timeout=30)
                if expected_response in response:
                    logger.info(f"Command '{cmd}' succeeded.")
                    return True
                else:
                    logger.warning(f"Command '{cmd}' did not receive expected response.")
                    self.connected = False
                    return False
            except (BrokenPipeError, ConnectionResetError, OSError) as e:
                self.connected = False
                logger.error(f"Connection lost during send: {e}. Will need to reconnect.")
                if reconnect_if_needed:
                    return self.send_command(cmd, expected_response)
            return False
        except Exception as e:
                logger.error(f"send_command error: {e}")

    # Convenience wrappers (original behavior, may reconnect)
    def left(self):
        return self.send_command(constants.CAMERA_STRING_LEFT, constants.STREAM_RESPONSE_LEFT)

    def right(self):
        return self.send_command(constants.CAMERA_STRING_RIGHT, constants.STREAM_RESPONSE_RIGHT)

    def wide(self):
        return self.send_command(constants.CAMERA_STRING_WIDE, constants.STREAM_RESPONSE_WIDE)

    def auto(self):
        return self.send_command(constants.CAMERA_STRING_AUTO, constants.STREAM_RESPONSE_AUTO)

    # These call send_command with reconnect_if_needed=False so the caller controls reconnection.
    def left_no_reconnect(self):
        return self.send_command(constants.CAMERA_STRING_LEFT, constants.STREAM_RESPONSE_LEFT, reconnect_if_needed=False)

    def right_no_reconnect(self):
        return self.send_command(constants.CAMERA_STRING_RIGHT, constants.STREAM_RESPONSE_RIGHT, reconnect_if_needed=False)

    def wide_no_reconnect(self):
        return self.send_command(constants.CAMERA_STRING_WIDE, constants.STREAM_RESPONSE_WIDE, reconnect_if_needed=False)

    def auto_no_reconnect(self):
        return self.send_command(constants.CAMERA_STRING_AUTO, constants.STREAM_RESPONSE_AUTO, reconnect_if_needed=False)
    
    def start_treatment(self):
        return self.send_command(constants.TURN_UV_ON, None)

    def cancel_treatment(self):
        return self.send_command(constants.TURN_UV_OFF, None)