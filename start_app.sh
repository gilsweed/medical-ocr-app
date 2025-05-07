#!/bin/bash

# Change to the project directory
cd "$(dirname "$0")"

# Start the backend server in the background
cd backend
python3 app.py &
BACKEND_PID=$!

# Start the frontend server
cd ..
npm start

# When the frontend is closed, also close the backend
kill $BACKEND_PID 