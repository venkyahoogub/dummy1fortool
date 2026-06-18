import sys
import pbc.get_about as get_about
import pbc.get_status as get_status
import pbc.get_help as get_help
import pbc.firmware_installer as firmware_installer
import pbc.get_toolversion as get_toolversion
import common_utilities.constants as constants
from common_utilities.log_config import logger


def handle_command(cmd: str):
    """
    Handles a single user command.
    """
    cmd = cmd.strip().lower()

    if cmd in ["--pbc_about", "pbc_about"]:
        get_about.get_about_info()
    elif cmd in ["--pbc_status", "pbc_status"]:
        get_status.get_status_info()
    elif cmd in ["--pbc_update_firmware_latest", "pbc_update_firmware_latest"]:
        firmware_installer.download_teamcity_artifacts_and_install()
    elif cmd in ["--ilinktesttool_version", "ilinktesttool_version"]:
        get_toolversion.get_toolversion_info()
    elif cmd in ["--help", "help"]:
        get_help.get_help_info()
    elif cmd in ["exit", "quit"]:
        logger.info("Exiting iLink tool...")
        return False
    else:
        logger.info(constants.PBC_INCORRECT_PARAMETER_MESSAGE)

    return True


def repl():
    """
    Runs the interactive REPL loop.
    """
    logger.info("Welcome to the iLink Test Tool (interactive mode). Type 'help' for commands, 'exit' to quit.")
    while True:
        try:
            cmd = input("iLink> ")
        except (KeyboardInterrupt, EOFError):
            logger.info("\nExiting iLink tool...")
            break

        if not handle_command(cmd):
            break


def main():
    """
    Entry point of the iLink test tool.
    Converts command-line arguments to lowercase and checks for the flag.
    If arguments are provided, runs once; otherwise, launches interactive mode.
    """
    if len(sys.argv) > 1:
        # one-shot mode
        args = " ".join(sys.argv[1:])
        handle_command(args)
    else:
        # interactive mode
        repl()

# The main below is needed because PyInstaller imports your script during packaging,
# and without this guard, main() runs unexpectedly.
# The `if __name__ == "__main__":` ensures main() only runs when executed directly as an executable,
# preventing the above side effect.
if __name__ == "__main__":
    main()
