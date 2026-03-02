#!/bin/bash
# Render build script for Python backend with system dependencies

set -o errexit  # Exit on error

echo "Installing system dependencies..."
apt-get update
apt-get install -y --no-install-recommends \
    build-essential \
    libopenblas-dev \
    libgomp1

echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel

echo "Installing Python dependencies..."
pip install --no-cache-dir -r requirements.txt

echo "Creating necessary directories..."
mkdir -p backend/faiss_index

echo "Build completed successfully!"
