# Changelog

All notable changes to this project will be documented in this file.

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