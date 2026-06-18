# Stop execution on any error
$ErrorActionPreference = "Stop"

# -------------------------------------------------------------------
# Arguments
# -------------------------------------------------------------------
if ($args.Count -lt 1) {
    Write-Error "Usage: .\build_installer.ps1 <version>"
    exit 1
}

$VERSION = $args[0]

# -------------------------------------------------------------------
# Resolve paths
# -------------------------------------------------------------------
$SCRIPT_DIR = $PSScriptRoot
$ROOT_DIR = Split-Path -Path $SCRIPT_DIR -Parent

$PYTHON_CLI_FILE = Join-Path $SCRIPT_DIR "ilink_test_tool.py"
$PYTHON_GUI_FILE = Join-Path $SCRIPT_DIR "ilink_test_tool_gui.py"

$PBC_FILE = "$ROOT_DIR\build_neo_pbc_api\source\python\pbc_pb2.py"
$HBC_FILE = "$ROOT_DIR\build_neo_hbc_api\source\python\hbc_pb2.py"
$CAL_FILE = "$ROOT_DIR\neo-calibration-server-api\source\python\calibration_server_api_pb2.py"
$UVC_FILE = "$SCRIPT_DIR\uvc\UvcServices_pb2.py"

$PROTOBUF_BUILD_SCRIPT_PBC = "$ROOT_DIR\build_neo_pbc_api\build_protobufs.ps1"
$PROTOBUF_BUILD_SCRIPT_HBC = "$ROOT_DIR\build_neo_hbc_api\build_protobufs.ps1"
$PROTOBUF_BUILD_SCRIPT_CAL = "$ROOT_DIR\build_neo_cal_server_api\build_protobufs.ps1"

$ENV_FILE = Join-Path $SCRIPT_DIR ".env"
$SRC_FOLDER = Join-Path $ROOT_DIR "source"
$GUI_RESOURCES = Join-Path $SCRIPT_DIR "resources"

$NANOPB = Join-Path $ROOT_DIR "nanopb"

# -------------------------------------------------------------------
# Ensure required tools exist
# -------------------------------------------------------------------
Write-Host "Checking nanopb and protoc binaries..."

$PROTOC_GEN_NANOPB = "$NANOPB\generator\protoc-gen-nanopb.bat"
$PROTOC_EXE = "$NANOPB\generator\protoc.bat"

if (-not (Test-Path $PROTOC_GEN_NANOPB)) { Write-Error "protoc-gen-nanopb not found at $PROTOC_GEN_NANOPB"; exit 1 }
if (-not (Test-Path $PROTOC_EXE)) { Write-Error "protoc not found at $PROTOC_EXE"; exit 1 }

Write-Host "Staging nanopb tools..."
Copy-Item $PROTOC_GEN_NANOPB -Destination "$SCRIPT_DIR\protoc-gen-nanopb.bat" -Force
Copy-Item $PROTOC_EXE -Destination "$SCRIPT_DIR\protoc.bat" -Force

# Add current SCRIPT_DIR directory to the temp session PATH
$env:PATH = "$SCRIPT_DIR;" + $env:PATH

# -------------------------------------------------------------------
# Update .env with quoted version
# -------------------------------------------------------------------
$key = "ILINK_TEST_TOOL_VERSION"
$newLine = "$key='`"$VERSION`"'"
Write-Host "Updating $ENV_FILE with $newLine"

if (Test-Path $ENV_FILE) {
    $lines = Get-Content $ENV_FILE
    if ($lines -match "^$key=") {
        $lines = $lines -replace "^$key=.*", $newLine
    } else {
        $lines += $newLine
    }
    Set-Content -Path $ENV_FILE -Value $lines
} else {
    Set-Content -Path $ENV_FILE -Value $newLine
}

Write-Host "Current .env contents:"
Get-Content $ENV_FILE | ForEach-Object { Write-Host $_ }

# -------------------------------------------------------------------
# Build protobuf files
# -------------------------------------------------------------------
function Build-ProtobufFile {
    param($scriptPath, $description)
    if (-not (Test-Path $scriptPath)) { Write-Error "Missing script: $scriptPath"; exit 1 }
    
    Write-Host $description
    $originalDir = Get-Location
    Set-Location (Split-Path $scriptPath)
    
    & $scriptPath
    
    Set-Location $originalDir
}

Build-ProtobufFile $PROTOBUF_BUILD_SCRIPT_HBC "Building HBC protobuf Python files"
Build-ProtobufFile $PROTOBUF_BUILD_SCRIPT_PBC "Building PBC protobuf Python files"
Build-ProtobufFile $PROTOBUF_BUILD_SCRIPT_CAL "Building Calibration Server protobuf Python files"

# -------------------------------------------------------------------
# PyInstaller CLI
# -------------------------------------------------------------------
Write-Host "Running PyInstaller for CLI..."
pyinstaller --clean --onefile `
  --hidden-import=google.protobuf `
  --hidden-import=google.protobuf.any_pb2 `
  --hidden-import=google.protobuf.internal `
  --hidden-import=google.protobuf.internal.builder `
  --add-data "$($PBC_FILE);." `
  --add-data "$($UVC_FILE);." `
  --add-data "$($ENV_FILE);." `
  --add-data "$($CAL_FILE);." `
  --add-data "$($SRC_FOLDER);source" `
  "$PYTHON_CLI_FILE"

# -------------------------------------------------------------------
# PyInstaller GUI
# -------------------------------------------------------------------
Write-Host "Running PyInstaller for GUI..."
pyinstaller --clean --onefile `
  --hidden-import=cv2 `
  --hidden-import=PIL._tkinter_finder `
  --hidden-import=google.protobuf `
  --hidden-import=google.protobuf.any_pb2 `
  --hidden-import=google.protobuf.internal `
  --hidden-import=google.protobuf.internal.builder `
  --add-data "$($PBC_FILE);." `
  --add-data "$($HBC_FILE);." `
  --add-data "$($UVC_FILE);." `
  --add-data "$($CAL_FILE);." `
  --add-data "$($ENV_FILE);." `
  --add-data "$($SRC_FOLDER);source" `
  --add-data "$($GUI_RESOURCES);resources" `
  "$PYTHON_GUI_FILE"

Write-Host "Windows build completed successfully."
