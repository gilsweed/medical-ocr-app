from flask import Flask, request, jsonify
import os
import subprocess
import json

app = Flask(__name__)

def run_google_vision_ocr(file_path):
    import ocr_pdf_async
    bucket_name = "hebrew-ocr-app-bucket-gilsweed-20240516"
    gcs_pdf = os.path.basename(file_path)
    output_prefix = "ocr_results/test"
    local_dir = "."
    output_txt = f"{os.path.splitext(gcs_pdf)[0]}_google_ocr.txt"

    if not ocr_pdf_async.upload_gcs_file(bucket_name, file_path, gcs_pdf):
        return None, "Google Vision: Upload failed"

    if not ocr_pdf_async.async_ocr_pdf(bucket_name, gcs_pdf, output_prefix):
        ocr_pdf_async.delete_gcs_file(bucket_name, gcs_pdf)
        return None, "Google Vision: OCR failed"

    json_files = ocr_pdf_async.download_gcs_results(bucket_name, output_prefix, local_dir)
    if not json_files:
        ocr_pdf_async.delete_gcs_file(bucket_name, gcs_pdf)
        return None, "Google Vision: Download failed"

    if not ocr_pdf_async.parse_ocr_results(json_files, output_txt):
        return None, "Google Vision: Parse failed"

    ocr_pdf_async.delete_gcs_file(bucket_name, gcs_pdf)
    ocr_pdf_async.delete_gcs_results(bucket_name, output_prefix)

    try:
        with open(output_txt, "r", encoding="utf-8") as f:
            text = f.read()
        return text, None
    except Exception as e:
        return None, f"Google Vision: Could not read output file: {e}"

def run_abbyy_ocr(file_path):
    output_txt = f"{os.path.splitext(os.path.basename(file_path))[0]}_abbyy_ocr.txt"
    abbyy_cli_path = "/Users/gilsweed/Desktop/Brurya/ABBYY_SDK/Samples/CommandLineInterface/CommandLineInterface"
    # Use "TextUnicodeDefaults" as the export format for ABBYY CLI
    try:
        result = subprocess.run(
            [
                abbyy_cli_path,
                "-if", file_path,
                "-of", output_txt,
                "-f", "TextUnicodeDefaults"
            ],
            capture_output=True, text=True, timeout=300
        )
        if result.returncode != 0:
            return None, f"ABBYY: CLI error: {result.stderr}"
        with open(output_txt, "r", encoding="utf-8") as f:
            text = f.read()
        return text, None
    except Exception as e:
        return None, f"ABBYY: Exception: {e}"

@app.route('/api/process', methods=['POST'])
def process_file():
    data = request.get_json()
    file_path = data.get('file_path')
    engine = data.get('engine', 'abbyy').lower()

    if not file_path or not os.path.exists(file_path):
        return jsonify({'success': False, 'error': 'File not found'}), 400

    if engine == "google":
        ocr_text, error = run_google_vision_ocr(file_path)
    elif engine == "abbyy":
        ocr_text, error = run_abbyy_ocr(file_path)
    else:
        return jsonify({'success': False, 'error': f'Unknown OCR engine: {engine}'}), 400

    if error:
        return jsonify({'success': False, 'error': error}), 500

    return jsonify({'success': True, 'text': ocr_text})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8082)
