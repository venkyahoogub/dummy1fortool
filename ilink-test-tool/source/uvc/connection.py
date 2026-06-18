import socket
import struct
import time
from source.common_utilities.log_config import logger
import source.common_utilities.constants as constants


class UvcConnection:
    def __init__(self, host, port, timeout=10):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.sock = None
        self.recv_buffer = bytearray()

    # --------------------------
    # Connection
    # --------------------------

    def connect(self):
        if self.sock is not None:
            try:
                self.sock.send(b"")
                logger.debug(f"Socket already connected to {self.host}:{self.port}")
                return
            except (socket.error, OSError):
                logger.info("Existing socket invalid. Reconnecting...")
                self.close()

        while True:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(self.timeout)
                self.sock.connect((self.host, self.port))
                logger.info(f"Connected to UVC server -> {self.host}:{self.port}")
                return
            except Exception as e:
                logger.warning(
                    f"Connection failed: {e}. Retrying in 10 seconds..."
                )
                time.sleep(10)

    def is_connected(self):
        return self.sock is not None

    def close(self):
        if self.sock:
            try:
                self.sock.close()
            except Exception as e:
                logger.warning(f"Error closing socket: {e}")
        self.sock = None

    # --------------------------
    # Messaging (length-prefixed)
    # --------------------------

    def send_message(self, msg_bytes):
        try:
            length_bytes = struct.pack("<I", len(msg_bytes))
            self.sock.sendall(length_bytes + msg_bytes)
        except (socket.timeout, socket.error, OSError) as e:
            logger.error(f"Send failed: {e}")
            raise

    def receive(self):
        try:
            while len(self.recv_buffer) < 4:
                chunk = self.sock.recv(4096)
                if not chunk:
                    raise RuntimeError(constants.SOCKET_CLOSED)
                self.recv_buffer.extend(chunk)

            msg_length = struct.unpack("<I", self.recv_buffer[:4])[0]

            while len(self.recv_buffer) < 4 + msg_length:
                chunk = self.sock.recv(4096)
                if not chunk:
                    raise RuntimeError(constants.SOCKET_CLOSED)
                self.recv_buffer.extend(chunk)

            msg_bytes = self.recv_buffer[4:4 + msg_length]
            self.recv_buffer = self.recv_buffer[4 + msg_length:]
            return msg_bytes

        except Exception as e:
            logger.error(f"Receive failed: {e}")
            raise