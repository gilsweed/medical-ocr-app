#!/bin/bash

# Kill any process using port 8082
PID=$(lsof -ti :8082)
if [ ! -z "$PID" ]; then
  echo "Killing process on port 8082 (PID: $PID)"
  kill $PID
fi

# Start backend with ABBYY environment variables in the background
export DYLD_FRAMEWORK_PATH=/Users/gilsweed/Desktop/Brurya/ABBYY_SDK
export DYLD_LIBRARY_PATH=/Users/gilsweed/Desktop/Brurya/ABBYY_SDK/FREngine.framework/Versions/A/Libraries
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3 main.py &

# Wait a moment to ensure backend starts
sleep 2

# Start Electron frontend
npm start
