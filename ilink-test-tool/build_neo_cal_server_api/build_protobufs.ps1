# Stop on any error
$ErrorActionPreference = "Stop"

# Resolve Absolute Paths
$SCRIPT_DIR = $PSScriptRoot
$ROOT_DIR = Split-Path -Path $SCRIPT_DIR -Parent

# Paths to the .proto file
$PROTO_DIR = Join-Path $ROOT_DIR "neo-calibration-server-api"
$PROTO_FILE = Join-Path $PROTO_DIR "calibration_server_api.proto"

# Output directories
$C_OUTPUT_DIR = Join-Path $SCRIPT_DIR "source\c"
$PYTHON_OUTPUT_DIR = Join-Path $PROTO_DIR "source\python"

# Tool Paths
$NANOPB_PATH = Join-Path $ROOT_DIR "nanopb\generator\protoc-gen-nanopb.bat"
$PROTOC_PATH = Join-Path $ROOT_DIR "nanopb\generator\protoc.bat"

# Create output directories
if (-not (Test-Path $C_OUTPUT_DIR)) {
    New-Item -ItemType Directory -Force -Path $C_OUTPUT_DIR | Out-Null
}

if (-not (Test-Path $PYTHON_OUTPUT_DIR)) {
    New-Item -ItemType Directory -Force -Path $PYTHON_OUTPUT_DIR | Out-Null
}

# Verify files exist
if (-not (Test-Path $PROTO_FILE)) {
    Write-Error "CANNOT FIND PROTO FILE AT: $PROTO_FILE"
    exit 1
}

if (-not (Test-Path $NANOPB_PATH)) {
    Write-Error "CANNOT FIND NANOPB AT: $NANOPB_PATH"
    exit 1
}

if (-not (Test-Path $PROTOC_PATH)) {
    Write-Error "CANNOT FIND PROTOC AT: $PROTOC_PATH"
    exit 1
}

# Generate C protobuf files
Write-Host "--- Generating C protobuf files ---"
& $NANOPB_PATH "--nanopb_opt=-I$PROTO_DIR" "--nanopb_out=$C_OUTPUT_DIR" "$PROTO_FILE"

# Generate Python protobuf files
Write-Host "--- Generating Python protobuf files ---"
& $PROTOC_PATH "-I=$PROTO_DIR" "--python_out=$PYTHON_OUTPUT_DIR" "$PROTO_FILE"

Write-Host "SUCCESS: Protobuf generation complete."