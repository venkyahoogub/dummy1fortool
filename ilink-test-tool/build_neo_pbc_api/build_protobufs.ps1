# Stop on any error
$ErrorActionPreference = "Stop"

# Resolve Absolute Paths: $PSScriptRoot is root/build_neo_pbc_api
$SCRIPT_DIR = $PSScriptRoot
$ROOT_DIR = Split-Path -Path $SCRIPT_DIR -Parent

# Paths to the .proto file (root/neo_pbc_api/pbc.proto)
$PROTO_DIR = Join-Path $ROOT_DIR "neo_pbc_api"
$PROTO_FILE = Join-Path $PROTO_DIR "pbc.proto"

# Output directories (relative to THIS script in build_neo_pbc_api)
$C_OUTPUT_DIR = Join-Path $SCRIPT_DIR "source\c"
$PYTHON_OUTPUT_DIR = Join-Path $SCRIPT_DIR "source\python"

# Tool Paths (root/nanopb/generator/...)
$NANOPB_PATH = Join-Path $ROOT_DIR "nanopb\generator\protoc-gen-nanopb.bat"
$PROTOC_PATH = Join-Path $ROOT_DIR "nanopb\generator\protoc.bat"

# Create output directories
if (-not (Test-Path $C_OUTPUT_DIR)) {
    New-Item -ItemType Directory -Force -Path $C_OUTPUT_DIR | Out-Null
}
if (-not (Test-Path $PYTHON_OUTPUT_DIR)) {
    New-Item -ItemType Directory -Force -Path $PYTHON_OUTPUT_DIR | Out-Null
}

# Verify Files Exist
if (-not (Test-Path $PROTO_FILE)) { Write-Error "CANNOT FIND PROTO FILE AT: $PROTO_FILE"; exit 1 }
if (-not (Test-Path $NANOPB_PATH)) { Write-Error "CANNOT FIND NANOPB AT: $NANOPB_PATH"; exit 1 }

# Execute Nanopb (C Output)
Write-Host "--- Generating C protobuf files ---"
& $NANOPB_PATH "--nanopb_opt=-I$PROTO_DIR" "--nanopb_out=$C_OUTPUT_DIR" "$PROTO_FILE"

# Execute Protoc (Python Output)
Write-Host "--- Generating Python protobuf files ---"
& $PROTOC_PATH "-I=$PROTO_DIR" "--python_out=$PYTHON_OUTPUT_DIR" "$PROTO_FILE"

Write-Host "SUCCESS: Protobuf generation complete."
