import threading
import os, sys, time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "hbc")))
from source.common_utilities.pb_socket import PbSocket
import hbc_pb2
import source.common_utilities.constants as constants
import source.common_utilities.log_config as log_config
from source.hbc.hbc_utils import logger

class Hbc(object):
    def __init__(self, rx_msg_handler):
        self.rx_msg_handler = rx_msg_handler
        self.socket = PbSocket(constants.HBC_IP, constants.HBC_PORT)

        # --- self-test synchronization ---
        self._self_test_event = threading.Event()
        self._self_test_result = None

        self.receiver = threading.Thread(target=self.stream_reader, daemon=True)
        self.receiver.start()

    def __del__(self):
        pass

    def stream_reader(self):
        while True:
            try:
                encoded_protobuf = self.socket.receive_message()
                from_hbc = hbc_pb2.FromHbc.FromString(encoded_protobuf)
                self.rx_msg_handler(from_hbc.WhichOneof("msg"), from_hbc)

                msg_type = from_hbc.WhichOneof("msg")

                # capture self-test result internally
                if msg_type == constants.PROTO_SELFTESTRESULT:
                    self._self_test_result = from_hbc.self_test_result
                    self._self_test_event.set()

                # still forward message if caller wants it
                if self.rx_msg_handler:
                    self.rx_msg_handler(msg_type, from_hbc)
            except OSError as st:
                logger.info(f"HBC stream reader shutting down for socket teardown: {st}")
                break  # expected on socket close — exit cleanly
            except Exception as e:
                logger.error(f"Error in HBC stream reader: {e}")
    # --- Basic HBC Requests ---

    def get_status(self):
        to_hbc = hbc_pb2.ToHbc()
        to_hbc.get_status.SetInParent()
        encoded_protobuf = to_hbc.SerializeToString()
        self.socket.send_message(encoded_protobuf)

    def get_about(self):
        to_hbc = hbc_pb2.ToHbc()
        to_hbc.get_about.SetInParent()
        encoded_protobuf = to_hbc.SerializeToString()
        self.socket.send_message(encoded_protobuf)

    def update_firmware(self, binaryfile):
        try:
            with open(binaryfile, 'rb') as f:
                data = f.read()
            to_hbc = hbc_pb2.ToHbc()
            to_hbc.firmware_image.length_in_bytes = len(data)
            to_hbc.firmware_image.data = data
            time.sleep(10)
            encoded_protobuf = to_hbc.SerializeToString()
            self.socket.send_message(encoded_protobuf)
            time.sleep(15)
        except Exception as err:
            logger.error(f"Unexpected error during firmware update: {err}")

    # --- HBC Requests: Get/Set Parameters ---
    
    def get_controls(self):
        to_hbc = hbc_pb2.ToHbc()
        to_hbc.get_controls.SetInParent()
        encoded_protobuf = to_hbc.SerializeToString()
        self.socket.send_message(encoded_protobuf)

    def get_device_settings(self):
        to_hbc = hbc_pb2.ToHbc()
        to_hbc.get_device_settings.SetInParent()
        encoded_protobuf = to_hbc.SerializeToString()
        self.socket.send_message(encoded_protobuf)

    def get_device_limits(self):
        to_hbc = hbc_pb2.ToHbc()
        to_hbc.get_device_limits.SetInParent()
        encoded_protobuf = to_hbc.SerializeToString()
        self.socket.send_message(encoded_protobuf)

    # --- HBC Requests: Control Actions ---

    def move_motors(self, x_pos_mm, y_pos_mm, z_pos_mm):
        to_hbc = hbc_pb2.ToHbc()
        move = to_hbc.move_motors
        move.x_position_mm = x_pos_mm
        move.y_position_mm = y_pos_mm
        move.z_position_mm = z_pos_mm
        encoded_protobuf = to_hbc.SerializeToString()
        self.socket.send_message(encoded_protobuf)
    
    def home_motors(self):
        to_hbc = hbc_pb2.ToHbc()
        move = to_hbc.home_motors.SetInParent()
        encoded_protobuf = to_hbc.SerializeToString()
        self.socket.send_message(encoded_protobuf)

    def set_fan_controls(self, uv_fan_enable, head_fans_enable):
        to_hbc = hbc_pb2.ToHbc()
        controls = to_hbc.set_fan_controls
        controls.uv_fan_enable = uv_fan_enable
        controls.head_fans_enable = head_fans_enable
        encoded_protobuf = to_hbc.SerializeToString()
        self.socket.send_message(encoded_protobuf)

    def set_nir_led_controls(self, top_percent, bot_percent):
        to_hbc = hbc_pb2.ToHbc()
        controls = to_hbc.set_nir_led_controls
        controls.top_intensity_percent = top_percent
        controls.bot_intensity_percent = bot_percent
        encoded_protobuf = to_hbc.SerializeToString()
        self.socket.send_message(encoded_protobuf)

    def set_fixation_led_controls(self, intensity_percent):
        to_hbc = hbc_pb2.ToHbc()
        to_hbc.set_fixation_led_controls.intensity_percent = intensity_percent
        encoded_protobuf = to_hbc.SerializeToString()
        self.socket.send_message(encoded_protobuf)

    def set_camera_trigger_controls(self, frequency_hz, duration_ms):
        to_hbc = hbc_pb2.ToHbc()
        controls = to_hbc.set_camera_trigger_controls
        controls.frequency_hz = frequency_hz
        controls.duration_ms = duration_ms
        encoded_protobuf = to_hbc.SerializeToString()
        self.socket.send_message(encoded_protobuf)
        
    # --- HBC Requests: Distance Sensor ---

    def distance_sensor_start_ranging(self):
        to_hbc = hbc_pb2.ToHbc()
        to_hbc.distance_sensor_start_ranging.SetInParent()
        encoded_protobuf = to_hbc.SerializeToString()
        self.socket.send_message(encoded_protobuf)

    def distance_sensor_stop_ranging(self):
        to_hbc = hbc_pb2.ToHbc()
        to_hbc.distance_sensor_stop_ranging.SetInParent()
        encoded_protobuf = to_hbc.SerializeToString()
        self.socket.send_message(encoded_protobuf)

    def set_distance_sensor_settings(self, gain, offset):
        to_hbc = hbc_pb2.ToHbc()
        settings = to_hbc.set_distance_sensor_device_settings
        settings.gain = gain
        settings.offset = offset
        encoded_protobuf = to_hbc.SerializeToString()
        self.socket.send_message(encoded_protobuf)

    # --- HBC Requests: UV/PD Calibration & Settings ---

    def get_calibration_table(self):
        to_hbc = hbc_pb2.ToHbc()
        to_hbc.get_calibration_table.SetInParent()
        encoded_protobuf = to_hbc.SerializeToString()
        self.socket.send_message(encoded_protobuf)

    def start_calibration(self, irradiance_mw_per_cm2, dac_count):
        to_hbc = hbc_pb2.ToHbc()
        cal = to_hbc.start_calibration
        cal.irradiance_mw_per_cm2 = irradiance_mw_per_cm2
        cal.dac_count = dac_count
        encoded_protobuf = to_hbc.SerializeToString()
        self.socket.send_message(encoded_protobuf)
        
    def start_uv_diagnostic(self, dac_counts, duration_ms):
        to_hbc = hbc_pb2.ToHbc()
        diag = to_hbc.start_uv_diagnostic
        diag.dac_counts = dac_counts
        diag.duration_ms = duration_ms
        encoded_protobuf = to_hbc.SerializeToString()
        self.socket.send_message(encoded_protobuf)
        
    def stop_uv_diagnostic(self):
        to_hbc = hbc_pb2.ToHbc()
        to_hbc.stop_uv_diagnostic.SetInParent()
        encoded_protobuf = to_hbc.SerializeToString()
        self.socket.send_message(encoded_protobuf)
        
    def start_self_test(self, irradiance_mw_per_cm2, timeout=5):
        # reset state
        self._self_test_event.clear()
        self._self_test_result = None

        to_hbc = hbc_pb2.ToHbc()
        to_hbc.start_self_test.irradiance_mw_per_cm2 = irradiance_mw_per_cm2
        self.socket.send_message(to_hbc.SerializeToString())

        if not self._self_test_event.wait(timeout):
            raise TimeoutError("Self-test timed out")

        return self._self_test_result

    def set_uv_device_settings(self, pd1_gain, pd2_gain, pd3_gain, pi_gain):
        to_hbc = hbc_pb2.ToHbc()
        settings = to_hbc.set_uv_device_settings
        settings.pd1_gain_count = pd1_gain
        settings.pd2_gain_count = pd2_gain
        settings.pd3_gain_count = pd3_gain
        settings.pi_gain_count = pi_gain
        encoded_protobuf = to_hbc.SerializeToString()
        self.socket.send_message(encoded_protobuf)
        
    def set_serial_number(self, device_serial_number):
        to_hbc = hbc_pb2.ToHbc()
        device_serial = to_hbc.set_serial_number
        device_serial.serial_number = device_serial_number
        encoded_protobuf = to_hbc.SerializeToString()
        self.socket.send_message(encoded_protobuf)
    
    def start_pulsed_treatment(self, irradiance_mw_per_cm2, treatment_time_ms, pulse_on_time_ms, pulse_off_time_ms):
        to_hbc = hbc_pb2.ToHbc()
        pulsed_treatment = to_hbc.start_pulsed_treatment
        pulsed_treatment.irradiance_mw_per_cm2 = irradiance_mw_per_cm2
        pulsed_treatment.pulse_on_time_ms = pulse_on_time_ms
        pulsed_treatment.pulse_off_time_ms = pulse_off_time_ms
        pulsed_treatment.treatment_time_ms = treatment_time_ms
        encoded_protobuf = to_hbc.SerializeToString()
        self.socket.send_message(encoded_protobuf)
    
    def start_cw_treatment(self, irradiance_mw_per_cm2, treatment_time_ms):
        to_hbc = hbc_pb2.ToHbc()
        cw_treatment = to_hbc.start_cw_treatment
        cw_treatment.irradiance_mw_per_cm2 = irradiance_mw_per_cm2
        cw_treatment.treatment_time_ms = treatment_time_ms
        encoded_protobuf = to_hbc.SerializeToString()
        self.socket.send_message(encoded_protobuf)

    def start_demo_treatment(self, treatment_time_ms):
        to_hbc = hbc_pb2.ToHbc()
        cw_treatment = to_hbc.start_demo_treatment
        cw_treatment.treatment_time_ms = treatment_time_ms
        encoded_protobuf = to_hbc.SerializeToString()
        self.socket.send_message(encoded_protobuf)
