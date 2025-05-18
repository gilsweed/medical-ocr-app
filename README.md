# OCR Scanner Electron App

A modern, cross-platform desktop application for OCR scanning and text processing, built with Electron (Node.js) and Python (Flask). Designed for robust, local, and privacy-compliant OCR workflows, especially for Hebrew and mixed-language documents. **Security and privacy are first-class features.**

---

## Project Overview
OCR Scanner Electron App is a user-friendly desktop tool for extracting text from images and PDFs using OCR technology. It features a modern UI, robust error handling, and is packaged for easy installation on macOS. The app is actively maintained and open to contributions. **Security and privacy best practices are built in, supporting both local and secure cloud workflows.**

---

## Features
- Local OCR processing for images and PDFs (Hebrew/English)
- Drag-and-drop and file picker UI
- Progress bar and result/error display
- Modern, user-friendly interface
- Robust error handling and feedback
- Packaged for macOS (Dock/Launchpad ready)
- Status indicator: Shows 'Ready' when the backend is running and reachable
- Modular architecture: Electron frontend, Python backend
- File-based workflow for privacy and compliance
- Easy to swap OCR engine (pytesseract, ABBYY, etc.)
- Manual review: Open files from within the app if OCR fails or is suspicious
- **Security & privacy by design:** Local and cloud workflows, encryption, and compliance

---

## Project Structure
```
.
├── backend/           # Python backend (Flask server, OCR logic)
├── docs/              # Documentation (API, development, history, plans, security)
├── index.html         # Main UI file
├── electron.js        # Electron main process
├── package.json       # Node.js project config
├── project_state.json # Project state, version history, architecture
├── TROUBLESHOOTING.md # Troubleshooting guide
├── CHANGELOG.md       # Version history and changes
└── README.md          # This file
```

---

## Installation & Usage

### Prerequisites
- Node.js (for Electron frontend)
- Python 3 (for backend)
- Tesseract OCR (for local OCR)

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

---

## Cloud Storage Setup for PDF/TIFF OCR

To enable PDF and TIFF OCR with Google Cloud Vision API, you must create a private Google Cloud Storage bucket with the following recommended settings:
- **Location:** Multi-region (e.g., `us`)
- **Storage class:** Standard
- **Public access prevention:** Enabled
- **Access control:** Uniform
- **Object versioning:** Disabled
- **Retention:** Disabled
- **Encryption:** Google-managed encryption key (default)

This bucket will be used to upload PDFs/TIFFs for async OCR processing. See the Security & Privacy documentation for more details.

---

## Automated PDF/TIFF OCR Workflow (Google Cloud Vision)

This app supports fully automated, privacy-compliant OCR for PDFs and TIFFs using Google Cloud Vision API. The workflow:
- Uploads the file to a secure, private Cloud Storage bucket
- Runs async OCR and waits for completion
- Downloads the result JSON(s) and parses the extracted text
- Saves the text locally (never in the cloud)
- Deletes both the original file and result JSON(s) from the bucket
- Notifies the user of any error at each step (upload, OCR, download, parse, delete)

**All steps are automated and designed for GDPR/HIPAA compliance.**

See the Security & Privacy documentation for more details.

---

## Documentation
- [Security & Privacy](docs/security.md): Security best practices, privacy, and compliance
- [Troubleshooting Guide](TROUBLESHOOTING.md): Common issues, solutions, and best practices
- [Changelog](CHANGELOG.md): Version history and changes
- [Project State](project_state.json): Architecture, version history, and known issues
- [Development Plan](docs/DEVELOPMENT_PLAN.md): Roadmap, feature map, and progress
- [API Documentation](docs/api.md): REST API endpoints and usage
- [Development Guide](docs/development.md): Environment setup, workflow, and best practices
- [Project History](docs/project_history.md): Major changes and technical improvements

---

## Current Development & Future Plans
- **Current:**
  - Modularize OCR backend to allow easy swapping of OCR engines (pytesseract, ABBYY, etc.)
  - Implement OCR quality check: If output is below standard, show warning and allow manual file review
  - Add 'Open File' button in UI for manual inspection
  - Improve batch processing and error handling
- **Planned:**
  - Integrate advanced OCR engines as they become available
  - Enhance UI for larger file sets and better accessibility
  - Add export options (Word, Excel, etc.)
  - Implement user settings and preferences
  - Expand documentation and add more troubleshooting tips

---

## Contributing
Pull requests and issues are welcome! Please see the [Troubleshooting Guide](TROUBLESHOOTING.md) and [CHANGELOG.md](CHANGELOG.md) before submitting. For architecture and version history, see [project_state.json](project_state.json).

---

## Support
For help, see TROUBLESHOOTING.md or open an issue on GitHub.

---

## License
[Your License Here]
