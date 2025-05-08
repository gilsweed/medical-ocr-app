#!/bin/bash

# Set up error handling
set -e

echo "Setting up Python virtual environment..."

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install PyQt6 pytesseract Pillow pdf2image pyobjc

echo "Virtual environment setup complete" 