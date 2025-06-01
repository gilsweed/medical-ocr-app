#!/usr/bin/env python3
import os
import json
from flask import Flask, render_template, request, jsonify
from pathlib import Path
from test_ocr import OCRTester

app = Flask(__name__)
tester = OCRTester()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test', methods=['POST'])
def test_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    expected_text = request.form.get('expected_text', '')
    
    # Save the file temporarily
    temp_path = Path('test_files') / file.filename
    temp_path.parent.mkdir(exist_ok=True)
    file.save(temp_path)
    
    # Run the test
    result = tester.run_test(str(temp_path), expected_text)
    
    # Clean up
    temp_path.unlink()
    
    return jsonify(result)

@app.route('/suite', methods=['POST'])
def test_suite():
    if 'suite' not in request.files:
        return jsonify({'error': 'No test suite file provided'}), 400
    
    suite_file = request.files['suite']
    test_cases = json.load(suite_file)
    
    results = tester.run_test_suite(test_cases)
    return jsonify(results)

if __name__ == '__main__':
    app.run(port=5001, debug=True) 