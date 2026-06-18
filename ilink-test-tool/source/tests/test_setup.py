import os
import subprocess
import sys
import shutil
# Ensures file is loaded to path for command line execution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from source.common_utilities.log_config import logger

def run_pyinstaller():
    """Set up: Run the PyInstaller command to create the executable."""
    logger.info("Creating executable using PyInstaller...")

    # Get the absolute path to ilink_test_tool.py relative to the project root
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))  # Navigate to the root of the project
    script_path = os.path.join(root_dir, 'source', 'ilink_test_tool.py')

    # Ensure the script path exists
    if not os.path.exists(script_path):
        logger.error(f"{script_path} does not exist!")
        sys.exit(1)

    # Correct path to pbc_pb2.py (relative to the root of the project)
    proto_file_path = os.path.join(root_dir, 'neo_pbc_api', 'source', 'python', 'pbc_pb2.py')

    # Ensure the proto file path exists
    if not os.path.exists(proto_file_path):
        logger.error(f"{proto_file_path} does not exist!")
        sys.exit(1)

    # Prepare the PyInstaller command with relative paths
    pyinstaller_cmd = [
        'pyinstaller', '--onefile',
        '--hidden-import=google.protobuf',
        '--hidden-import=google.protobuf.internal',
        '--hidden-import=google.protobuf.internal.builder',
        f'--add-data={proto_file_path}:.',  # Correct path to the proto file
        '--distpath', os.path.join(root_dir, 'dist'),  # Custom dist path relative to the root folder
        '--workpath', os.path.join(root_dir, 'build'),  # Custom build (work) path relative to the root folder
        script_path  # Absolute path to the script
    ]

    # Run PyInstaller command
    result = subprocess.run(pyinstaller_cmd, capture_output=True, text=True)

    if result.returncode != 0:
        logger.error("PyInstaller failed!")
        logger.error(result.stderr)
        sys.exit(1)

    logger.info("PyInstaller output:\n%s", result.stdout)

def cleanup():
    """Tear down: Delete the executable and cleanup temporary files."""
    logger.info("Cleaning up generated files...")

    # Get the project root directory
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))  # Navigate to the root of the project

    # Paths to the generated directories and spec file (relative to the project root)
    dist_dir = os.path.join(root_dir, 'dist')
    build_dir = os.path.join(root_dir, 'build')
    spec_file = os.path.join(root_dir, 'source', 'ilink_test_tool.spec')

    # Remove the generated executable and dist/build directories
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)  # Remove dist directory
        logger.info("Removed dist directory: %s", dist_dir)

    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)  # Remove build (work) directory
        logger.info("Removed build directory: %s", build_dir)

    if os.path.exists(spec_file):
        os.remove(spec_file)  # Remove the spec file
        logger.info("Removed spec file: %s", spec_file)

    logger.info("Cleanup complete.")
