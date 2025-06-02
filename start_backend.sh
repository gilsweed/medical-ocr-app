#!/bin/bash

# Kill any process using port 8082
PID=$(lsof -ti :8082)
if [ ! -z "$PID" ]; then
  echo "Killing process on port 8082 (PID: $PID)"
  kill $PID
fi

# Set up ABBYY SDK environment variables
export DYLD_FRAMEWORK_PATH=/Users/gilsweed/Desktop/Brurya/ABBYY_SDK
export DYLD_LIBRARY_PATH=/Users/gilsweed/Desktop/Brurya/ABBYY_SDK/FREngine.framework/Versions/A/Libraries
export FREngineDataFolder=/Users/gilsweed/Desktop/Brurya/ABBYY_SDK/Data

# Create data folder if it doesn't exist
mkdir -p "$FREngineDataFolder"

# Start backend
echo "Starting backend with ABBYY SDK environment..."
cd backend
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3 main.py
