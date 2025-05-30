# OCR Scanner Electron App – Development Plan & Roadmap (Updated)

## Vision
A secure, user-friendly, cross-platform desktop app for batch OCR, review, and AI-powered summarization of patient documents, with robust privacy, multi-user, and export features.

---

## Roadmap & Feature Map (2024)

### 1. Patient ID Handling
- Auto-detect patient ID from folder name (with manual override).
- Manual edits always override auto-detection.
- Patient ID validated (red if invalid).
- Output files/folders named `[patient_id]_[date]` (format adjustable in settings).
- Future: Option to auto-detect patient ID from OCRed text (planned, not required for v1).

### 2. File Selection & Batch Input
- "Select Files/Folders" button (drag-and-drop planned for future).
- Recursively finds all supported files (PDF, JPG, TIFF, etc.).
- Unlimited files per batch.
- Dynamic, minimal progress bar (disappears after processing completes).

### 3. OCR Processing & Confidence Scoring
- Batch OCR using selected engine (ABBYY/Google Vision).
- Numeric confidence score for each file (engine metric or estimated).
- Confidence threshold adjustable in settings.
- Low-confidence files flagged in red, sorted to top.
- Hovering shows tooltip with cause of low confidence.

### 4. Review & Final Summary Panel
- Main window: two independently scrollable, resizable panels (left: file previews, right: summaries).
- All low-confidence files shown as full previews in a single scrollable left panel.
- Right panel: editable, RTL summary boxes (one per file), can be hidden/collapsed for focused review.
- "AI Assist" button for each summary opens a floating, resizable dialog.
- AI dialog: upper chat history (color-coded prompts), lower prompt editor, both scrollable independently.
- Save button stores chat/prompt and closes dialog.
- User can create/save prompt templates, select from dropdown (last used is default).
- User can upload/manage knowledge files (rules, guidelines) and reference them in prompts.
- AI dialog supports conversational interaction; user can reference knowledge files in chat.
- All manual summary edits are learned by the AI in the background for future improvement.

### 5. Export & Output Management
- Export all summaries as a single file (.txt default, user can change format; last used is default).
- Exported file includes all summaries, final summary, and a section listing all low-confidence files.
- Option to export original files with summaries as a zip.
- All exports go to a dedicated output folder (name includes patient ID and date).
- Export structure designed for easy sharing (Dropbox, Google Drive, etc.).
- Export content is user-friendly and order/structure is adjustable.
- Optionally, export includes all previous summaries for the patient (full history).

### 6. Security, Retention, and Multi-User
- All data stored encrypted (macOS Keychain/Touch ID, future: Windows Hello).
- Retention policy: auto-delete data after user-configurable number of days.
- Multi-user support planned: output folder structure and sharing designed for Dropbox/Google Drive.

### 7. Knowledge Files & AI Learning
- User can upload, view, edit, and manage knowledge files from the app menu.
- AI can access referenced files in prompts and chat.
- All summary edits and feedback are used to improve future AI output (continuous learning).

### 8. Future Enhancements
- Drag-and-drop file/folder input.
- Auto-detect patient ID from OCRed text.
- More export formats and batch export options.
- Advanced multi-user collaboration.
- Deeper AI learning/fine-tuning.

---

## Implementation Notes
- All UI/UX is Mac-like, modern, and accessible (RTL support for Hebrew).
- All panels are resizable; file list and summary panels can be collapsed/minimized.
- Floating AI dialog is always on top, adjustable, and supports full chat history.
- All features are designed for extensibility and future-proofing.

---

## Progress Tracking
- [x] Secure file input (single file)
- [x] OCR engine toggle (Google/ABBYY)
- [x] Modern UI/UX
- [x] Error handling and automation scripts
- [ ] Batch processing (multi-file/folder)
- [ ] Summarization (Ollama/local GPT)
- [ ] Feedback learning
- [ ] Export options (Word, PDF, etc.)
- [ ] User settings/preferences
- [ ] Secure history/logs
- [ ] Full encryption/compliance features
- [ ] Automated tests

---

## To-Do List (Key Future Features)
- [ ] Auto-detect patient ID from OCRed text
- [ ] Drag-and-drop file/folder input
- [ ] Advanced multi-user collaboration
- [ ] Deeper AI learning/fine-tuning

---

## Recent UI/UX and Feature Updates (2024)

### Unified Files Preview Panel
- Left panel is now "Files Preview" with a centered header.
- Shows all files (high-confidence first, then low-confidence) in a single scrollable list.
- High-confidence files: green border; low-confidence: red border.
- Each file preview supports multi-page files (scrollable area, page navigation controls).
- Panel is horizontally resizable.
- Note: Files can be ordered by date found in OCR text (not file creation date).

### Summary Box Improvements
- Summary box is centered in the right panel, with max width (now 900px) and fixed position.
- Expands vertically to use available space, always visually centered.
- Section label ("סיכום נוכחי של המטופל") is above the box, centered.

### AI Dialog & Action Bar
- "AI Assist" button now in the action bar above the summary box, next to "Save All Corrections" and "Export".
- Floating AI dialog is resizable, draggable, and can be minimized/closed.
- All text areas in the AI dialog are maximized for usability.

### ABBYY Advanced Region Mapping (Planned)
- Parse ABBYY OCR output to extract block/area coordinates and confidence.
- Map recognized text blocks to their locations on the scanned image.
- Track and highlight which areas/blocks contributed to the summary.
- UI: Overlay highlights on the scanned image preview; allow users to see which regions were used for summary.
- Backend: Maintain mapping between summary text and source blocks/areas.
- Benefit: Improves transparency, review, and trust in the summary process for users.
- Note: Requires extra parsing, mapping, and UI overlay work, but fully supported by ABBYY SDKs.

---

## Step-by-Step Roadmap

1. **Patient ID Handling**
   - Auto-detect from folder name
   - Manual override & validation
   - Output naming conventions

2. **File Selection & Batch Input**
   - Select files/folders (multi-file)
   - Recursive search for supported files
   - Progress bar for batch jobs

3. **OCR Processing & Confidence Scoring**
   - Batch OCR (ABBYY/Google Vision)
   - Confidence scoring & threshold
   - Flag low-confidence files

4. **Unified Files Preview Panel**
   - All files (high/low confidence) in one scrollable panel
   - Color-coded borders (green/red)
   - Multi-page file support (scrollable, page navigation)
   - Order by date in OCR text

5. **Review & Final Summary Panel**
   - Editable, RTL summary box (centered, resizable)
   - Section label above summary
   - AI Assist button in action bar

6. **AI Dialog & Prompt Management**
   - Floating, resizable, draggable AI dialog
   - Maximized text areas
   - Save/close, prompt templates, knowledge file management

7. **Export & Output Management**
   - Export summaries (txt, zip, etc.)
   - Output folder structure (patient ID, date)
   - Export history, original files, and summaries

8. **Security, Retention, and Multi-User**
   - Encrypted storage
   - Retention policy (auto-delete)
   - Multi-user support (Dropbox/Google Drive structure)

9. **Knowledge Files & AI Learning**
   - Upload/manage knowledge files
   - AI learns from manual edits and feedback

10. **ABBYY Advanced Region Mapping (Planned)**
    - Parse ABBYY output for block/area coordinates
    - Map/overlay summary sources on scanned images
    - UI highlights for summary source regions

11. **Future Enhancements**
    - Drag-and-drop input
    - Auto-detect patient ID from OCR text
    - More export formats
    - Advanced multi-user collaboration
    - Deeper AI learning/fine-tuning

### Visual Flow (Text Diagram)

```
[1] Patient ID Handling
      ↓
[2] File Selection & Batch Input
      ↓
[3] OCR Processing & Confidence Scoring
      ↓
[4] Unified Files Preview Panel
      ↓
[5] Review & Final Summary Panel
      ↓
[6] AI Dialog & Prompt Management
      ↓
[7] Export & Output Management
      ↓
[8] Security, Retention, Multi-User
      ↓
[9] Knowledge Files & AI Learning
      ↓
[10] ABBYY Advanced Region Mapping
      ↓
[11] Future Enhancements
```

--- 