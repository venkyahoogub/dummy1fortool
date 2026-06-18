#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROTO_DIR="$SCRIPT_DIR/../neo-calibration-server-api"
PROTO_FILE="calibration_server_api.proto"

mkdir -p "$PROTO_DIR/source/python"

protoc \
    -I="$PROTO_DIR" \
    --python_out="$PROTO_DIR/source/python" \
    "$PROTO_DIR/$PROTO_FILE"