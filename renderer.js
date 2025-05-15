const { ipcRenderer } = require('electron');

let failCount = 0;
const MAX_FAILS = 3;
const statusText = document.getElementById('statusText');
const reconnectBtn = document.getElementById('reconnectBtn');

async function updateStatus(manual = false) {
  try {
    const result = await ipcRenderer.invoke('check-backend-status');
    if (result.status === 'Ready') {
      failCount = 0;
      statusText.textContent = result.status;
      statusText.style.color = result.color;
      reconnectBtn.style.display = 'none';
    } else {
      failCount++;
      if (failCount >= MAX_FAILS || manual) {
        statusText.textContent = 'Offline';
        statusText.style.color = '#b71c1c';
        reconnectBtn.style.display = '';
      }
    }
  } catch (e) {
    failCount++;
    if (failCount >= MAX_FAILS || manual) {
      statusText.textContent = 'Offline';
      statusText.style.color = '#b71c1c';
      reconnectBtn.style.display = '';
    }
  }
}

reconnectBtn.onclick = () => {
  updateStatus(true);
};

updateStatus();
setInterval(updateStatus, 5000); // Check every 5 seconds

// --- File/Folder Selection Logic ---

const selectFilesBtn = document.getElementById('selectFilesBtn');
const selectFolderBtn = document.getElementById('selectFolderBtn');
const fileInputFiles = document.getElementById('fileInputFiles');
const fileInputFolder = document.getElementById('fileInputFolder');
const fileList = document.getElementById('fileList');
const errorDiv = document.getElementById('error');
let selectedFiles = [];
const SUPPORTED_EXT = ['.pdf', '.jpg', '.jpeg', '.tiff', '.tif', '.png', '.bmp', '.gif'];

function showError(msg) {
  errorDiv.textContent = msg;
  errorDiv.style.display = 'block';
}
function clearError() {
  errorDiv.textContent = '';
  errorDiv.style.display = 'none';
}
function updateFileList() {
  fileList.innerHTML = '';
  selectedFiles.forEach((file, idx) => {
    const li = document.createElement('li');
    li.textContent = file;
    const btn = document.createElement('button');
    btn.textContent = 'Remove';
    btn.className = 'remove-btn';
    btn.onclick = () => {
      selectedFiles.splice(idx, 1);
      updateFileList();
    };
    li.appendChild(btn);
    fileList.appendChild(li);
  });
}
function isSupported(filePath) {
  return SUPPORTED_EXT.includes(
    filePath.slice(filePath.lastIndexOf('.')).toLowerCase()
  );
}
function addFiles(files) {
  let errors = [];
  for (const file of files) {
    if (!isSupported(file)) {
      errors.push(
        `File ${file} is not a supported type. Supported types: ${SUPPORTED_EXT.join(', ').toUpperCase()}`
      );
      continue;
    }
    if (!selectedFiles.includes(file)) {
      selectedFiles.push(file);
    }
  }
  updateFileList();
  if (errors.length) showError(errors.join('\n'));
  else clearError();
}

// File selection
selectFilesBtn.onclick = () => {
  fileInputFiles.value = '';
  fileInputFiles.click();
};
fileInputFiles.addEventListener('change', (e) => {
  clearError();
  let files = [];
  for (const file of e.target.files) {
    files.push(file.path);
  }
  addFiles(files);
});

// Folder selection
selectFolderBtn.onclick = () => {
  fileInputFolder.value = '';
  fileInputFolder.click();
};
fileInputFolder.addEventListener('change', (e) => {
  clearError();
  let files = [];
  for (const file of e.target.files) {
    files.push(file.path);
  }
  addFiles(files);
});
