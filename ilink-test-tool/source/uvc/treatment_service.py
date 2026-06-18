import time
import UvcServices_pb2
from source.common_utilities.log_config import logger
import source.common_utilities.constants as constants
from source.uvc.ConnectToUVCNetcat import NetcatClient


class TreatmentService:
    def __init__(self, connection, send_lock, token_provider):
        self.connection = connection
        self._send_lock = send_lock
        self.get_next_token = token_provider
        self._last_keepalive_log = 0
        self._last_other_log = 0
    
    def set_treatment_parameters(self):
        msg = UvcServices_pb2.UvcUicCommMessage()
        req = msg.REQTreatmentParameters

        req.Token = self.get_next_token()
        req.PatientId = "TEST123"
        req.EyeTreated = UvcServices_pb2.UvcUicCommMessage.EYE_TYPE_OD
        req.UvIrradiance = 3          # mW/cm2
        req.UvDose = 5.9              # J/cm2
        req.OuterDiameter_mm = 9.0
        req.InnerDiameter_mm = 0.0
        req.OffsetX_mm = 0.0
        req.OffsetY_mm = 0.0
        req.IsDemoTreatment = True
        req.ScanPitch = 1.0
        req.ScanPeriod = 1.0
        req.TreatmentId = "TX001"
        #req.IsCustom = True

        self.connection.send_message(msg.SerializeToString())
        logger.info("SetTreatmentParametersRequest sent")

    def request_treatment_state(self):
        msg = UvcServices_pb2.UvcUicCommMessage()
        msg.REQTreatmentState.SetInParent()
        self.connection.send_message(msg.SerializeToString())
        logger.info("TreatmentStateRequest sent")

    def complete_induction_state(self):
        msg = UvcServices_pb2.UvcUicCommMessage()
        msg.REQCompleteInduction.SetInParent()
        self.connection.send_message(msg.SerializeToString())
        logger.info("CompleteInductionState sent")

    def start_treatment(self):
        self.set_treatment_parameters()
        time.sleep(1) # small delay after params are set to complete induction
        self.complete_induction_state()

        # Connect to the NetCat Client
        netcat = NetcatClient()
        if not netcat.connect():
            logger.error("Failed to connect to Netcat UVC CLI")
            return None

        time.sleep(1) # Calling the CLI interface
        # Send a request "eyetracking manual"
        if not netcat.send_command("eyetracking manual", "Eye tracking is now set to manual"):
            logger.error("Failed to set eyetracking to manual")
            return None

        time.sleep(1) # Calling the CLI interface
        # Send a request "align true"
        if not netcat.send_command("align true", ""):
            logger.error("Failed to enable alignment")
            return None

        time.sleep(1)
        self.request_treatment_state()

        msg = UvcServices_pb2.UvcUicCommMessage()
        req = UvcServices_pb2.UvcUicCommMessage.GenericRequest()
        req.Token = self.get_next_token()
        req.CommandId = UvcServices_pb2.UvcUicCommMessage.UI_START_TREATMENT
        msg.REQGeneric.CopyFrom(req)

        with self._send_lock:
            logger.info("UI start treatment sent via UVC")
            # Start treatment (runs for a UVC side hardcoded 60 seconds)
            self.connection.send_message(msg.SerializeToString())

        while True:
            rsp_bytes = self.connection.receive()
            rsp_msg = UvcServices_pb2.UvcUicCommMessage()
            rsp_msg.ParseFromString(rsp_bytes)

            if rsp_msg.HasField("RSPGeneric"):
                logger.info(f"Got response {rsp_msg.RSPGeneric}")
            elif rsp_msg.HasField("EVTKeepAlive"):
                now = time.time()
                if now - self._last_keepalive_log > 5:
                    logger.info("Keep-alive received from UVC")
                    self._last_keepalive_log = now
            elif rsp_msg.HasField("EVTSimple"):
                evt_type = rsp_msg.EVTSimple.EventType
                
                if evt_type == UvcServices_pb2.UvcUicCommMessage.UI_START_TREATMENT:
                    logger.info(f"Treatment has begun {rsp_msg}")

                elif evt_type == UvcServices_pb2.UvcUicCommMessage.EVENT_TREATMENT_FINISHED:
                    logger.info(f"Treatment finished {rsp_msg}")
                    return rsp_msg.EVTSimple
            else:
                now = time.time()
                if now - self._last_other_log >= 1:
                    logger.info(f"Other msg: {rsp_msg}")
                    self._last_other_log = now

    def get_treatment_data(self):
        self.request_treatment_state()

        msg = UvcServices_pb2.UvcUicCommMessage()
        req = UvcServices_pb2.UvcUicCommMessage.GenericRequest()
        req.Token = self.get_next_token()
        req.CommandId = UvcServices_pb2.UvcUicCommMessage.UI_GET_TREATMENT_DATA
        msg.REQGeneric.CopyFrom(req)

        with self._send_lock:
            logger.info("UI asks for treatment data via UVC")
            self.connection.send_message(msg.SerializeToString())

        while True:
            rsp_bytes = self.connection.receive()
            rsp_msg = UvcServices_pb2.UvcUicCommMessage()
            rsp_msg.ParseFromString(rsp_bytes)

            if rsp_msg.HasField("RSPTreatmentData"):
                data = rsp_msg.RSPTreatmentData.Data
                logger.info(f"data msg: {data}")
                return data
            elif rsp_msg.HasField("RSPGeneric"):
                logger.info(f"Got generic ACK: {rsp_msg.RSPGeneric}")
                # Don't return — keep waiting for the actual data
            elif rsp_msg.HasField("EVTKeepAlive"):
                now = time.time()
                if now - self._last_keepalive_log > 5:
                    logger.info("Keep-alive received from UVC")
                    self._last_keepalive_log = now
            else:
                logger.info(f"Other message received: {rsp_msg}")

    def pause_treatment(self, duration_seconds):
        # Send pause request
        msg = UvcServices_pb2.UvcUicCommMessage()
        msg.REQPauseTreatment.SetInParent()
        with self._send_lock:
            self.connection.send_message(msg.SerializeToString())
            logger.info(f"Pause treatment sent, waiting {duration_seconds}s")

        time.sleep(int(duration_seconds))

        # Send resume (deliver) request
        msg = UvcServices_pb2.UvcUicCommMessage()
        msg.REQDeliverTreatment.SetInParent()
        with self._send_lock:
            self.connection.send_message(msg.SerializeToString())
            logger.info("Deliver treatment sent — resuming treatment")

    def start_treatment_with_pause_and_resume(self, pause_duration_seconds):
        # --- Setup phase (same as before) ---
        elapsed_ms = 0
        self.set_treatment_parameters()
        time.sleep(1)
        self.complete_induction_state()

        netcat = NetcatClient()
        if not netcat.connect():
            logger.error("Failed to connect to Netcat UVC CLI")
            return None

        time.sleep(1)
        if not netcat.send_command("eyetracking manual", "Eye tracking is now set to manual"):
            logger.error("Failed to set eyetracking to manual")
            return None

        time.sleep(1)
        if not netcat.send_command("align true", ""):
            logger.error("Failed to enable alignment")
            return None

        time.sleep(1)
        self.request_treatment_state()

        # --- Start treatment ---
        msg = UvcServices_pb2.UvcUicCommMessage()
        req = UvcServices_pb2.UvcUicCommMessage.GenericRequest()
        req.Token = self.get_next_token()
        req.CommandId = UvcServices_pb2.UvcUicCommMessage.UI_START_TREATMENT
        msg.REQGeneric.CopyFrom(req)

        with self._send_lock:
            logger.info("UI start treatment sent via UVC")
            self.connection.send_message(msg.SerializeToString())

        # --- Control flags ---
        treatment_started = False   # true when UV actually delivering
        pause_sent = False
        resume_sent = False
        pause_start_time = None

        # --- Main event loop ---
        while True:
            rsp_bytes = self.connection.receive()
            rsp_msg = UvcServices_pb2.UvcUicCommMessage()
            rsp_msg.ParseFromString(rsp_bytes)

            now = time.time()

            # --- Handle treatment progress ---
            if rsp_msg.HasField("EVTTreatmentTime"):
                elapsed_ms = rsp_msg.EVTTreatmentTime.Times_ms
                
                if not treatment_started:
                    logger.info("Treatment actively delivering UV")
                    treatment_started = True

            # --- Send pause once treatment has run for 10 seconds ---
            if not pause_sent and elapsed_ms >= 10000:
                msg = UvcServices_pb2.UvcUicCommMessage()
                msg.REQPauseTreatment.SetInParent()

                with self._send_lock:
                    self.connection.send_message(msg.SerializeToString())

                logger.info(f"Pause sent at {elapsed_ms} ms")
                pause_sent = True
                pause_start_time = time.time()

            # --- Wait duration without blocking receive loop ---
            if pause_sent and not resume_sent:
                elapsed = now - pause_start_time
                if elapsed >= int(pause_duration_seconds):
                    msg = UvcServices_pb2.UvcUicCommMessage()
                    msg.REQDeliverTreatment.SetInParent()

                    with self._send_lock:
                        self.connection.send_message(msg.SerializeToString())

                    logger.info("Resume (deliver) treatment sent")
                    resume_sent = True

            # --- Standard message handling ---
            if rsp_msg.HasField("RSPGeneric"):
                logger.info(f"Got response {rsp_msg.RSPGeneric}")

            elif rsp_msg.HasField("EVTKeepAlive"):
                if now - self._last_keepalive_log > 5:
                    logger.info("Keep-alive received from UVC")
                    self._last_keepalive_log = now

            elif rsp_msg.HasField("EVTSimple"):
                evt_type = rsp_msg.EVTSimple.EventType

                if evt_type == UvcServices_pb2.UvcUicCommMessage.EVENT_TREATMENT_FINISHED:
                    logger.info("Treatment finished")
                    return rsp_msg.EVTSimple

            else:
                if now - self._last_other_log >= 1:
                    logger.info(f"Other msg: {rsp_msg}")
                    self._last_other_log = now
