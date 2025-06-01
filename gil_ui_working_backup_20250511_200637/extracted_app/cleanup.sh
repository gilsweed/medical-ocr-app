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

# Function to check if a process is running on a port
check_port() {
    local port=$1
    if lsof -i :$port > /dev/null; then
        return 0
    else
        return 1
    fi
}

# Function to kill process on a port
kill_port() {
    local port=$1
    if check_port $port; then
        print_warning "Port $port is in use. Attempting to kill the process..."
        lsof -ti :$port | xargs kill -9
        sleep 2
    fi
}

# Clean up Python environment
cleanup_python() {
    print_status "Cleaning up Python environment..."

    cd backend
    
    # Remove virtual environment
    if [ -d "venv" ]; then
        rm -rf venv
        print_status "Removed Python virtual environment"
    fi

    # Remove Python cache files
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
    find . -type f -name "*.pyc" -delete
    print_status "Removed Python cache files"

    cd ..
}

# Clean up Node.js environment
cleanup_node() {
    print_status "Cleaning up Node.js environment..."

    # Remove node_modules
    if [ -d "node_modules" ]; then
        rm -rf node_modules
        print_status "Removed node_modules"
    fi

    # Remove package-lock.json
    if [ -f "package-lock.json" ]; then
        rm package-lock.json
        print_status "Removed package-lock.json"
    fi
}

# Clean up build artifacts
cleanup_build() {
    print_status "Cleaning up build artifacts..."

    # Remove dist directory
    if [ -d "dist" ]; then
        rm -rf dist
        print_status "Removed dist directory"
    fi

    # Remove build directory
    if [ -d "build" ]; then
        rm -rf build
        print_status "Removed build directory"
    fi
}

# Clean up logs
cleanup_logs() {
    print_status "Cleaning up logs..."

    # Remove log files
    if [ -d "logs" ]; then
        rm -rf logs/*
        print_status "Removed log files"
    fi
}

# Kill running processes
kill_processes() {
    print_status "Killing running processes..."

    # Kill any process using port 8080
    kill_port 8080

    print_status "Killed running processes"
}

# Main cleanup process
main() {
    print_status "Starting cleanup process..."

    # Kill running processes
    kill_processes

    # Clean up Python environment
    cleanup_python

    # Clean up Node.js environment
    cleanup_node

    # Clean up build artifacts
    cleanup_build

    # Clean up logs
    cleanup_logs

    print_status "Cleanup complete!"
}

# Run the cleanup
main 