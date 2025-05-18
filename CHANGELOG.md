# Changelog

All notable changes to this project will be documented in this file.

## [1.5.0] - 2025-05-16
### Added
- Fully automated PDF/TIFF async OCR workflow with Google Cloud Vision API
- Upload, OCR, download, parse, and deletion steps are all automated
- Error notifications for each step (upload, OCR, download, parse, delete)
- Extracted text is only saved locally; all cloud files are deleted after use
- Documentation updated to reflect new workflow and privacy guarantees

## [1.4.0] - 2025-05-16
### Added
- Modularized OCR backend to allow easy swapping of OCR engines (pytesseract, ABBYY, etc.)
- Implemented OCR quality check: If output is below standard, show warning and allow manual file review
- Added 'Open File' button in UI for manual inspection of files with OCR warnings
- Improved batch processing and error handling
- Updated documentation to reflect new features and workflow

### Planned
- Integrate advanced OCR engines as they become available
- Enhance UI for larger file sets and better accessibility
- Add export options (Word, Excel, etc.)
- Implement user settings and preferences
- Expand documentation and add more troubleshooting tips

## [1.3.3] - 2025-05-15
### Permanent 'Status: Ready' Fix
- Added unified startup script (`start_all.sh`) to ensure backend is always running before Electron app starts
- Status indicator now remains 'Ready' as long as backend is running
- Reconnect button and robust polling logic confirmed
- Documentation updated to reflect new workflow and best practices

## [1.3.2] - 2025-05-15
### Added
- Unified startup script (`start_all.sh`) for robust, one-command launch of backend and frontend
- Documentation updated to reflect new workflow and best practices

## [1.3.1] - 2025-05-15
### Stable version before robust polling and reconnect button
- Backend and frontend reliably communicate
- Status indicator shows 'Ready' when backend is running
- UI and documentation professionalized
- All previous features and bugfixes included

## [1.3.0] - 2025-05-13
### Added
- Electron app now reliably shows 'Status: Ready' when the backend is running and reachable (confirmed working in current version)
- Documentation updated and professionalized (README, TROUBLESHOOTING, CHANGELOG)
- Clear install, run, and troubleshooting instructions for both backend and frontend

## [1.2.0] - 2024-05-10
### Added
- Changed app and window background to grey for a modern look
- Ensured PDF files can be selected in the file picker
- Fixed port Promise bug in process-image handler
- Improved error handling and feedback in the UI
- Documented Dock/Desktop packaging mission in project pipeline
- Committed all changes to git

## [1.1.0] - 2024-05-09
### Added
- Merged legacy and new codebases
- Fixed backend config and process management
- Reinstalled and cleaned dependencies
- Modernized UI with drag-and-drop, action buttons, and feedback
- Packaged app as .app bundle
- Moved app to /Applications for Launchpad/Dock integration
- Backed up and committed all changes to git

## [1.0.2] - 2024-05-09
### Changed
- Removed Gunicorn and its configuration
- Switched to Flask's development server
- Simplified process management
- Improved server stability
- Enhanced cleanup procedures
- Updated port management

## [1.0.1] - 2024-03-19
### Improved
- Improved ProcessManager with multiprocessing
- Enhanced port management with wider range
- Added better process cleanup
- Improved error handling and logging
- Updated component status tracking
- Added detailed component descriptions

## [1.0.0] - 2024-03-19
### Initial Release
- Implemented ProcessManager class
- Created gunicorn.conf.py
- Added proper signal handling
- Implemented cleanup procedures
- Created start.sh script
- Added process synchronization

---

## Documentation Links
- [Troubleshooting Guide](TROUBLESHOOTING.md)
- [Project State & Architecture](project_state.json)
- [Development Plan](docs/DEVELOPMENT_PLAN.md)
- [API Documentation](docs/api.md)
- [Development Guide](docs/development.md)
- [Project History](docs/project_history.md)

For troubleshooting and upgrade instructions, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
For architecture and project state, see [project_state.json](project_state.json). 