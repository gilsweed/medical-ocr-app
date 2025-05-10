const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const { spawn, execSync } = require('child_process');
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
        icon: path.join(__dirname, 'backend', 'assets', 'icon.png'),
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false
        }
    });

    // Set dock icon for macOS
    if (process.platform === 'darwin') {
        app.dock.setIcon(path.join(__dirname, 'backend', 'assets', 'icon.png'));
    }

    // Load the HTML file
    mainWindow.loadFile('index.html');

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

            // Determine correct backend path
            let basePath = __dirname;
            // Always use app.asar.unpacked if running from a packaged app
            if (basePath.includes('app.asar')) {
                basePath = basePath.replace('app.asar', 'app.asar.unpacked');
            }
            // For extra safety, if running from /Resources/app.asar, force the unpacked path
            if (basePath.endsWith('Resources')) {
                basePath = path.join(basePath, 'app.asar.unpacked');
            }
            const backendDir = path.join(basePath, 'backend');
            // Use the PyInstaller-built executable
            const execPath = path.join(backendDir, 'dist', process.platform === 'win32' ? 'supervisor.exe' : 'supervisor');

            console.log('Supervisor executable path:', execPath);
            console.log('Backend directory:', backendDir);

            // Start the supervisor executable
            pythonProcess = spawn(execPath, [], {
                stdio: 'pipe',
                cwd: backendDir,
                env: {
                    ...process.env,
                    PYTHONUNBUFFERED: '1',
                    PYTHONPATH: backendDir,
                    PYTHONWARNINGS: 'ignore',
                    PYTHONFAULTHANDLER: '1'
                }
            });

            // Handle process errors
            pythonProcess.on('error', (error) => {
                console.error('Failed to start supervisor executable:', error);
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
                console.log(`Supervisor stdout: ${data}`);
            });

            pythonProcess.stderr.on('data', (data) => {
                const logLine = data.toString();
                if (logLine.includes('ERROR') || 
                    logLine.includes('CRITICAL') ||
                    logLine.includes('FATAL')) {
                    console.error(`Supervisor stderr: ${data}`);
                    if (!responseSent) {
                        responseSent = true;
                        reject(new Error(`Supervisor backend error: ${data}`));
                    } else {
                        console.error('Error occurred after response was sent:', data);
                    }
                } else {
                    console.log(`Supervisor output: ${data}`);
                }
            });

            pythonProcess.on('close', (code) => {
                console.log(`Supervisor process exited with code ${code}`);
                if (code !== 0 && !responseSent) {
                    responseSent = true;
                    reject(new Error(`Supervisor backend exited with code ${code}`));
                } else if (code !== 0) {
                    console.error('Supervisor backend exited with non-zero code after response was sent:', code);
                }
                pythonProcess = null;
            });

            return pythonProcess;
        } catch (error) {
            console.error('Error starting supervisor backend:', error);
            if (!responseSent) {
                reject(error);
            } else {
                console.error('Error occurred after response was sent:', error);
            }
        }
    });
}

// This method will be called when Electron has finished initialization
app.whenReady().then(() => {
    // Create window immediately
    createWindow();

    // Start Python backend in parallel
    startPythonBackend().catch((error) => {
        console.error('Failed to start Python backend:', error);
        // Optionally, notify the renderer of backend failure via IPC
    });

    app.on('activate', () => {
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
    const result = await dialog.showOpenDialog(mainWindow, {
        properties: ['openFile'],
        filters: [
            { name: 'Images and PDFs', extensions: ['jpg', 'jpeg', 'png', 'pdf'] }
        ]
    });
    return result.filePaths[0];
});

// IPC handlers for OCR processing
ipcMain.handle('process-image', async (event, filePath) => {
    try {
        console.log('Processing image:', filePath);
        responseSent = false;

        const port = await getPythonPort();

        const response = await fetch(`http://localhost:${port}/api/process`, {
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
        console.error('Error occurred after response was sent:', error);
        return null;
    }
}); 