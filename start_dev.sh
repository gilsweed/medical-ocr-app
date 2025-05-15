#!/bin/bash

# Start the backend in a new terminal window
BACKEND_DIR="$(cd "$(dirname "$0")/backend" && pwd)"
cd "$BACKEND_DIR"
if [ ! -d "venv" ]; then
  echo "[ERROR] Python virtual environment not found in backend/venv. Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
  exit 1
fi

# macOS: open a new Terminal window and run the backend
osascript <<END
 tell application "Terminal"
   do script "cd '$BACKEND_DIR'; source venv/bin/activate; python3 main.py"
 end tell
END

# Return to project root and start Electron app
cd "$(dirname "$0")"
echo "[INFO] Starting Electron app..."
npm start 