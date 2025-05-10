const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld(
  'electron',
  {
    processImage: (filePath) => ipcRenderer.invoke('process-image', filePath),
    selectFile: () => ipcRenderer.invoke('select-file')
  }
); 