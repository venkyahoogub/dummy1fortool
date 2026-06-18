import threading
import os, sys, time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "pbc")))
from source.common_utilities.pb_socket import PbSocket
import pbc_pb2
import source.common_utilities.constants as constants
import source.common_utilities.log_config as log_config
from source.pbc.pbc_utils import logger

class Pbc(object):
    def __init__(self, rx_msg_handler):
        self.rx_msg_handler = rx_msg_handler
        self.socket = PbSocket(constants.PBC_IP, constants.PBC_PORT)
        self.receiver = threading.Thread(target=self.stream_reader, daemon=True)
        self.receiver.start()

    def __del__(self):
        pass

    def stream_reader(self):
        while True:
            try:
                encoded_protobuf = self.socket.receive_message()
                from_pbc = pbc_pb2.FromPbc.FromString(encoded_protobuf)
                self.rx_msg_handler(from_pbc.WhichOneof("msg"), from_pbc)
            except OSError as st:
                logger.info(f"PBC stream reader shutting down for socket teardown: {st}")
                break  # expected on socket close — exit cleanly
            except Exception as e:
                logger.error(f"Error in HBC stream reader: {e}")

    def get_status(self):
        to_pbc = pbc_pb2.ToPbc()
        to_pbc.get_status.SetInParent()
        encoded_protobuf = to_pbc.SerializeToString()
        self.socket.send_message(encoded_protobuf)

    def get_about(self):
        to_pbc = pbc_pb2.ToPbc()
        to_pbc.get_about.SetInParent()
        encoded_protobuf = to_pbc.SerializeToString()
        self.socket.send_message(encoded_protobuf)
    
    def get_controls(self):
        to_pbc = pbc_pb2.ToPbc()
        to_pbc.get_controls.SetInParent()
        encoded_protobuf = to_pbc.SerializeToString()
        self.socket.send_message(encoded_protobuf)

    def get_device_limits(self):
        to_pbc = pbc_pb2.ToPbc()
        to_pbc.get_device_limits.SetInParent()
        encoded_protobuf = to_pbc.SerializeToString()
        self.socket.send_message(encoded_protobuf)

    def update_firmware(self, binaryfile):
        try:
            with open(binaryfile, 'rb') as f:
                data = f.read()
            to_pbc = pbc_pb2.ToPbc()
            to_pbc.firmware_image.length_in_bytes = len(data)
            to_pbc.firmware_image.data = data
            time.sleep(10)
            encoded_protobuf = to_pbc.SerializeToString()
            self.socket.send_message(encoded_protobuf)
            time.sleep(15)
        except Exception as err:
            logger.error(f"Unexpected error during firmware update: {err}")
    
    # --- LED color effects ---
    def start_led_strip_static_color_effect(self, red, green, blue):
        to_pbc = pbc_pb2.ToPbc()
        led_controls = to_pbc.start_led_strip_static_color_effect
        led_controls.red = red
        led_controls.green = green
        led_controls.blue = blue
        encoded_protobuf = to_pbc.SerializeToString()
        self.socket.send_message(encoded_protobuf)

    def start_led_strip_pulse_effect(self, red, green, blue, pulse_period_ms):
        to_pbc = pbc_pb2.ToPbc()
        led_controls = to_pbc.start_led_strip_pulse_effect
        led_controls.red = red
        led_controls.green = green
        led_controls.blue = blue
        led_controls.pulse_period_ms = pulse_period_ms
        encoded_protobuf = to_pbc.SerializeToString()
        self.socket.send_message(encoded_protobuf)
    
    def start_led_strip_rainbow_effect(self):
        to_pbc = pbc_pb2.ToPbc()
        to_pbc.start_led_strip_rainbow_effect.SetInParent()
        encoded_protobuf = to_pbc.SerializeToString()
        self.socket.send_message(encoded_protobuf)
    
    def start_led_strip_chasing_rainbow_effect(self):
        to_pbc = pbc_pb2.ToPbc()
        to_pbc.start_led_strip_chasing_rainbow_effect.SetInParent()
        encoded_protobuf = to_pbc.SerializeToString()
        self.socket.send_message(encoded_protobuf)

    # --- Fan and Brake controls ---
    def set_fan_controls(self, fans_enable):
        to_pbc = pbc_pb2.ToPbc()
        controls = to_pbc.set_fan_controls
        controls.fans_enable = fans_enable
        encoded_protobuf = to_pbc.SerializeToString()
        self.socket.send_message(encoded_protobuf)
    
    def set_brake_controls(self, brake_enable):
        to_pbc = pbc_pb2.ToPbc()
        controls = to_pbc.set_brake_controls
        controls.brake_enable = brake_enable
        encoded_protobuf = to_pbc.SerializeToString()
        self.socket.send_message(encoded_protobuf)

    # --- USB power controls ---
    def set_usb_power_controls(self, port_1_channel_1_enable, port_1_channel_2_enable, port_2_channel_1_enable, port_2_channel_2_enable):
        to_pbc = pbc_pb2.ToPbc()
        controls = to_pbc.set_usb_power_controls
        controls.port_1_channel_1_enable = port_1_channel_1_enable
        controls.port_1_channel_2_enable = port_1_channel_2_enable
        controls.port_2_channel_1_enable = port_2_channel_1_enable
        controls.port_2_channel_2_enable = port_2_channel_2_enable
        encoded_protobuf = to_pbc.SerializeToString()
        self.socket.send_message(encoded_protobuf)
            
    def get_help(self):
        commands = {
            "--help": "Provides information on arguments that can be used with this tool.",
            "--pbc_about": "Provides the meta data information about the pbc",
            "--pbc_status": "Provides the status information about the pbc",
            "--pbc_update_firmware_latest": "Allows user to update to the latest firmware version",
            "--ilinktesttool_version": "Provides the ilink test tool's version",
        }
        lines = ["The following messages can be passed as parameters to the ilink test tool:"]
        for cmd, desc in commands.items():
            lines.append(f"{cmd:<32} --> {desc}")
        msg = "\n".join(lines)
        log_config.logger.info(msg)
        return msg