#!/bin/bash

# Create a temporary icon file
cat > ~/Desktop/medical_icon.svg << 'EOL'
<?xml version="1.0" encoding="UTF-8"?>
<svg width="128" height="128" version="1.1" viewBox="0 0 128 128" xmlns="http://www.w3.org/2000/svg">
 <circle cx="64" cy="64" r="60" fill="#4a90e2"/>
 <path d="m64 32v64m-32-32h64" stroke="#fff" stroke-width="12" stroke-linecap="round"/>
</svg>
EOL

# Convert SVG to ICNS
mkdir -p ~/Desktop/medical_icon.iconset
sips -s format png ~/Desktop/medical_icon.svg --out ~/Desktop/medical_icon.iconset/icon_16x16.png -z 16 16
sips -s format png ~/Desktop/medical_icon.svg --out ~/Desktop/medical_icon.iconset/icon_32x32.png -z 32 32
sips -s format png ~/Desktop/medical_icon.svg --out ~/Desktop/medical_icon.iconset/icon_128x128.png -z 128 128
sips -s format png ~/Desktop/medical_icon.svg --out ~/Desktop/medical_icon.iconset/icon_256x256.png -z 256 256
iconutil -c icns ~/Desktop/medical_icon.iconset

# Create the desktop shortcut with icon
cat > ~/Desktop/Medical\ App.command << 'EOL'
#!/bin/bash
cd /Users/gilsweed/Desktop/Brurya/gil
./start_app.sh
EOL

# Make it executable
chmod +x ~/Desktop/Medical\ App.command

# Set the icon
fileicon set ~/Desktop/Medical\ App.command ~/Desktop/medical_icon.icns

# Clean up temporary files
rm -rf ~/Desktop/medical_icon.svg ~/Desktop/medical_icon.iconset ~/Desktop/medical_icon.icns 