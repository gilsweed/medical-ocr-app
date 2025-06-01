#!/bin/bash

# Function to check if a port is in use
check_port() {
    lsof -i :$1 >/dev/null 2>&1
    return $?
}

# Function to wait for a port to be free
wait_for_port() {
    local port=$1
    local timeout=30
    local start_time=$(date +%s)
    
    while check_port $port; do
        if [ $(($(date +%s) - start_time)) -gt $timeout ]; then
            echo "Timeout waiting for port $port to be free"
            return 1
        fi
        echo "Waiting for port $port to be free..."
        sleep 1
    done
    return 0
}

# Function to wait for a service to be ready
wait_for_service() {
    local port=$1
    local timeout=30
    local start_time=$(date +%s)
    
    while ! curl -s http://localhost:$port/health >/dev/null; do
        if [ $(($(date +%s) - start_time)) -gt $timeout ]; then
            echo "Timeout waiting for service on port $port"
            return 1
        fi
        echo "Waiting for service on port $port..."
        sleep 1
    done
    return 0
}

# Function to cleanup processes
cleanup() {
    echo "Cleaning up processes..."
    
    # Kill any existing Python processes
    pkill -f "python.*supervisor.py" || true
    pkill -f "gunicorn" || true
    
    # Wait for ports to be free
    wait_for_port 8080
    wait_for_port 3000
    
    echo "Cleanup complete"
}

# Set up trap for cleanup on exit
trap cleanup EXIT

# Start the backend server
echo "Starting backend server..."
cd backend
python supervisor.py &
BACKEND_PID=$!

# Wait for backend to be ready
if ! wait_for_service 8080; then
    echo "Backend server failed to start"
    exit 1
fi

# Start the Electron app
echo "Starting Electron app..."
cd ..
npm start

# Wait for the backend process
wait $BACKEND_PID 