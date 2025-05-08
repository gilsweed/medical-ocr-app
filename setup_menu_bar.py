import os
import sys
import plistlib
import shutil

APP_NAME = "OCR Scanner"
APP_ID = "com.ocr.scanner"

# Create Info.plist
info_plist = {
    'CFBundleName': APP_NAME,
    'CFBundleDisplayName': APP_NAME,
    'CFBundleIdentifier': APP_ID,
    'CFBundleVersion': "1.0.0",
    'CFBundleShortVersionString': "1.0.0",
    'CFBundlePackageType': "APPL",
    'CFBundleSignature': "????",
    'LSMinimumSystemVersion': "10.13.0",
    'NSHighResolutionCapable': True,
    'LSUIElement': False,  # Show in Dock
    'NSPrincipalClass': "NSApplication",
    'CFBundleIconFile': 'AppIcon.icns',
    'LSBackgroundOnly': False,  # Ensure it's not background only
    'NSAppleEventsEnabled': True,  # Enable Apple Events
    'LSApplicationCategoryType': 'public.app-category.utilities',  # Set as utility app
    'LSArchitecturePriority': ['arm64'],  # Force arm64 architecture
}

# Create the app bundle structure
def create_app_bundle():
    try:
        app_path = f"{APP_NAME}.app"
        contents_path = os.path.join(app_path, "Contents")
        macos_path = os.path.join(contents_path, "MacOS")
        resources_path = os.path.join(contents_path, "Resources")
        
        # Create directories
        os.makedirs(macos_path, exist_ok=True)
        os.makedirs(resources_path, exist_ok=True)
        
        # Create the launcher script with proper environment setup
        launcher_script = f"""#!/bin/bash

# Enable error reporting
set -e

# Force arm64 architecture
export ARCHFLAGS="-arch arm64"

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${{BASH_SOURCE[0]}}" )" && pwd )"
APP_DIR="$(dirname "$SCRIPT_DIR")"
RESOURCES_DIR="$APP_DIR/Resources"
APP_ROOT="$RESOURCES_DIR/app"

# Log file for debugging
LOG_FILE="$APP_ROOT/launcher.log"

# Function to log messages
log() {{
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}}

# Start logging
log "Starting launcher script"
log "Script directory: $SCRIPT_DIR"
log "App directory: $APP_DIR"
log "Resources directory: $RESOURCES_DIR"
log "App root: $APP_ROOT"

# Check if required files exist
if [ ! -f "$APP_ROOT/mac_app.py" ]; then
    log "Error: mac_app.py not found in $APP_ROOT"
    exit 1
fi

# Change to the app directory
cd "$APP_ROOT"
log "Changed to directory: $(pwd)"

# Set up Python environment
export PYTHONPATH="$APP_ROOT:$PYTHONPATH"
export PATH="/usr/local/bin:/usr/bin:/bin:$PATH"
log "Set up environment variables"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    log "Found virtual environment, activating..."
    source venv/bin/activate
    log "Virtual environment activated"
else
    log "No virtual environment found, using system Python"
fi

# Set Qt plugin path
export QT_PLUGIN_PATH="$APP_ROOT/venv/lib/python3.13/site-packages/PyQt6/Qt6/plugins"
log "Set QT_PLUGIN_PATH to $QT_PLUGIN_PATH"

# Set Qt library path
export DYLD_LIBRARY_PATH="$APP_ROOT/venv/lib/python3.13/site-packages/PyQt6/Qt6/lib:$DYLD_LIBRARY_PATH"
log "Set DYLD_LIBRARY_PATH to include Qt libraries"

# Set Qt framework path
export DYLD_FRAMEWORK_PATH="$APP_ROOT/venv/lib/python3.13/site-packages/PyQt6/Qt6/lib:$DYLD_FRAMEWORK_PATH"
log "Set DYLD_FRAMEWORK_PATH to include Qt frameworks"

# Check Python version and architecture
log "Python version: $(python3 --version)"
log "Python architecture: $(arch)"

# Run the Python script with arm64 architecture and debug output
log "Starting mac_app.py with arm64 architecture"
arch -arm64 "$APP_ROOT/venv/bin/python3" mac_app.py 2>> "$LOG_FILE"

# Log any errors
if [ $? -ne 0 ]; then
    log "Error: Python script failed with exit code $?"
    exit 1
fi

log "Python script completed successfully"
"""
        
        with open(os.path.join(macos_path, APP_NAME), 'w') as f:
            f.write(launcher_script)
        
        # Make the launcher executable
        os.chmod(os.path.join(macos_path, APP_NAME), 0o755)
        
        # Write Info.plist
        with open(os.path.join(contents_path, 'Info.plist'), 'wb') as f:
            plistlib.dump(info_plist, f)
        
        # Copy icons if they exist
        if os.path.exists('icon.iconset'):
            # Convert iconset to icns
            os.system('iconutil -c icns icon.iconset')
            if os.path.exists('icon.icns'):
                shutil.copy('icon.icns', os.path.join(resources_path, 'AppIcon.icns'))
        
        if os.path.exists('menu_bar_icon.png'):
            shutil.copy('menu_bar_icon.png', os.path.join(resources_path, 'menu_bar_icon.png'))
        
        print(f"Created app bundle at: {os.path.abspath(app_path)}")
        return True
    except Exception as e:
        print(f"Error creating app bundle: {str(e)}")
        return False

if __name__ == "__main__":
    success = create_app_bundle()
    if not success:
        sys.exit(1) 