import os
import sys
import json
import logging
from flask import Flask, request, jsonify
import pytesseract
from PIL import Image
import pdf2image
import ollama
from dicta import Dicta
import tempfile
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backend.log'),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)

class DocumentProcessor:
    def __init__(self):
        self.ollama = ollama.Client()
        self.dicta = Dicta()
        
    def process_image(self, image_path):
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image, lang='heb+eng')
            return text
        except Exception as e:
            logging.error(f"Error processing image: {str(e)}")
            raise

    def process_pdf(self, pdf_path):
        try:
            images = pdf2image.convert_from_path(pdf_path)
            texts = []
            for i, image in enumerate(images):
                text = pytesseract.image_to_string(image, lang='heb+eng')
                texts.append(f"--- Page {i+1} ---\n{text}")
            return "\n\n".join(texts)
        except Exception as e:
            logging.error(f"Error processing PDF: {str(e)}")
            raise

    def process_file(self, file_path):
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext == '.pdf':
            return self.process_pdf(file_path)
        else:
            return self.process_image(file_path)

    def enhance_prompt(self, base_prompt, text, language):
        enhanced_prompt = base_prompt
        
        # Add language-specific instructions
        if language == 'hebrew':
            enhanced_prompt += "\nPlease ensure the summary is in Hebrew."
        elif language == 'english':
            enhanced_prompt += "\nPlease ensure the summary is in English."
            
        # Analyze text with Dicta for Hebrew content
        if any('\u0590' <= char <= '\u05FF' for char in text):
            enhanced_prompt += "\nThe text contains Hebrew content. Please maintain proper Hebrew formatting and terminology."
            
        return enhanced_prompt

    async def process_files(self, file_paths, prompt, language='auto'):
        all_text = []
        
        for file_path in file_paths:
            text = self.process_file(file_path)
            all_text.append(text)
            
        combined_text = "\n\n".join(all_text)
        
        # Enhance prompt based on content and language
        enhanced_prompt = self.enhance_prompt(prompt, combined_text, language)
        
        # Generate summary using Ollama
        response = self.ollama.generate(
            model="mistral",
            prompt=f"{enhanced_prompt}\n\nText to summarize:\n{combined_text}"
        )
        
        return response['response']

processor = DocumentProcessor()

@app.route('/process', methods=['POST'])
def process_files():
    try:
        data = request.json
        file_paths = data.get('files', [])
        prompt = data.get('prompt', '')
        language = data.get('language', 'auto')
        
        result = processor.process_files(file_paths, prompt, language)
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        logging.error(f"Error processing files: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5000))
    app.run(host='127.0.0.1', port=port) 