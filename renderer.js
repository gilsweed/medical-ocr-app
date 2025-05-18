const { ipcRenderer } = require('electron');

document.addEventListener('DOMContentLoaded', () => {
  const fileInput = document.getElementById('file-input');
  const uploadForm = document.getElementById('upload-form');
  const ocrResultDiv = document.getElementById('ocr-result');

  uploadForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    if (!fileInput.files.length) {
      ocrResultDiv.textContent = 'Please select a file.';
      return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);

    ocrResultDiv.textContent = 'Uploading and processing...';

    try {
      const response = await fetch('http://localhost:8082/api/ocr/pdf', {
        method: 'POST',
        body: formData
      });
      const data = await response.json();

      if (data.warning && data.warning.length > 0) {
        ocrResultDiv.textContent = 'Warning: ' + data.warning;
      } else if (data.success) {
        ocrResultDiv.textContent = 'File uploaded. Processing...';
      } else {
        ocrResultDiv.textContent = 'Error: ' + (data.error || 'Unknown error');
      }

      // Fetch the OCR result
      if (data.job_id) {
        let statusData;
        let tries = 0;
        do {
          const statusResp = await fetch(`http://localhost:8082/api/ocr/pdf/status/${data.job_id}`);
          statusData = await statusResp.json();
          if (statusData.success && statusData.status === 'done') {
            break;
          }
          await new Promise(res => setTimeout(res, 1000));
          tries++;
        } while (tries < 10 && (!statusData || statusData.status !== 'done'));

        if (statusData && statusData.success && statusData.status === 'done') {
          ocrResultDiv.textContent = statusData.text;
        } else {
          ocrResultDiv.textContent = 'OCR job status: ' + (statusData.status || 'Unknown');
        }
      }
    } catch (err) {
      ocrResultDiv.textContent = 'Error: ' + err.message;
    }
  });
});