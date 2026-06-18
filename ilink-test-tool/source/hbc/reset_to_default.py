from source.hbc.set_and_get_camera_triggers import set_get_camera_trigger_controls
from source.hbc.set_and_get_fixation_led_controls import set_get_fixation_led
from source.hbc.set_and_get_nir_led_controls import set_get_nir_led
from source.hbc.set_hbc_calibration import set_calibration_value
from source.hbc.set_motor_fan_controls import home_motors
from source.hbc.set_serial_number import set_serial_number
from source.hbc.set_uv_device_settings import set_uv_device_settings
from common_utilities import constants


def reset_to_default(timeout=60):
    # Reset Camera Trigger Controls
    set_get_camera_trigger_controls(constants.PROTO_DEFAULT_FREQ, 
                                    constants.PROTO_DEFAULT_DUR, timeout=5)

    # Reset Fixation LED's
    set_get_fixation_led(constants.PROTO_DEFAULT_INT, timeout=5)

    # Reset NIR LED's
    set_get_nir_led(constants.PROTO_DEFAULT_NIR, 
                    constants.PROTO_DEFAULT_NIR, timeout=5)

    # Reset HBC Calibration value
    set_calibration_value(constants.PROTO_DEFAULT_IRR, 
                          constants.PROTO_DEFAULT_DAC)

    # Reset Device Serial Number
    set_serial_number("DEFAULT-DB5")

    # Reset UV device settings
    set_uv_device_settings(constants.PROTO_DEFAULT_PD1_GC, 
                           constants.PROTO_DEFAULT_PD2_GC, 
                           constants.PROTO_DEFAULT_PD3_GC, 
                           constants.PROTO_DEFAULT_PI_GC, 
                           timeout=5)

    # Home motors
    home_motors(timeout=60)
    return (
        "HBC has been reset to default values.\n"
        "**************************************\n"
        "Camera Trigger - frequency: 30 hz, duration: 7 ms\n"
        "Fixation LED: 10%\n"
        "NIR LED: top:80%, bot:80%\n"
        "HBC Calibration: irradiance: 30 mw/cm2, dac_count:5000\n"
        "Serial# DEFAULT-DB5\n"
        "pd1: 0, pd2: 512, pd3: 256, pi: 1023\n"
        "**************************************\n"
    )