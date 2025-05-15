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

### 5. UI Not Centered or Not Modern
- **Root Cause:** Outdated or missing CSS.
- **Solution:**
  - Update `index.css` with the latest modern, centered styles (see [README.md](README.md#installation--usage)).

---

## Best Practices
- Always run backend and frontend commands from their correct directories.
- Fully clean out `node_modules` and build artifacts when troubleshooting persistent issues.
- Ensure you are editing the correct files and that your changes are being used.
- Add IPC and backend status check logic to the Electron main process if the frontend needs to know backend status.
- Use debug lines to confirm which files are being executed.

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