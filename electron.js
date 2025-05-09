const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const isDev = process.env.NODE_ENV === 'development';
const waitOn = require('wait-on');
const fs = require('fs');

let mainWindow;
let pythonProcess;
let responseSent = false;

// Configuration
function getPythonPort() {
    const portFile = path.join(__dirname, 'backend', 'port.txt');
    let attempts = 0;
    const maxAttempts = 10;
    const waitTime = 1000; // 1 second

    return new Promise((resolve, reject) => {
        function tryReadPort() {
            try {
                if (fs.existsSync(portFile)) {
                    const port = fs.readFileSync(portFile, 'utf8').trim();
                    console.log('Using port from port.txt:', port);
                    resolve(parseInt(port, 10));
                } else if (attempts < maxAttempts) {
                    attempts++;
                    console.log(`Port file not found, attempt ${attempts}/${maxAttempts}. Waiting ${waitTime}ms...`);
                    setTimeout(tryReadPort, waitTime);
                } else {
                    console.log('Port file not found after maximum attempts, using default port 8080');
                    resolve(8080);
                }
            } catch (error) {
                console.error('Error reading port file:', error);
                if (attempts < maxAttempts) {
                    attempts++;
                    setTimeout(tryReadPort, waitTime);
                } else {
                    console.log('Failed to read port file after maximum attempts, using default port 8080');
                    resolve(8080);
                }
            }
        }

        tryReadPort();
    });
}

const PYTHON_PORT = getPythonPort();

function createWindow() {
  // Create the browser window.
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, 'assets', 'icon.png'),
    title: 'OCR Scanner'
  });

  // Set dock icon
  if (process.platform === 'darwin') {
    app.dock.setIcon(path.join(__dirname, 'assets', 'icon.png'));
  }

  // Load the app
  if (isDev) {
    mainWindow.loadURL('http://localhost:3000');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, 'build/index.html'));
  }

  // Log any errors that occur during loading
  mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription) => {
    console.error('Failed to load:', errorCode, errorDescription);
  });
}

// Clean up Python process
function cleanupPythonProcess() {
    if (pythonProcess) {
        try {
            // Try graceful shutdown first
            pythonProcess.kill('SIGTERM');
            
            // Give it a moment to clean up
            setTimeout(() => {
                if (pythonProcess) {
                    // Force kill if still running
                    pythonProcess.kill('SIGKILL');
                    pythonProcess = null;
                }
            }, 1000);
        } catch (error) {
            console.error('Error cleaning up Python process:', error);
        }
    }
}

// Start Python backend
async function startPythonBackend() {
    return new Promise(async (resolve, reject) => {
        try {
            console.log('Starting Python backend...');
            responseSent = false;

            const pythonPath = path.join(__dirname, 'backend', 'venv', 'bin', 'python');
            const scriptPath = path.join(__dirname, 'backend', 'supervisor.py');
            const backendDir = path.join(__dirname, 'backend');

            console.log('Python path:', pythonPath);
            console.log('Script path:', scriptPath);
            console.log('Backend directory:', backendDir);

            // Clean up any existing Python processes
            cleanupPythonProcess();

            // Start the Python process with proper error handling
            pythonProcess = spawn(pythonPath, [scriptPath], {
                stdio: 'pipe',
                cwd: backendDir,
                env: {
                    ...process.env,
                    PYTHONUNBUFFERED: '1',  // Ensure Python output is not buffered
                    PYTHONPATH: backendDir,  // Add backend directory to Python path
                    PYTHONWARNINGS: 'ignore',  // Suppress Python warnings
                    PYTHONFAULTHANDLER: '1'  // Enable Python fault handler
                }
            });

            // Handle process errors
            pythonProcess.on('error', (error) => {
                console.error('Failed to start Python process:', error);
                if (!responseSent) {
                    responseSent = true;
                    reject(error);
                }
            });

            // Get the port from the file
            const port = await getPythonPort();

            // Wait for the Python backend to be ready
            waitOn({
                resources: [`http://localhost:${port}`],
                timeout: 30000,
                validateStatus: (status) => status === 200,
                delay: 2000,
                interval: 1000,
                verbose: true
            })
                .then(() => {
                    if (!responseSent) {
                        console.log('Python backend is ready');
                        responseSent = true;
                        resolve();
                    }
                })
                .catch((err) => {
                    if (!responseSent) {
                        console.error('Failed to start Python backend:', err);
                        responseSent = true;
                        reject(err);
                    }
                });

            pythonProcess.stdout.on('data', (data) => {
                console.log(`Python stdout: ${data}`);
            });

            pythonProcess.stderr.on('data', (data) => {
                // Only treat as error if it's not a startup log or info message
                const logLine = data.toString();
                if (logLine.includes('ERROR') || 
                    logLine.includes('CRITICAL') ||
                    logLine.includes('FATAL')) {
                    console.error(`Python stderr: ${data}`);
                    if (!responseSent) {
                        responseSent = true;
                        reject(new Error(`Python backend error: ${data}`));
                    } else {
                        console.error('Error occurred after response was sent:', data);
                    }
                } else {
                    console.log(`Python output: ${data}`);
                }
            });

            pythonProcess.on('close', (code) => {
                console.log(`Python process exited with code ${code}`);
                if (code !== 0 && !responseSent) {
                    responseSent = true;
                    reject(new Error(`Python backend exited with code ${code}`));
                } else if (code !== 0) {
                    console.error('Python backend exited with non-zero code after response was sent:', code);
                }
                pythonProcess = null;
            });

            return pythonProcess;
        } catch (error) {
            console.error('Error starting Python backend:', error);
            if (!responseSent) {
                reject(error);
            } else {
                console.error('Error occurred after response was sent:', error);
            }
        }
    });
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
app.whenReady().then(async () => {
  try {
    // Wait for webpack server to be ready
    await waitOn({
      resources: ['http://localhost:3000'],
      timeout: 60000,
      validateStatus: (status) => status === 200,
      delay: 1000, // Wait 1 second before starting to check
      interval: 500 // Check every 500ms
    });
    console.log('Webpack server is ready');

    // Start Python backend
    await startPythonBackend();
    
    // Create window
    createWindow();
  } catch (error) {
    console.error('Failed to start application:', error);
    app.quit();
  }

  app.on('activate', () => {
    // On macOS it's common to re-create a window in the app when the
    // dock icon is clicked and there are no other windows open.
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

// Handle app quit
app.on('window-all-closed', () => {
    cleanupPythonProcess();
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

// Clean up Python process on app quit
app.on('before-quit', () => {
    cleanupPythonProcess();
});

// Handle process termination
process.on('SIGTERM', () => {
    cleanupPythonProcess();
    app.quit();
});

process.on('SIGINT', () => {
    cleanupPythonProcess();
    app.quit();
});

// IPC handlers for communication between renderer and main process
ipcMain.handle('select-file', async () => {
  const { dialog } = require('electron');
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters: [
      { name: 'Images', extensions: ['jpg', 'jpeg', 'png'] },
      { name: 'PDFs', extensions: ['pdf'] }
    ]
  });
  return result.filePaths[0];
});

// IPC handlers for OCR processing
ipcMain.handle('process-image', async (event, filePath) => {
  try {
    console.log('Processing image:', filePath);
    responseSent = false;

    const response = await fetch(`http://localhost:${PYTHON_PORT}/api/process`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ filePath }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to process file');
    }

    const result = await response.json();
    responseSent = true;
    return result;
  } catch (error) {
    console.error('Error processing image:', error);
    if (!responseSent) {
      return {
        success: false,
        error: error.message || 'Failed to process file'
      };
    }
    // If response was already sent, just log the error
    console.error('Error occurred after response was sent:', error);
    return null;
  }
}); 