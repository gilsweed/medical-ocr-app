#!/bin/bash

# Start backend
cd /Users/gilsweed/Desktop/Brurya/gil/backend
echo "Starting backend..."
python3 main.py &
BACKEND_PID=$!

# Wait for backend to be ready
echo "Waiting for backend to be ready..."
until curl -s http://localhost:8082/health | grep -q 'ok'; do
  sleep 1
done

# Start Electron app
cd /Users/gilsweed/Desktop/Brurya/gil
echo "Starting Electron app..."
npx electron .

# When Electron app closes, stop backend
echo "Stopping backend..."
kill $BACKEND_PID
