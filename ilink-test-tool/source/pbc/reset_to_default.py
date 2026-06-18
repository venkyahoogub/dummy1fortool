from source.pbc.led_controls import start_static_color_effect
from source.pbc.set_brake_fan_controls import brake_controls, set_fan_controls
from source.pbc.usb_power_controls import usb_controls

def reset_to_default(timeout=60):
    # Turn on brakes
    brake_controls(True)

    # Turn on fans
    set_fan_controls(True)

    # Turn of LED strip
    start_static_color_effect(0,0,0)

    # Turn on USB controls for all 3 channels
    usb_controls(True, True, True, True, timeout=60)

    return (
        "PBC has been reset to default values.\n "
        "**************************************\n"
        "Brake - On \n"
        "Fan(s) - On \n"
        "LED Strip - Off \n"
        "3 USB channels - On \n"
        "**************************************\n"
    )
