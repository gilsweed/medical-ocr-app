from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/api/process', methods=['POST'])
def process_file():
    data = request.get_json()
    file_path = data.get('file_path')
    print(f"Received file_path: {file_path}")
    print(f"os.path.exists: {os.path.exists(file_path)}")
    if not file_path or not os.path.exists(file_path):
        return jsonify({'success': False, 'error': 'File not found'}), 400

    # Dummy OCR result for testing
    ocr_text = f"OCR would process: {file_path}"
    return jsonify({'success': True, 'text': ocr_text})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8082)
