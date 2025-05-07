from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import pytesseract
import tempfile
import os
import requests

app = Flask(__name__)
CORS(app)

def is_hebrew(text):
    hebrew_chars = sum(1 for c in text if '\u0590' <= c <= '\u05FF')
    return hebrew_chars > 0

def dicta_ocr_hebrew(image_path):
    url = "https://dicta.org.il/api/ocr/heb"
    with open(image_path, "rb") as f:
        files = {"file": f}
        response = requests.post(url, files=files)
    if response.status_code == 200:
        return response.json().get("text", "")
    else:
        return f"Error: {response.status_code} - {response.text}"

@app.route('/api/ocr', methods=['POST'])
def ocr_endpoint():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    lang = request.form.get('lang', 'heb+eng')
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name

    try:
        text = pytesseract.image_to_string(Image.open(tmp_path), lang=lang)
    except Exception as e:
        os.unlink(tmp_path)
        return jsonify({'error': f'Tesseract error: {str(e)}'}), 500

    if is_hebrew(text):
        dicta_text = dicta_ocr_hebrew(tmp_path)
        os.unlink(tmp_path)
        return jsonify({'text': dicta_text})
    else:
        os.unlink(tmp_path)
        return jsonify({'text': text})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
