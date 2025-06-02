const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const axios = require('axios');
const { dialog } = require('electron');

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    backgroundColor: '#222222',
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  mainWindow.loadFile('index.html');
}

ipcMain.handle('check-backend-status', async () => {
  try {
    const res = await axios.get('http://localhost:8082/health');
    if (res.status === 200) {
      return { status: 'Ready', color: '#4caf50' };
    }
    return { status: 'Offline', color: '#b71c1c' };
  } catch (e) {
    return { status: 'Offline', color: '#b71c1c' };
  }
});

// IPC handler for folder selection
ipcMain.handle('select-folder', async () => {
  const result = await dialog.showOpenDialog({
    properties: ['openDirectory']
  });
  if (result.canceled || !result.filePaths.length) return null;
  return result.filePaths[0];
});

// IPC handlers for OCR processing
ipcMain.handle('process-image', async (event, filePath) => {
    try {
        console.log('Processing image:', filePath);
        responseSent = false;

        const response = await fetch(`http://localhost:8082/api/process`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                file_path: filePath,
                engine: 'google'  // Specify Google Vision as the OCR engine
            }),
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

app.whenReady().then(() => {
  createWindow();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit();
});
