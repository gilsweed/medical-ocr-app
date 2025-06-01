#!/bin/bash

# Exit on error
set -e

# Create logs directory
mkdir -p logs

# Function to log messages with timestamps
log() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local message="[$timestamp] $1"
    echo "$message" | tee -a logs/auto.log
}

# Function to handle errors
handle_error() {
    log "ERROR: $1"
    if [[ "$2" == "critical" ]]; then
        log "CRITICAL ERROR: This requires manual intervention. Please check the logs."
        echo "$1" > logs/last_error.txt
        exit 1
    fi
}

# Function to cleanup processes
cleanup() {
    log "Cleaning up processes..."
    pkill -f "python|node" || true
    rm -f backend/port.txt
    
    # Log cleanup completion
    log "Cleanup completed"
}

# Function to check system requirements
check_requirements() {
    log "Checking system requirements..."
    
    # Check Python version
    if ! command -v python3 &> /dev/null; then
        handle_error "Python 3 is not installed" "critical"
    else
        log "Python 3 found: $(python3 --version)"
    fi
    
    # Check Node.js version
    if ! command -v node &> /dev/null; then
        handle_error "Node.js is not installed" "critical"
    else
        log "Node.js found: $(node --version)"
    fi
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        handle_error "npm is not installed" "critical"
    else
        log "npm found: $(npm --version)"
    fi
}

# Function to setup environment
setup_environment() {
    log "Setting up environment..."
    
    # Create necessary directories
    mkdir -p backend/logs
    log "Created backend/logs directory"
    
    # Create and activate Python virtual environment
    if [ ! -d "backend/venv" ]; then
        log "Creating Python virtual environment..."
        python3 -m venv backend/venv
        log "Virtual environment created successfully"
    else
        log "Using existing virtual environment"
    fi
    
    source backend/venv/bin/activate
    log "Virtual environment activated"
    
    # Install Python dependencies
    log "Installing Python dependencies..."
    pip install -r backend/requirements.txt > logs/pip_install.log 2>&1
    if [ $? -eq 0 ]; then
        log "Python dependencies installed successfully"
    else
        handle_error "Failed to install Python dependencies. Check logs/pip_install.log for details" "critical"
    fi
    
    # Install Node.js dependencies
    log "Installing Node.js dependencies..."
    npm install > logs/npm_install.log 2>&1
    if [ $? -eq 0 ]; then
        log "Node.js dependencies installed successfully"
    else
        handle_error "Failed to install Node.js dependencies. Check logs/npm_install.log for details" "critical"
    fi
}

# Function to start the application
start_application() {
    log "Starting application..."
    
    # Start the backend
    log "Starting backend server..."
    cd backend
    ./venv/bin/python supervisor.py > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    cd ..
    log "Backend server started with PID: $BACKEND_PID"
    
    # Wait for backend to be ready
    log "Waiting for backend to be ready..."
    for i in {1..30}; do
        if curl -s http://localhost:8080/health > /dev/null; then
            log "Backend is ready"
            break
        fi
        if [ $i -eq 30 ]; then
            handle_error "Backend failed to start" "critical"
        fi
        sleep 1
    done
    
    # Start the frontend
    log "Starting frontend..."
    npm start > logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    log "Frontend started with PID: $FRONTEND_PID"
    
    # Monitor processes
    log "Starting process monitoring..."
    while true; do
        if ! kill -0 $BACKEND_PID 2>/dev/null; then
            handle_error "Backend process died" "critical"
        fi
        if ! kill -0 $FRONTEND_PID 2>/dev/null; then
            handle_error "Frontend process died" "critical"
        fi
        sleep 5
    done
}

# Main execution
trap cleanup EXIT INT TERM

log "Starting automated build and run process..."

# Check requirements
check_requirements

# Setup environment
setup_environment

# Start application
start_application 