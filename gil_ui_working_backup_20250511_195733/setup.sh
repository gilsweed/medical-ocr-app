#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status messages
print_status() {
    echo -e "${GREEN}[✓] $1${NC}"
}

print_error() {
    echo -e "${RED}[✗] $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[!] $1${NC}"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check system requirements
check_requirements() {
    print_status "Checking system requirements..."

    # Check Node.js
    if ! command_exists node; then
        print_error "Node.js is not installed. Please install Node.js v14 or higher."
        exit 1
    fi

    # Check Python
    if ! command_exists python3; then
        print_error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi

    # Check Tesseract
    if ! command_exists tesseract; then
        print_warning "Tesseract OCR is not installed. Please install it:"
        echo "  - macOS: brew install tesseract"
        echo "  - Linux: sudo apt-get install tesseract-ocr"
        echo "  - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki"
        exit 1
    fi

    print_status "All system requirements met."
}

# Setup Python virtual environment
setup_python_env() {
    print_status "Setting up Python virtual environment..."

    cd backend

    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi

    # Activate virtual environment
    source venv/bin/activate

    # Install dependencies
    pip install --upgrade pip
    pip install -r requirements.txt

    # Deactivate virtual environment
    deactivate

    cd ..
    print_status "Python environment setup complete."
}

# Setup Node.js environment
setup_node_env() {
    print_status "Setting up Node.js environment..."

    # Install dependencies
    npm install

    print_status "Node.js environment setup complete."
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."

    # Create logs directory if it doesn't exist
    mkdir -p logs

    print_status "Directory structure setup complete."
}

# Main setup process
main() {
    print_status "Starting setup process..."

    # Check system requirements
    check_requirements

    # Create necessary directories
    create_directories

    # Setup Python environment
    setup_python_env

    # Setup Node.js environment
    setup_node_env

    print_status "Setup complete! You can now run the application with:"
    echo "  npm run dev"
}

# Run the setup
main 