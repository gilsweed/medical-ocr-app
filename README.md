# Doctor Insurance OCR and Analysis System

A web application for processing medical documents using OCR and AI-powered summarization, specifically designed for insurance assessments.

## Features

- OCR processing for both images and PDF files
- Hebrew and English text recognition
- AI-powered text summarization using Llama 2
- Customizable summary settings
- Progress tracking for both OCR and summarization
- Persistent user preferences

## Technical Stack

- Frontend: React.js
- Backend: Flask (Python)
- OCR: Tesseract.js
- PDF Processing: PDF.js
- AI Model: Llama 2 (llama-2-7b-chat.Q2_K.gguf)

## Setup

### Frontend

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

### Backend

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Download the Llama 2 model:
- Download `llama-2-7b-chat.Q2_K.gguf`
- Place it in `backend/models/`

5. Start the Flask server:
```bash
python app.py
```

## Usage

1. Select the language for OCR (Hebrew, English, or both)
2. Upload an image or PDF file
3. Click "Scan Document" to process the file
4. Once OCR is complete, click "Summarize Text" to generate an AI summary
5. Adjust summary settings using the gear icon ⚙️

## Configuration

- OCR language can be selected for each document
- Summary language preference is stored in browser localStorage
- Custom prompts can be configured for summarization
- Backend port can be configured (default: 5001)
