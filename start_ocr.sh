#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to log messages
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

# Function to log errors
error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

# Function to kill process on a port
kill_port() {
    local port=$1
    log "Checking for processes on port $port..."
    
    if lsof -ti :$port > /dev/null; then
        log "Found process on port $port, killing it..."
        sudo lsof -ti :$port | xargs -r sudo kill -9 2>/dev/null
        lsof -ti :$port | xargs -r kill -9 2>/dev/null
        sleep 2
    else
        log "No process found on port $port"
    fi
}

# Function to check if a port is available
check_port() {
    local port=$1
    if lsof -ti :$port > /dev/null; then
        return 1
    fi
    return 0
}

# Function to start backend server
start_backend() {
    log "Starting backend server..."
    cd /Users/gilsweed/Desktop/Brurya/gil/backend
    
    # Start backend in background
    python3 main.py > backend.log 2>&1 &
    BACKEND_PID=$!
    
    # Wait for backend to start
    for i in {1..30}; do
        if curl -s http://localhost:8082/health > /dev/null; then
            log "Backend server started successfully"
            return 0
        fi
        sleep 1
    done
    
    error "Backend server failed to start"
    return 1
}

# Function to start frontend
start_frontend() {
    log "Starting frontend..."
    cd /Users/gilsweed/Desktop/Brurya/gil
    npm start > frontend.log 2>&1 &
    FRONTEND_PID=$!
}

# Function to monitor logs
monitor_logs() {
    log "Monitoring logs..."
    tail -f /Users/gilsweed/Desktop/Brurya/gil/backend/backend.log /Users/gilsweed/Desktop/Brurya/gil/frontend.log
}

# Main execution
main() {
    # Kill existing processes
    kill_port 8080
    kill_port 8082
    
    # Start backend
    if ! start_backend; then
        error "Failed to start backend server"
        exit 1
    fi
    
    # Start frontend
    start_frontend
    
    # Monitor logs
    monitor_logs
}

# Cleanup on exit
cleanup() {
    log "Cleaning up..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    kill_port 8080
    kill_port 8082
}

# Set up cleanup trap
trap cleanup EXIT

# Run main function
main
