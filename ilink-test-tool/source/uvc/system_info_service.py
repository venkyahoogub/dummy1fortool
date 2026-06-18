import time
import UvcServices_pb2
from source.common_utilities.log_config import logger
import source.common_utilities.constants as constants


class SystemInfoService:
    def __init__(self, connection, send_lock, token_provider):
        self.connection = connection
        self._send_lock = send_lock
        self.get_next_token = token_provider
        self._cached_system_info = None
        self._last_keepalive_log = 0

    def _request_system_info(self):
        if self._cached_system_info:
            return self._cached_system_info

        msg = UvcServices_pb2.UvcUicCommMessage()
        req = UvcServices_pb2.UvcUicCommMessage.GenericRequest()
        req.Token = self.get_next_token()
        req.CommandId = UvcServices_pb2.UvcUicCommMessage.UI_QUERY_SYSTEM_INFO
        msg.REQGeneric.CopyFrom(req)

        with self._send_lock:
            self.connection.send_message(msg.SerializeToString())

        while True:
            rsp_bytes = self.connection.receive()
            rsp_msg = UvcServices_pb2.UvcUicCommMessage()
            rsp_msg.ParseFromString(rsp_bytes)

            if rsp_msg.HasField("RSPSystemInfo"):
                self._cached_system_info = rsp_msg.RSPSystemInfo
                return self._cached_system_info

            elif rsp_msg.HasField("EVTKeepAlive"):
                now = time.time()
                if now - self._last_keepalive_log > 5:
                    logger.info("Keep-alive received from UVC")
                    self._last_keepalive_log = now

            else:
                logger.warning(constants.RECIEVED_OTHER_MSG)

    # Public getters

    def get_about(self):
        info = self._request_system_info()
        return "\n".join([
            f"UVC Version: {info.UvcVersion}",
            f"UVC Serial: {info.UvcSerialNumber}",
            f"HBC Version: {info.HbcVersion}",
            f"HBC Serial: {info.HbcSerialNumber}",
            f"PBC Version: {info.PbcVersion}",
            f"PBC Serial: {info.PbcSerialNumber}",
        ])

    def is_calibration_data_valid(self):
        return str(self._request_system_info().IsCalibrationDataValid)

    def is_camera_working(self):
        return str(self._request_system_info().IsCameraWorking)

    def get_errors(self):
        sysinfo = self._request_system_info()
        errors = [(e.Code, e.Message) for e in sysinfo.Errors]
        if not errors:
            return "No errors"
        return "; ".join(
            [f"Code: {c}, Message: {m}" for c, m in errors]
        )