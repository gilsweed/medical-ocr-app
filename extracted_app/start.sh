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

# Start Python backend
start_backend() {
    print_status "Starting Python backend..."

    # Kill any process using port 8080
    kill_port 8080

    cd backend
    source venv/bin/activate
    
    # Start the Python backend
    python src/app.py &
    BACKEND_PID=$!
    
    # Wait for backend to start
    print_status "Waiting for backend to start..."
    for i in {1..30}; do
        if curl -s http://localhost:8080/health > /dev/null; then
            print_status "Backend started successfully"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "Backend failed to start"
            exit 1
        fi
        sleep 1
    done

    cd ..
}

# Start Electron frontend
start_frontend() {
    print_status "Starting Electron frontend..."
    npm run dev
}

# Cleanup function
cleanup() {
    print_status "Cleaning up..."
    
    # Kill backend process
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    
    # Kill any remaining process on port 8080
    kill_port 8080
    
    print_status "Cleanup complete"
    exit 0
}

# Set up trap for cleanup
trap cleanup SIGINT SIGTERM

# Main function
main() {
    # Start backend
    start_backend

    # Start frontend
    start_frontend
}

# Run the application
main 