#!/bin/bash
set -euo pipefail

# -------------------------------------------------------------------
# Arguments
# -------------------------------------------------------------------
if [ $# -lt 1 ]; then
  echo "Usage: $0 <version>"
  exit 1
fi

VERSION="$1"

# -------------------------------------------------------------------
# Resolve paths
# Script lives in /source
# -------------------------------------------------------------------
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

PYTHON_CLI_FILE="${SCRIPT_DIR}/ilink_test_tool.py"
PYTHON_GUI_FILE="${SCRIPT_DIR}/ilink_test_tool_gui.py"

PBC_FILE="${ROOT_DIR}/neo_pbc_api/source/python/pbc_pb2.py"
HBC_FILE="${ROOT_DIR}/neo-hbc-api/source/python/hbc_pb2.py"
UVC_FILE="${SCRIPT_DIR}/uvc/UvcServices_pb2.py"
CAL_FILE="${ROOT_DIR}/neo-calibration-server-api/source/python/calibration_server_api_pb2.py"

PROTOBUF_BUILD_SCRIPT_PBC="${ROOT_DIR}/neo_pbc_api/build_protobufs.sh"
PROTOBUF_BUILD_SCRIPT_HBC="${ROOT_DIR}/neo-hbc-api/build_protobufs.sh"
PROTOBUF_BUILD_SCRIPT_CAL="${ROOT_DIR}/build_neo_cal_server_api/build_protobufs.sh" 

ENV_FILE="${SCRIPT_DIR}/.env"
SRC_FOLDER="${ROOT_DIR}/source"
GUI_RESOURCES="${SCRIPT_DIR}/resources"

NANOPB="${ROOT_DIR}/nanopb"

# -------------------------------------------------------------------
# Ensure required tools exist and add symlinks
# -------------------------------------------------------------------
echo "Checking nanopb and protoc binaries"

if [ ! -x "${NANOPB}/generator/protoc-gen-nanopb" ]; then
  echo "Error: protoc-gen-nanopb not found or not executable at ${NANOPB}/generator/protoc-gen-nanopb"
  exit 1
fi

if [ ! -x "${NANOPB}/generator/protoc" ]; then
  echo "Error: protoc not found or not executable at ${NANOPB}/generator/protoc"
  exit 1
fi

echo "Creating symlinks for nanopb tools"
ln -sf "${NANOPB}/generator/protoc-gen-nanopb" "${SCRIPT_DIR}/protoc-gen-nanopb"
ln -sf "${NANOPB}/generator/protoc" "${SCRIPT_DIR}/protoc"

# Include the current script directory in PATH
export PATH="${SCRIPT_DIR}:$PATH"

echo "Using protoc: $(which protoc)"
echo "Using nanopb: $(which nanopb)"

# -------------------------------------------------------------------
# Update .env with quoted version
# -------------------------------------------------------------------
if [ -f "$ENV_FILE" ]; then
  echo "Updating $ENV_FILE with ILINK_TEST_TOOL_VERSION='\"$VERSION\"'"
  if grep -q "^ILINK_TEST_TOOL_VERSION=" "$ENV_FILE"; then
    sed -i "s/^ILINK_TEST_TOOL_VERSION=.*/ILINK_TEST_TOOL_VERSION='\"$VERSION\"'/" "$ENV_FILE"
  else
    echo "ILINK_TEST_TOOL_VERSION='\"$VERSION\"'" >> "$ENV_FILE"
  fi
else
  echo "ILINK_TEST_TOOL_VERSION='\"$VERSION\"'" > "$ENV_FILE"
fi

# -------------------------------------------------------------------
# File validation helper
# -------------------------------------------------------------------
validate_file() {
  local file="$1"
  local name="$2"

  if [ ! -f "$file" ]; then
    echo "Error: ${name:-File} '$file' not found."
    exit 1
  fi
}

# -------------------------------------------------------------------
# Build protobuf files
# -------------------------------------------------------------------
build_protobuf_file() {
  local script="$1"
  local description="$2"

  validate_file "$script" "$description"

  chmod +x "$script"
  echo "$description"

  (
    # Explicitly set PATH for subprocesses
    export PATH="${SCRIPT_DIR}:$PATH"
    cd "$(dirname "$script")"
    ./$(basename "$script")
  )
}

build_protobuf_file "$PROTOBUF_BUILD_SCRIPT_HBC" "Building HBC protobuf Python files"
build_protobuf_file "$PROTOBUF_BUILD_SCRIPT_PBC" "Building PBC protobuf Python files"
build_protobuf_file "$PROTOBUF_BUILD_SCRIPT_CAL" "Building Calibration Server protobuf Python files"

# -------------------------------------------------------------------
# Validate required files exist
# -------------------------------------------------------------------
validate_file "$PYTHON_CLI_FILE" "Python ILink Test Tool CLI file"
validate_file "$PYTHON_GUI_FILE" "Python ILink Test Tool GUI file"
validate_file "$PBC_FILE" "PBC file"
validate_file "$HBC_FILE" "HBC file"
validate_file "$UVC_FILE" "UVC file"
validate_file "$ENV_FILE" "ENV file"
validate_file "$CAL_FILE" "Calibration Server protobuf file"

# -------------------------------------------------------------------
# PyInstaller CLI
# -------------------------------------------------------------------
echo "Running PyInstaller for CLI"
pyinstaller --clean --onefile \
  --hidden-import=google.protobuf \
  --hidden-import=google.protobuf.any_pb2 \
  --hidden-import=google.protobuf.internal \
  --hidden-import=google.protobuf.internal.builder \
  --add-data "$PBC_FILE:." \
  --add-data "$UVC_FILE:." \
  --add-data "$ENV_FILE:." \
  --add-data "$SRC_FOLDER:source" \
  --add-data "$CAL_FILE:." \
  "$PYTHON_CLI_FILE"

echo "CLI build of linux executable has completed successfully."

# -------------------------------------------------------------------
# PyInstaller GUI
# -------------------------------------------------------------------
echo "Running PyInstaller for GUI"
pyinstaller --clean --onefile \
  --hidden-import=cv2 \
  --hidden-import=PIL._tkinter_finder \
  --hidden-import=google.protobuf \
  --hidden-import=google.protobuf.any_pb2 \
  --hidden-import=google.protobuf.internal \
  --hidden-import=google.protobuf.internal.builder \
  --add-data "$PBC_FILE:." \
  --add-data "$HBC_FILE:." \
  --add-data "$UVC_FILE:." \
  --add-data "$CAL_FILE:." \
  --add-data "$ENV_FILE:." \
  --add-data "$SRC_FOLDER:source" \
  --add-data "$GUI_RESOURCES:resources" \
  "$PYTHON_GUI_FILE"

echo "GUI build of linux executable has completed successfully."