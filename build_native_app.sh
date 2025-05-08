#!/bin/bash

# Set up error handling
set -e

echo "Building OCR Scanner.app..."

# Get Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Using Python version: $PYTHON_VERSION"

# Create app bundle structure
APP_NAME="OCR Scanner.app"
CONTENTS_DIR="$APP_NAME/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"
RESOURCES_DIR="$CONTENTS_DIR/Resources"
FRAMEWORKS_DIR="$CONTENTS_DIR/Frameworks"
PYTHON_DIR="$RESOURCES_DIR/lib/python$PYTHON_VERSION"

# Remove existing app if it exists
rm -rf "$APP_NAME"

# Create directory structure
mkdir -p "$MACOS_DIR" "$RESOURCES_DIR" "$FRAMEWORKS_DIR" "$PYTHON_DIR"

# Copy icon
cp icon.icns "$RESOURCES_DIR/AppIcon.icns"

# Create Info.plist
cat > "$CONTENTS_DIR/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>OCRScanner</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>CFBundleIdentifier</key>
    <string>com.ocr.scanner</string>
    <key>CFBundleName</key>
    <string>OCR Scanner</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>CFBundleSupportedPlatforms</key>
    <array>
        <string>MacOSX</string>
    </array>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF

# Create launcher script
cat > "$MACOS_DIR/OCRScanner" << EOF
#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="\$(dirname "\$SCRIPT_DIR")"
RESOURCES_DIR="\$APP_DIR/Resources"

# Set up Python environment
export PYTHONPATH="\$RESOURCES_DIR/lib/python$PYTHON_VERSION/site-packages"
export DYLD_LIBRARY_PATH="\$RESOURCES_DIR/lib"

# Run the Python script
python3 "\$RESOURCES_DIR/mac_app.py"
EOF

# Make launcher script executable
chmod +x "$MACOS_DIR/OCRScanner"

# Copy Python script and dependencies
cp mac_app.py "$RESOURCES_DIR/"
cp -r venv/lib/python$PYTHON_VERSION/site-packages "$PYTHON_DIR/"

echo "App bundle created successfully at $APP_NAME"