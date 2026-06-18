import threading
from source.common_utilities.log_config import logger
import source.common_utilities.constants as constants

from .connection import UvcConnection
from .heartbeat import HeartbeatManager
from .system_info_service import SystemInfoService
from .treatment_service import TreatmentService


class UvcClient:
    def __init__(self,
                 host=constants.UVC_IP,
                 port=constants.UVC_PORT,
                 timeout=10):

        self._token = 0
        self._send_lock = threading.Lock()

        self.connection = UvcConnection(host, port, timeout)
        self.heartbeat = HeartbeatManager(
            self.connection,
            self._send_lock
        )

        self.system_info = SystemInfoService(
            self.connection,
            self._send_lock,
            self._next_token
        )

        self.treatment = TreatmentService(
            self.connection,
            self._send_lock,
            self._next_token
        )

    # --------------------------
    # Token
    # --------------------------

    def _next_token(self):
        self._token += 1
        return self._token

    # --------------------------
    # Connection lifecycle
    # --------------------------

    def connect(self):
        self.connection.connect()
        self.heartbeat.start()

    def is_connected(self):
        return self.connection.is_connected()

    def disconnect(self):
        self.heartbeat.stop()
        self.connection.close()
        logger.info("Disconnected from UVC server")

    # --------------------------
    # Expose public API
    # --------------------------

    def get_about(self):
        return self.system_info.get_about()

    def is_calibration_data_valid(self):
        return self.system_info.is_calibration_data_valid()

    def is_camera_working(self):
        return self.system_info.is_camera_working()

    def get_errors(self):
        return self.system_info.get_errors()

    def start_treatment(self):
        return self.treatment.start_treatment()

    def get_treatment_data(self):
        return self.treatment.get_treatment_data()

    def start_treatment_with_pause_and_resume(self, pause_time):
        return self.treatment.start_treatment_with_pause_and_resume(pause_time)