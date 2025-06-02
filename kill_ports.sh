#!/bin/bash

echo "Aggressively killing processes on ports 8080 and 8082..."

# Function to kill process on a port
kill_port() {
    local port=$1
    echo "Checking for processes on port $port..."
    
    # Try multiple methods to find and kill the process
    if lsof -ti :$port > /dev/null; then
        echo "Found process on port $port, killing it..."
        # Try sudo first
        sudo lsof -ti :$port | xargs -r sudo kill -9 2>/dev/null
        # If that fails, try without sudo
        lsof -ti :$port | xargs -r kill -9 2>/dev/null
        # Wait a moment for the port to be released
        sleep 2
    else
        echo "No process found on port $port"
    fi
}

# Kill processes on both ports
kill_port 8080
kill_port 8082

# Additional cleanup
echo "Performing additional cleanup..."
pkill -f "python3 main.py"
pkill -f "node"
pkill -f "electron"

echo "Waiting for ports to be fully released..."
sleep 3

# Verify ports are free
echo "Verifying ports are free..."
if lsof -i :8080 > /dev/null; then
    echo "WARNING: Port 8080 is still in use!"
else
    echo "Port 8080 is free"
fi

if lsof -i :8082 > /dev/null; then
    echo "WARNING: Port 8082 is still in use!"
else
    echo "Port 8082 is free"
fi

echo "Cleanup complete!" 