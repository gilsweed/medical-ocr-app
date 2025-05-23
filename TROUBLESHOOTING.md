# Troubleshooting Guide: OCR Scanner Electron App

This guide documents common issues, symptoms, and solutions for the OCR Scanner Electron App. For installation and usage, see [README.md](README.md). For version history, see [CHANGELOG.md](CHANGELOG.md).

---

## Quick Checklist
- [ ] Are you running backend and frontend from the correct directories?
- [ ] Is the backend running on the correct port (default: 8082)?
- [ ] Does `curl http://localhost:8082/health` return `{ "status": "ok" }`?
- [ ] Are you using the correct Node.js and Python versions?
- [ ] Have you installed all dependencies (`npm install`, `pip install -r requirements.txt`)?
- [ ] Are you editing the correct files (see [Project Structure](README.md#project-structure))?
- [ ] Is Tesseract OCR installed and available in your PATH?
- [ ] Are you using the correct OCR language settings (Hebrew/English)?

---

## Common Issues & Solutions

### 1. Electron App Shows "Status: Offline"
- **Root Cause:** Backend server is not running or not reachable at `http://localhost:8082`.
- **Solution:**
  1. Open a terminal and run:
     ```sh
     cd /Users/gilsweed/Desktop/Brurya/gil/backend
     python3 main.py
     ```
  2. In a second terminal, run:
     ```sh
     cd /Users/gilsweed/Desktop/Brurya/gil
     npm start
     ```
  3. Test backend with:
     ```sh
     curl http://localhost:8082/health
     ```
  4. If you see `{ "status": "ok" }`, the backend is running.

### 2. Electron App Shows Old Code or Won't Update
- **Root Cause:** Editing the wrong file or running from the wrong directory.
- **Solution:**
  - Confirm you are editing files in `/Users/gilsweed/Desktop/Brurya/gil`.
  - Add a debug line at the top of `electron.js`:
    ```js
    console.log('*** DEBUG: electron.js running from', __dirname);
    ```
  - Run `npm start` and check the terminal for the debug output.

### 3. Dependency or Module Errors
- **Root Cause:** Corrupted or missing `node_modules` or Python packages.
- **Solution:**
  1. Clean and reinstall dependencies:
     ```sh
     cd /Users/gilsweed/Desktop/Brurya/gil
     rm -rf node_modules dist out build package-lock.json
     npm cache clean --force
     npm install --registry=https://registry.npmjs.org/
     npm install axios
     ```
  2. For Python:
     ```sh
     cd backend
     python3 -m venv venv
     source venv/bin/activate
     pip install -r requirements.txt
     ```

### 4. Backend Not Responding or Crashing
- **Root Cause:** Port conflict, missing dependencies, or code errors.
- **Solution:**
  - Check backend terminal for errors.
  - Ensure port 8082 is free or change the port in both backend and Electron.
  - Reinstall Python dependencies.
  - Ensure Tesseract OCR is installed and working.

### 5. UI Not Centered or Not Modern
- **Root Cause:** Outdated or missing CSS.
- **Solution:**
  - Update `index.css` with the latest modern, centered styles (see [README.md](README.md#installation--usage)).

### 6. OCR Output is Poor or Empty
- **Root Cause:** Low-quality scan, wrong language, or OCR engine issue.
- **Solution:**
  - Ensure the document is high-quality and clearly scanned.
  - Check that the correct OCR language (Hebrew/English) is selected.
  - If using pytesseract, ensure the correct language data is installed.
  - If the app shows a warning about OCR quality, use the 'Open File' button to manually review the file.
  - Consider trying a different OCR engine if results are consistently poor.

### 7. 'Open File' Button Does Not Work
- **Root Cause:** File path is invalid or Electron shell integration is broken.
- **Solution:**
  - Ensure the file exists at the given path.
  - Check for errors in the Electron main/renderer process.
  - Update Electron to the latest version if needed.

---

## Best Practices
- Always run backend and frontend commands from their correct directories.
- Fully clean out `node_modules` and build artifacts when troubleshooting persistent issues.
- Ensure you are editing the correct files and that your changes are being used.
- Add IPC and backend status check logic to the Electron main process if the frontend needs to know backend status.
- Use debug lines to confirm which files are being executed.
- Use the modular OCR backend to allow easy switching of OCR engines in the future.
- Use the 'Open File' button for manual review if OCR output is suspicious.

---

## More Resources
- [README.md](README.md): Project overview, install/build/run instructions
- [CHANGELOG.md](CHANGELOG.md): Version history
- [project_state.json](project_state.json): Architecture, version history, known issues
- [docs/DEVELOPMENT_PLAN.md](docs/DEVELOPMENT_PLAN.md): Roadmap and feature map
- [docs/api.md](docs/api.md): API documentation
- [docs/development.md](docs/development.md): Development workflow and best practices
- [docs/project_history.md](docs/project_history.md): Project history and technical improvements

---

## How to Confirm You Are Editing the Correct electron.js File

1. Open electron.js in your project folder:
   ```sh
   nano /Users/gilsweed/Desktop/Brurya/gil/electron.js
   ```
2. At the very top, add this line:
   ```js
   console.log('*** DEBUG: electron.js running from', __dirname);
   ```
3. Save and exit nano (Ctrl + O, Enter, then Ctrl + X).
4. Start your app:
   ```sh
   npm start
   ```
5. Look for this line in your terminal:
   ```
   *** DEBUG: electron.js running from /Users/gilsweed/Desktop/Brurya/gil
   ```
6. If you see it, you are editing the correct file. If not, check your folder and try again.

---

**This file is for your future self or any assistant helping you with this project.**

## Status: Offline Troubleshooting

**Symptom:** Electron app shows "Status: Offline"

**Root Cause:** The backend server is not running or not reachable at `http://localhost:8080`.

**Correct Solution:**
1. Open a terminal and run:
   ```sh
   cd /Users/gilsweed/Desktop/Brurya/gil/backend
   python3 main.py
   ```
   (Leave this terminal open and running)
2. In a second terminal, run:
   ```sh
   cd /Users/gilsweed/Desktop/Brurya/gil
   npm start
   ```

**Do NOT:**
- Use `flask run` or set `FLASK_APP`
- Run from your home directory (`~`)
- Run backend in the background or as part of a script
- Close the backend terminal

**Common Mistakes:**
- Running backend from the home directory (`~`)
- Using `flask run` or `FLASK_APP` (not compatible with this project)
- Running backend in the background or as part of a script (causes SIGTERM)
- Closing the terminal where the backend is running

**If you still see "Offline":**
- Check the backend terminal for errors
- Make sure you see `* Running on http://127.0.0.1:8080`
- Copy any error messages and seek help 

To open your `index.html` file in nano, run this command in your terminal:

```sh
nano /Users/gilsweed/Desktop/Brurya/gil/index.html
```

- This will open the file for editing.
- You can then make changes, save with `Ctrl + O` (then Enter), and exit with `Ctrl + X`.

Let me know when it's open or if you need help with the next step! 

body {
  background: #cccccc !important;
  color: #222;
} 

---

## ABBYY FineReader Engine Licensing & SDK Integration

This section documents troubleshooting steps and best practices for integrating ABBYY FineReader Engine 12 for Mac ARM64, with a focus on licensing and SDK activation issues.

### Common Licensing Issues
- **Error:** `ABBYY FineReader Engine is not licensed.`
  - The SDK cannot find or validate the license file. This is usually due to an incorrect license file, wrong file location, or a license not valid for your platform (Mac ARM64).
- **Error:** `Serial number is not valid` or `This serial number is already activated`
  - The serial number is not valid for this SDK/platform, or has already been activated on another machine.

### Troubleshooting Steps
1. **Check License File Location**
   - License files must be in:
     `/Users/<your-username>/Library/Application Support/ABBYY/SDK/12/Licenses/`
   - Typical files: `SWATxxxxxxxxxxxxxxxxxxxx.ABBYY.LocalLicense`, `ABBYY.License`, `.profile`, `.log`
2. **Set Permissions**
   - Ensure the license directory and files are readable:
     ```sh
     chmod -R 777 "/Users/<your-username>/Library/Application Support/ABBYY/SDK/12"
     ```
3. **Set Environment Variables**
   - Some builds require:
     ```sh
     export ABBYY_LICENSE_PATH="/Users/<your-username>/Library/Application Support/ABBYY/SDK/12/Licenses"
     export DYLD_FRAMEWORK_PATH="/path/to/FREngine.framework/parent"
     ```
   - You can also run the sample as:
     ```sh
     ABBYY_LICENSE_PATH="..." DYLD_FRAMEWORK_PATH="..." ./CommandLineInterface ...
     ```
4. **Framework Location**
   - Ensure `FREngine.framework` is in `/Library/Frameworks/` or symlinked there.
5. **Check License File Name**
   - Try renaming your license file to `ABBYY.License` if not recognized.
6. **Review Log Files**
   - Check `ProductProtection_*.log` in the license directory for clues.
7. **Try Running as Root**
   - For testing only:
     ```sh
     sudo ABBYY_LICENSE_PATH="..." DYLD_FRAMEWORK_PATH="..." ./CommandLineInterface ...
     ```
8. **Reboot**
   - Sometimes required after activation.
9. **Check Platform Compatibility**
   - Confirm with ABBYY that your license is for **FineReader Engine 12**, **Mac**, and **ARM64** (Apple Silicon/M2).
10. **Contact ABBYY Support**
    - If all else fails, provide your serial, platform, and error messages to ABBYY support. Ask for a license reset or a new license file for your platform.

### Best Practices
- Document all troubleshooting steps and ABBYY support correspondence in your project docs.
- Keep a copy of all license files and logs for support.
- Update this section with any new issues or solutions as they arise.

### See Also
- [README.md](README.md): Project overview and links to all documentation
- [CHANGELOG.md](CHANGELOG.md): Version history
- [docs/security.md](docs/security.md): Security and compliance
- [docs/development.md](docs/development.md): Development workflow

--- 