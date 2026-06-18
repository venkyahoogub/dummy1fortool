import os
import time
import subprocess
import sys
import constants
import re
from test_setup import run_pyinstaller, cleanup
from dotenv import load_dotenv
from source.common_utilities.log_config import logger

# Load environment variables from .env file
load_dotenv()


def wait_for_executable(executable_path, timeout=60, poll_interval=2):
    """Wait for the executable to be created in the dist folder."""
    logger.info(f"Waiting for the executable at {executable_path}...")

    start_time = time.time()

    while not os.path.exists(executable_path):
        if time.time() - start_time > timeout:
            logger.error(f"Timeout: The executable {executable_path} was not created in time.")
            sys.exit(1)
        time.sleep(poll_interval)

    logger.info(f"Executable {executable_path} found!")


def run_subprocess(executable_path, argument):
    try:
        """Run the executable with the given argument and capture output."""
        result = subprocess.run([executable_path, argument], capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"Test failed! Error executing the executable with argument {argument}.")
            logger.error(result.stderr)
            return None  # Indicating failure

        return result.stdout

    except Exception as e:
        logger.exception(f"An error occurred while running the subprocess: {e}")
        return None

def validate_output(expected_values, output, regex=False):
    """General function to validate the output with either direct match or regex."""
    for key, expected_value in expected_values.items():
        if regex:
            match = re.search(expected_value, output)
            if match:
                logger.info(f"Test passed: {key} matched with value {match.group(1)}.")
            else:
                logger.error(f"Test failed: {key} did not match expected pattern.")
                return False
        else:
            for line in output.splitlines():
                if line.strip().startswith(f"{key}:"):
                    value = line.split(":", 1)[1].strip()
                    if isinstance(expected_value, bool):
                        value = value.lower() == 'true'
                        if value == expected_value:
                            logger.info(f"Test passed: {key} with value {expected_value}.")
                            break
                        else:
                            logger.error(f"Test failed: {key} value {value}, expected {expected_value}.")
                            return False
                    elif isinstance(expected_value, int):
                        if len(value) == expected_value:
                            logger.info(f"Test passed: {key} length is {expected_value}.")
                            break
                        else:
                            logger.error(f"Test failed: {key} length is {len(value)}, expected {expected_value}.")
                            return False
    else:
        logger.info("All expected values were found in the output.")
        return True


def run_test(executable_path, argument, expected_values, regex=False):
    """General function to run the test and validate expected output."""
    logger.info(f"Running the test with argument: {argument}")

    output = run_subprocess(executable_path, argument)
    if output is None:
        return False  # Test failed

    logger.info(f"Test output:\n{output}")
    return validate_output(expected_values, output, regex)


def run_test_pbc_status(executable_path):
    """Run the status test."""
    expected_values = {
        "power_supply_ch3_is_enabled": True,
        "power_supply_ac_is_ok": True,
        "power_supply_dc_is_ok": True,
        "usb1_ch1_is_enabled": True,
        "usb1_ch2_is_enabled": True,
        "usb2_ch1_is_enabled": True,
        "usb2_ch2_is_enabled": True,
        "galil_elo_is_enabled": True,
        "galil_logic_is_enabled": True,
        "galil_amp_is_enabled": True,
        "brake_is_released": True,
        "brake_shoulder_is_released": True,
        "uv_sbc_is_enabled": True,
        "estop_is_pressed": True,
        "netswitch_is_enabled": True
    }
    return run_test(executable_path, '--pbc_status', expected_values)


def run_test_pbc_about(executable_path):
    """Run the about test with regex pattern matching."""
    expected_values = {
        "version": r'\"([0-9]+\.[0-9]+\.[0-9]+)\"',
        "bootloader_version": r'\"([0-9]+\.[0-9]+\.[0-9]+)\"',
        "serial_number": r'\"([a-f0-9]{15})\"',
        "mac_address": r'\"([0-9A-Fa-f]{2}(:[0-9A-Fa-f]{2}){5})\"'
    }
    return run_test(executable_path, '--pbc_about', expected_values, regex=True)

def run_test_pbc_error(executable_path):
    """Run the error test."""
    logger.info("Running the test to check the error message...")

    output = run_subprocess(executable_path, '--pbc_about1')
    if output is None:
        return False  # Test failed

    logger.info(f"Test output:\n{output}")
    if constants.PBC_ERROR_MESSAGE in output:
        logger.info(constants.TEST_PASSED_ERRORCASE)
        return True
    else:
        logger.error(f"{constants.TEST_FAILED_ERRORCASE} \nOutput: {output}")
        return False

def run_test_firmware_update_to_latest(executable_path):
    # Using a regular expression to match the fixed part of the string of firmware install
    expected_output = r"Installation and verification of neo_pbc_fw_bootable_image_JTAG_INSTALL_SIGNED.*\.bin is complete"
    return run_test_validate_terminal_outputs(executable_path, '--pbc_update_firmware_latest', expected_output)

def run_test_check_tool_version(executable_path):
    # Using a regular expression to match the fixed part of the string ilink test tool version
    expected_values = r"The version of the ilink test tool is:.*"
    return run_test_validate_terminal_outputs(executable_path, '--ilinktesttool_version', expected_values)

def run_test_validate_terminal_outputs(executable_path, argument, expected_output):
    logger.info(f"Running the test with argument: {argument}")

    output = run_subprocess(executable_path, argument)
    if output is None:
        return False  # Test failed

    logger.info(f"Test output:\n{output}")

    # Use regular expressions to check if the expected strings are in the output
    if not re.search(expected_output, output):
        logger.error(f"'{expected_output}' not found in '{output}'")
        return False
    return True

def main():
    test_results = {
        'pbc_status': False,
        'pbc_about': False,
        'pbc_error': False,
        'pbc_update_firmware_latest': False,
        'ilink_test_tool_version': False
    }

    try:
        # Setup: Create the executable
        run_pyinstaller()

        # Get the root directory of the project
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        executable_path = os.path.join(root_dir, 'dist', 'ilink_test_tool')

        # Wait for the executable to be created by PyInstaller
        wait_for_executable(executable_path)

        # Run all tests and track the status
        test_results['pbc_status'] = run_test_pbc_status(executable_path)
        test_results['pbc_about'] = run_test_pbc_about(executable_path)
        test_results['pbc_error'] = run_test_pbc_error(executable_path)
        test_results['pbc_update_firmware_latest'] = run_test_firmware_update_to_latest(executable_path)
        test_results['ilink_test_tool_version'] = run_test_check_tool_version(executable_path)

    finally:
        # Teardown: Clean up after the test
        cleanup()

    # Summary of test results
    logger.info("\nTest Summary:")
    for test, passed in test_results.items():
        status = "PASSED" if passed else "FAILED"
        logger.info(f"Test {test}: {status}")

    # Final status: If any test failed, return a non-zero exit code
    if all(test_results.values()):
        logger.info(constants.TEST_PASSED_GENERIC)
    else:
        logger.error(constants.TEST_FAILED_GENERIC)
        sys.exit(1)


# Using this main function as standalone test launcher.
if __name__ == '__main__':
    main()
