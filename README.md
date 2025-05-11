# OCR Scanner Electron App

A modern desktop application for OCR scanning and text processing, built with Electron and Python.

## Project Overview

- **Type:** Electron Desktop App
- **Backend:** Python (Flask server, OCR, PDF processing)
- **Frontend:** HTML/CSS/JS (Electron renderer)
- **Status:** Actively developed and maintained

## Features
- OCR processing for images and PDFs
- Drag-and-drop and file picker UI
- Progress bar and result/error display
- Packaged for macOS (Dock/Launchpad ready)
- Modern, user-friendly interface

## Project Structure
```
.
├── backend/           # Python backend (Flask server, OCR logic)
├── docs/              # Additional documentation
├── logs/              # Application logs
├── out/               # Build output (installers, .app, .dmg, etc.)
├── index.html         # Main UI file
├── electron.js        # Electron main process
├── package.json       # Node.js project config
├── project_state.json # Project state, version history
├── TROUBLESHOOTING.md # Troubleshooting guide
├── CHANGELOG.md       # Version history and changes
└── README.md          # This file
```

## Installation & Usage

### Prerequisites
- Node.js (for Electron)
- Python 3 (for backend, if building from source)

### Running from Source
```sh
npm install
npm start
```

### Building the App
```sh
npm run build
```
- The packaged app will be in the `out/` directory as a `.dmg` (macOS) or other installer.

### Installing the App
- Open the `.dmg` file in `out/`, drag the app to Applications, and open it from there.

## Documentation
- [Troubleshooting Guide](TROUBLESHOOTING.md)
- [Changelog](CHANGELOG.md)
- [Project State](project_state.json)
- Additional docs in the `docs/` folder

## License
[Your License Here]
