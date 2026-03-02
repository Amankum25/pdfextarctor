#!/bin/bash
# Render build script for Python backend

set -o errexit  # Exit on error

echo "Upgrading pip..."
pip install --upgrade pip setuptools wheel

echo "Installing Python dependencies..."
pip install --no-cache-dir -r requirements.txt

echo "Creating necessary directories..."
mkdir -p backend/faiss_index

echo "Build completed successfully!"
