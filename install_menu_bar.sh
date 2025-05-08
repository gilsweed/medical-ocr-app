#!/bin/bash

# Exit on error
set -e

echo "Creating app bundle..."
python3 setup_menu_bar.py

if [ ! -d "OCR Scanner.app" ]; then
    echo "Error: App bundle creation failed"
    exit 1
fi

echo "Installing to Applications folder..."
# Remove existing installation if it exists
rm -rf "/Applications/OCR Scanner.app"

# Copy the app to Applications
cp -r "OCR Scanner.app" /Applications/

# Create Resources directory if it doesn't exist
mkdir -p "/Applications/OCR Scanner.app/Contents/Resources/app"

# Copy all necessary files
echo "Copying application files..."
cp -r mac_app.py requirements.txt requirements_native.txt "/Applications/OCR Scanner.app/Contents/Resources/app/"

# Copy virtual environment if it exists
if [ -d "venv" ]; then
    echo "Copying virtual environment..."
    cp -r venv "/Applications/OCR Scanner.app/Contents/Resources/app/"
fi

# Set proper permissions
chmod -R 755 "/Applications/OCR Scanner.app"
xattr -cr "/Applications/OCR Scanner.app"

echo "Installation complete!"
echo "OCR Scanner has been installed to the Applications folder"
echo "You can now find it in your Dock"
echo "To start the app, click the OCR Scanner icon in your Dock" 