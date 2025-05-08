const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const isDev = process.env.NODE_ENV === 'development';

class AppManager {
    constructor() {
        this.mainWindow = null;
        this.pythonProcess = null;
        this.pythonPath = isDev ? 'python' : path.join(process.resourcesPath, 'python');
    }

    createWindow() {
        this.mainWindow = new BrowserWindow({
            width: 1200,
            height: 800,
            webPreferences: {
                nodeIntegration: true,
                contextIsolation: false
            }
        });

        // Load the index.html file
        this.mainWindow.loadFile(path.join(__dirname, '../renderer/index.html'));

        // Open DevTools in development
        if (isDev) {
            this.mainWindow.webContents.openDevTools();
        }
    }

    startPythonBackend() {
        const pythonScript = path.join(__dirname, '../backend/server.py');
        
        this.pythonProcess = spawn(this.pythonPath, [pythonScript]);

        this.pythonProcess.stdout.on('data', (data) => {
            console.log(`Python stdout: ${data}`);
        });

        this.pythonProcess.stderr.on('data', (data) => {
            console.error(`Python stderr: ${data}`);
        });

        this.pythonProcess.on('close', (code) => {
            console.log(`Python process exited with code ${code}`);
        });
    }

    setupIPC() {
        // File selection
        ipcMain.handle('select-files', async () => {
            const result = await dialog.showOpenDialog({
                properties: ['openFile', 'multiSelections'],
                filters: [
                    { name: 'Documents', extensions: ['pdf', 'jpg', 'jpeg', 'tiff', 'tif', 'png'] }
                ]
            });
            return result.filePaths;
        });

        // Process files
        ipcMain.handle('process-files', async (event, { files, prompt, language }) => {
            // Implementation will be added
            return new Promise((resolve, reject) => {
                // TODO: Implement file processing
            });
        });

        // Save prompt
        ipcMain.handle('save-prompt', async (event, { name, prompt }) => {
            // Implementation will be added
        });

        // Load prompts
        ipcMain.handle('load-prompts', async () => {
            // Implementation will be added
        });
    }

    init() {
        app.whenReady().then(() => {
            this.createWindow();
            this.startPythonBackend();
            this.setupIPC();

            app.on('activate', () => {
                if (BrowserWindow.getAllWindows().length === 0) {
                    this.createWindow();
                }
            });
        });

        app.on('window-all-closed', () => {
            if (process.platform !== 'darwin') {
                app.quit();
            }
        });

        app.on('before-quit', () => {
            if (this.pythonProcess) {
                this.pythonProcess.kill();
            }
        });
    }
}

const appManager = new AppManager();
appManager.init(); 