#!/bin/bash

# This script generates the Python gRPC code from the .proto files.

PROTO_DIR=./shared/proto
OUTPUT_DIR=./shared/proto

# Create the output directory if it doesn't exist
mkdir -p ${OUTPUT_DIR}

# Generate gRPC code for all .proto files
python -m grpc_tools.protoc \
    -I${PROTO_DIR} \
    --python_out=${OUTPUT_DIR} \
    --grpc_python_out=${OUTPUT_DIR} \
    ${PROTO_DIR}/*.proto

# Add __init__.py to the generated directories to make them packages
touch ${OUTPUT_DIR}/__init__.py
find ${OUTPUT_DIR} -type d -exec touch {}/__init__.py \;
