#!/bin/bash

# Create and activate virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements_native.txt

# Install system dependencies
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Installing system dependencies using Homebrew..."
    
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo "Homebrew not found. Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    # Install poppler for PDF processing
    echo "Installing poppler..."
    brew install poppler
    
    # Install Tesseract and language packs
    echo "Installing Tesseract OCR..."
    brew install tesseract
    echo "Installing Tesseract language packs..."
    brew install tesseract-lang
    
    # Verify Tesseract installation
    if ! command -v tesseract &> /dev/null; then
        echo "Error: Tesseract installation failed"
        exit 1
    fi
    
    # Print Tesseract version and available languages
    echo "Tesseract version:"
    tesseract --version
    echo "Available languages:"
    tesseract --list-langs
    
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Installing system dependencies using apt..."
    sudo apt-get update
    sudo apt-get install -y poppler-utils tesseract-ocr tesseract-ocr-heb tesseract-ocr-eng
fi

echo "Dependencies installed successfully!" 