#!/bin/bash

# Step 1: Go to project root
cd /Users/gilsweed/Desktop/Brurya/gil || exit 1

# Step 2: Clean npm cache and remove old modules/lock file
echo "Cleaning npm cache and removing old node_modules and lock file..."
npm cache clean --force
rm -rf node_modules package-lock.json

# Step 3: Install all dependencies (with fallback registry)
echo "Installing dependencies..."
npm install || npm install --registry=https://registry.npmjs.org/

# Step 4: Install Electron (if not already present)
echo "Ensuring Electron is installed..."
npm install electron

# Step 5: Open a new Terminal window for the backend
echo "Opening backend in a new Terminal window..."
osascript <<EOF
tell application "Terminal"
    do script "cd /Users/gilsweed/Desktop/Brurya/gil/backend && python3 main.py"
    activate
end tell
EOF

# Step 6: Start the Electron app in this terminal
echo "Starting Electron app in this terminal..."
./node_modules/.bin/electron .

echo "If you see any missing module errors, run: npm install <missing-module-name> in /Users/gilsweed/Desktop/Brurya/gil"
