# OCR Scanner Electron App – Development Plan & Progress

## Roadmap & Feature Map

### 1. File Input (Drag-and-Drop & Picker)
- **User Story:**
  - As a user, I want to select or drag-and-drop multiple files, folders, and subfolders (including PDFs, JPG, JPEG, TIFF, PNG, BMP, GIF, etc.) into the app, so I can process them all at once. If a file fails to load, I want to see a clear error message explaining what went wrong.
- **Input:**
  - Multiple files at once (batch selection)
  - Drag-and-drop of folders and subfolders (recursively find all supported files)
  - Supported file types: PDF, JPG, JPEG, TIFF, PNG, BMP, GIF, etc.
- **Output:**
  - The app lists all selected files (with full paths)
  - If a file fails to load, an error message is shown, explaining the issue
- **UI:**
  - Drag-and-drop area (accepts files and folders)
  - File picker button (allows multi-select)
  - List of selected files (with remove option)
  - Error display area
- **Backend:**
  - Not needed for this step
- **Error Handling:**
  - Only allow supported file types (PDF, JPG, JPEG, TIFF, PNG, BMP, GIF, etc.)
  - If a file is not supported, show an error:  "File [filename] is not a supported type. Supported types: PDF, JPG, JPEG, TIFF, PNG, BMP, GIF."
  - If a file cannot be read (corrupt, permission denied, etc.), show an error:  "File [filename] could not be loaded: [system error message]."
  - If a folder is empty or contains no supported files, show an error.

---

### 2. Process Button & Backend OCR
- **User Story:**
  - As a user, I want to click "Process" to send all selected files to the backend for OCR and get the extracted text.
- **Input:**
  - List of selected files
- **Output:**
  - Extracted text for each file, or error message
- **UI:**
  - "Process" button
  - Progress bar
  - Result display area
- **Backend:**
  - `/api/process` endpoint (accepts files, returns text)
- **Error Handling:**
  - Show errors for files that fail to process

---

### 3. Action Buttons (Copy, Export, Clear)
- **User Story:**
  - As a user, I want to copy, export, or clear the extracted text.
- **UI:**
  - "Copy", "Export", "Clear" buttons
- **Functionality:**
  - Copy to clipboard, save to file, clear result area

---

### 4. Advanced Features (Dicta, AI, Batch, Settings)
- **User Story:**
  - As a user, I want to analyze text with Dicta/AI, process batches, and configure settings.
- **UI:**
  - "Dicta", "AI Analyze", "Settings" buttons
- **Backend:**
  - Dicta/AI endpoints

---

## Progress Tracking

- [x] Status indicator (backend/IPC working)
- [ ] File input: multi-file, folder/subfolder drag-and-drop, error handling (**current step**)
- [ ] Process button & backend OCR
- [ ] Action buttons (copy, export, clear)
- [ ] Advanced features (Dicta, AI, batch, settings)

---

## Notes
- Input must support drag-and-drop of folders and subfolders, recursively finding all supported files (PDF, JPG, JPEG, TIFF, PNG, BMP, GIF, etc.)
- This file will be updated as we move forward. 