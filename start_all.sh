#!/bin/bash

# Set environment variables for Google Cloud credentials and bucket name
export GOOGLE_APPLICATION_CREDENTIALS="/Users/gilsweed/Desktop/Brurya/gil/ocr-service-account.json"
export GCS_BUCKET_NAME="hebrew-ocr-app-bucket-gilsweed-20240516"

# Start the backend (main.py) in the background
echo "Starting backend..."
python3 backend/main.py &
BACKEND_PID=$!

# Wait for the backend to be ready
echo "Waiting for backend to be ready..."
sleep 3

# Start the Electron app
echo "Starting Electron app..."
npm start

# When Electron app closes, stop the backend
kill $BACKEND_PID