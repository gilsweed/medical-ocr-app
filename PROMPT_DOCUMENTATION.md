Persistent Prompts & Instructions (Summary)
General Context
This is an OCR Scanner Electron App project with a Python (Flask) backend and Electron (Node.js) frontend.
The backend provides OCR and health endpoints; the frontend provides a modern UI and status monitoring.
All documentation and versioning is managed in README.md, CHANGELOG.md, TROUBLESHOOTING.md, and docs/.
Startup & Workflow
Always use start_all.sh to launch both backend and frontend together for reliability.
The backend must be running for the Electron app to show “Status: Ready.”
If you launch from the Dock/Launchpad, you must start the backend manually.
The “Reconnect” button in the UI allows manual retry if the backend was offline.
Status & Polling
Use robust polling in the frontend: only show “Offline” after several failed health checks.
The status should remain “Ready” as long as the backend is running and healthy.
If the backend is restarted, the status will return to “Ready” automatically.
Versioning & Restoration
Use git for version control.
After each milestone or version, commit all changes and tag the release (e.g., git tag v1.3.3).
The CHANGELOG documents what changed, but only git allows you to restore code to a previous version.
To restore a version: git checkout vX.Y.Z
Documentation & Context Restoration
Keep all persistent prompts and instructions in PROMPT_DOCUMENTATION.md.
To update: edit the file and commit the change to git.
Editing & File Management
When editing files in nano, always delete all text and paste the new content provided.
Confirm you are editing the correct file in the correct directory.
After editing, always save and restart the Electron app to see changes.
Troubleshooting
If the app shows “Status: Offline,” check that the backend is running and accessible at http://localhost:8082/health.
Use curl http://localhost:8082/health to test backend health.
If the Reconnect button does not work, ensure the backend is running and the frontend code is up to date.
Use Developer Tools (Cmd+Option+I) to check for frontend errors.
Professional Practices
Document all major changes in CHANGELOG.md.
Tag and commit each release in git.
Keep your documentation up to date as the project evolves.
For production, consider packaging the backend to auto-start with Electron, but only after development is stable.
