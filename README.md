# OCR Scanner Electron App

A modern, cross-platform desktop application for OCR scanning and text processing, built with Electron (Node.js) and Python (Flask).

## Project Overview
OCR Scanner Electron App is a user-friendly desktop tool for extracting text from images and PDFs using OCR technology. It features a modern UI, robust error handling, and is packaged for easy installation on macOS. The app is actively maintained and open to contributions.

## Features
- OCR processing for images and PDFs
- Drag-and-drop and file picker UI
- Progress bar and result/error display
- Modern, user-friendly interface
- Robust error handling and feedback
- Packaged for macOS (Dock/Launchpad ready)
- **Status indicator:** Shows 'Ready' when the backend is running and reachable

## Architecture
- **Electron Main Process:** Handles window management, IPC, and backend status checks
- **Renderer Process:** User interface (index.html, JS, CSS)
- **Python Backend:** Flask server for OCR and PDF/image processing

## Project Structure
```
.
├── backend/           # Python backend (Flask server, OCR logic)
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
- Node.js (for Electron frontend)
- Python 3 (for backend)

### Backend Setup
```sh
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py
```
- The backend will run on http://127.0.0.1:8082

### Frontend (Electron) Setup
```sh
cd /Users/gilsweed/Desktop/Brurya/gil
npm install --registry=https://registry.npmjs.org/
npm start
```
- The Electron app will open and connect to the backend.
- The status will show **'Ready'** when the backend is running and reachable.

### Building the App
```sh
npm run build
```
- The packaged app will be in the `out/` directory as a `.dmg` (macOS) or other installer.

## Documentation
- [Troubleshooting Guide](TROUBLESHOOTING.md)
- [Changelog](CHANGELOG.md)
- [Project State](project_state.json)
- Additional docs in the `docs/` folder (if present)

## Contributing
Pull requests and issues are welcome! Please see the [Troubleshooting Guide](TROUBLESHOOTING.md) and [CHANGELOG.md](CHANGELOG.md) before submitting. For architecture and version history, see [project_state.json](project_state.json).

## Support
For help, see TROUBLESHOOTING.md or open an issue on GitHub.

## License
[Your License Here]
