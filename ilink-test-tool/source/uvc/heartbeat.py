import threading
import struct
from source.common_utilities.log_config import logger
import UvcServices_pb2


class HeartbeatManager:
    def __init__(self, connection, send_lock, interval=1.0):
        self.connection = connection
        self.interval = interval
        self._send_lock = send_lock
        self._stop_event = threading.Event()
        self._thread = None
        self._count = 0

    def start(self):
        if self._thread and self._thread.is_alive():
            return

        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._loop,
            daemon=True
        )
        self._thread.start()
        logger.info("Heartbeat thread started")

    def stop(self):
        if self._thread:
            self._stop_event.set()
            self._thread.join(timeout=5)

            if self._thread.is_alive():
                logger.warning("Heartbeat thread did not stop within 5 seconds")
            else:
                logger.info("Heartbeat thread stopped")

    def _loop(self):
        logger.info(f"Heartbeat loop running ({self.interval}s interval)")

        while not self._stop_event.wait(self.interval):
            try:
                # Construct a proper keep-alive message and set the EventType field.
                msg = UvcServices_pb2.UvcUicCommMessage()
                # Ensure the server sees this as an actual KEEP_ALIVE event
                msg.EVTKeepAlive.EventType = UvcServices_pb2.UvcUicCommMessage.EVENT_KEEP_ALIVE

                msg_bytes = msg.SerializeToString()

                with self._send_lock:
                    if self.connection.is_connected():
                        # Use the connection's send_message so the length-prefixing is
                        # handled consistently in one place.
                        self.connection.send_message(msg_bytes)
                        self._count += 1
                        logger.debug(f"Heartbeat #{self._count}")

            except Exception as e:
                logger.warning(f"Heartbeat error: {e}")
                break

        logger.info("Heartbeat loop exited")
