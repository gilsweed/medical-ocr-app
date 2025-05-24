const fileInput = document.getElementById('fileInput');
const processButton = document.getElementById('processButton');
const resultArea = document.getElementById('resultArea');
const engineSelect = document.getElementById('engineSelect');

// Ensure ABBYY is the default if nothing is selected
if (engineSelect && !engineSelect.value) {
    engineSelect.value = "abbyy";
}

// Always clear result area when file input is clicked or changed
fileInput.addEventListener('click', () => {
    resultArea.textContent = '';
});
fileInput.addEventListener('change', () => {
    resultArea.textContent = '';
});
engineSelect.addEventListener('change', () => {
    resultArea.textContent = '';
});

processButton.addEventListener('click', async () => {
    const files = fileInput.files;
    if (!files.length) {
        resultArea.textContent = 'Please select a file.';
        return;
    }
    const file = files[0];
    let engine = engineSelect.value || "abbyy"; // Default to ABBYY

    // Send file path and engine to backend
    const response = await fetch('http://localhost:8082/api/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            file_path: file.path,
            engine: engine
        })
    });

    const data = await response.json();
    if (data.success) {
        resultArea.textContent = data.text;
    } else {
        resultArea.textContent = `Error: ${data.error}`;
    }
});
