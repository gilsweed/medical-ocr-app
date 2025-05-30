# OCR Scanner Electron App

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/gilsweed/medical-ocr-app/actions) [![License](https://img.shields.io/badge/license-ISC-blue)](LICENSE) [![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey)](#)

A modern, cross-platform desktop application for OCR scanning and text processing, built with Electron (Node.js) and Python (Flask). Designed for robust, local, and privacy-compliant OCR workflows, especially for Hebrew and mixed-language documents. **Security and privacy are first-class features.**

---

## Quick Start

1. **Clone the repository:**
   ```sh
   git clone <repo-url>
   cd gil
   ```
2. **Install dependencies:**
   - Backend: `cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt`
   - Frontend: `cd .. && npm install --registry=https://registry.npmjs.org/`
3. **Run the backend:**
   ```sh
   cd backend
   source venv/bin/activate
   python3 main.py
   ```
4. **Run the frontend:**
   ```sh
   cd ..
   npm start
   ```
5. **Build the app:**
   ```sh
   npm run build
   ```

---

## Project Overview

OCR Scanner Electron App is a user-friendly desktop tool for extracting text from images and PDFs using OCR technology. It features a modern, Mac-like UI, robust error handling, and is packaged for easy installation on macOS, Windows, and Linux. The app is actively maintained and open to contributions. **Security and privacy best practices are built in, supporting both local and secure cloud workflows.**

---

## Features

- Local OCR processing for images and PDFs (Hebrew/English, mixed-language)
- **Toggleable OCR engine:** ABBYY CLI (default) or Google Vision API
- Drag-and-drop and file picker UI
- Progress bar and result/error display
- Modern, RTL-friendly, accessible interface
- Robust error handling and feedback
- Status indicator: Shows 'Ready' when the backend is running and reachable
- Modular architecture: Electron frontend, Python backend
- File-based workflow for privacy and compliance
- Manual review: Open files from within the app if OCR fails or is suspicious
- **Security & privacy by design:** Local and cloud workflows, encryption, and compliance
- Automation scripts for easy startup and port management

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
├── start_all.sh       # Unified startup script (backend + frontend)
└── README.md          # This file
```

---

## Documentation Index
- [Project Overview](#project-overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation & Usage](#installation--usage)
- [Quick Start](#quick-start)
- [Automation Scripts](#automation-scripts)
- [OCR Engine Selection](#ocr-engine-selection)
- [Cloud Storage & Privacy](#cloud-storage-setup-for-pdftiff-ocr)
- [Automated PDF/TIFF OCR Workflow](#automated-pdftiff-ocr-workflow-google-cloud-vision)
- [Documentation](#documentation)
- [Development & Roadmap](#current-development--future-plans)
- [Contributing](#contributing)
- [Support](#support)
- [License](#license)

---

## Getting Help

- See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.
- For architecture and version history, see [project_state.json](project_state.json).
- For the full roadmap, see [docs/DEVELOPMENT_PLAN.md](docs/DEVELOPMENT_PLAN.md).
- For API usage, see [docs/api.md](docs/api.md).
- For security and compliance, see [docs/security.md](docs/security.md).
- For development workflow, see [docs/development.md](docs/development.md).
- For project history, see [docs/project_history.md](docs/project_history.md).
- If you need further help, open an issue on GitHub or contact the maintainer.

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
  - Modularize OCR backend to allow easy swapping of OCR engines (ABBYY, Google Vision, etc.)
  - Modernize UI/UX for accessibility and RTL support
  - Implement robust error handling and automation scripts
  - Improve batch processing and error handling
- **Planned:**
  - Batch processing (multi-file/folder)
  - Summarization (Ollama/local GPT)
  - Feedback learning
  - Export options (Word, PDF, etc.)
  - User settings/preferences
  - Secure history/logs
  - Full encryption/compliance features
  - Automated tests

---

## Detailed Workflow & Roadmap

This app is designed for secure, efficient batch OCR and AI-powered summarization of patient documents. The workflow and features are based on an in-depth, step-by-step planning process. Key highlights:

- Patient ID auto-detection from folder name (manual override always possible)
- Batch file/folder input, unlimited files per batch
- Dynamic progress bar (minimal, disappears after processing)
- OCR with numeric confidence scoring; low-confidence files flagged and sorted to top
- Main review panel: left = all low-confidence file previews (scrollable), right = editable summaries (RTL, Hebrew, independently scrollable, can be hidden)
- Floating, resizable AI dialog: upper chat (color-coded), lower prompt editor, both scrollable; supports prompt templates and knowledge file references
- All summary edits are learned by the AI for future improvement (background, automatic)
- Export: all summaries and logs in a single file (.txt default, user can change), with option to include originals as zip; output folder always named with patient ID and date
- All data encrypted (macOS Keychain/Touch ID); retention policy and multi-user support planned

For the full, detailed roadmap and feature breakdown, see [docs/DEVELOPMENT_PLAN.md](docs/DEVELOPMENT_PLAN.md).

---

## Contributing

Pull requests and issues are welcome! Please see the [Troubleshooting Guide](TROUBLESHOOTING.md) and [CHANGELOG.md](CHANGELOG.md) before submitting. For architecture and version history, see [project_state.json](project_state.json).

---

## Support

For help, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md) or open an issue on GitHub.

---

## License

[ISC](LICENSE)
