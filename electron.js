const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const axios = require('axios');

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    backgroundColor: '#222222',
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
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

app.whenReady().then(() => {
  createWindow();

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit();
});
