from flask import Flask, request, jsonify
import os
import subprocess
import json
import logging
from ocr_pdf_async import (
    upload_gcs_file,
    async_ocr_pdf,
    download_gcs_results,
    parse_ocr_results,
    delete_gcs_file,
    delete_gcs_results
)
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Set environment variables
GCS_BUCKET_NAME = "hebrew-ocr-app-bucket-gilsweed-20240516"
UPLOAD_FOLDER = "/tmp"

def run_abbyy_ocr(file_path, batch_mode=False):
    output_txt = f"{os.path.splitext(os.path.basename(file_path))[0]}_abbyy_ocr.txt"
    output_xml = f"{os.path.splitext(os.path.basename(file_path))[0]}_abbyy_ocr.xml"
    abbyy_cli_path = "/Users/gilsweed/Desktop/Brurya/ABBYY_SDK/Samples/CommandLineInterface/CommandLineInterface"
    
    # Set environment variables for this process
    env = os.environ.copy()
    env['FRENGINE_ROOT'] = '/Users/gilsweed/Desktop/Brurya/ABBYY_SDK/FREngine.framework'
    env['DYLD_LIBRARY_PATH'] = '/Users/gilsweed/Desktop/Brurya/ABBYY_SDK/FREngine.framework/Versions/Current/Libraries'
    env['DYLD_FALLBACK_LIBRARY_PATH'] = '/Users/gilsweed/Desktop/Brurya/ABBYY_SDK/FREngine.framework/Versions/Current/Libraries'
    env['DYLD_FRAMEWORK_PATH'] = '/Users/gilsweed/Desktop/Brurya/ABBYY_SDK'
    
    try:
        # First run with XML output to get confidence levels
        xml_result = subprocess.run(
            [
                abbyy_cli_path,
                "-if", file_path,
                "-of", output_xml,
                "-f", "XML",
                "-rm", "Accurate"
            ],
            capture_output=True, text=True, timeout=300,
            env=env
        )
        
        if xml_result.returncode != 0:
            return None, None, f"ABBYY: XML generation error: {xml_result.stderr}"
            
        # Parse XML to get confidence levels
        confidence_level = parse_confidence_from_xml(output_xml)
        
        # Then run with text output
        text_result = subprocess.run(
            [
                abbyy_cli_path,
                "-if", file_path,
                "-of", output_txt,
                "-f", "Text",
                "-rm", "Accurate"
            ],
            capture_output=True, text=True, timeout=300,
            env=env
        )
        
        if text_result.returncode != 0:
            return None, None, f"ABBYY: Text generation error: {text_result.stderr}"
            
        # Read the OCR text
        with open(output_txt, 'r', encoding='utf-8') as f:
            ocr_text = f.read()
            
        # Clean up temporary files
        os.remove(output_txt)
        os.remove(output_xml)
        
        return ocr_text, confidence_level, None
        
    except Exception as e:
        return None, None, f"ABBYY: Error: {str(e)}"

def parse_confidence_from_xml(xml_file):
    try:
        import xml.etree.ElementTree as ET
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Find all confidence values
        confidence_values = []
        for page in root.findall('.//page'):
            for block in page.findall('.//block'):
                for par in block.findall('.//par'):
                    for line in par.findall('.//line'):
                        for char in line.findall('.//char'):
                            conf = char.get('confidence')
                            if conf:
                                confidence_values.append(float(conf))
        
        # Calculate average confidence
        if confidence_values:
            return sum(confidence_values) / len(confidence_values)
        return 0.0
        
    except Exception as e:
        logger.error(f"Error parsing confidence from XML: {e}")
        return 0.0

@app.route('/api/process', methods=['POST'])
def process_file():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        file_path = data.get('file_path')
        engine = data.get('engine', 'abbyy')  # Default to ABBYY if not specified
        
        if not file_path:
            return jsonify({"error": "No file path provided"}), 400
            
        # Convert relative path to absolute if needed
        if not os.path.isabs(file_path):
            file_path = os.path.abspath(file_path)
            
        # Check if file exists and is readable
        if not os.path.exists(file_path):
            return jsonify({"error": f"File not found: {file_path}"}), 404
        if not os.access(file_path, os.R_OK):
            return jsonify({"error": f"File not readable: {file_path}"}), 403
            
        if engine.lower() == 'google':
            # Process with Google Vision OCR
            try:
                # Upload file to GCS
                gcs_filename = os.path.basename(file_path)
                if not upload_gcs_file(GCS_BUCKET_NAME, file_path, gcs_filename):
                    return jsonify({"error": "Failed to upload file to GCS"}), 500
                    
                # Run OCR
                output_prefix = f"ocr_results/{os.path.splitext(gcs_filename)[0]}"
                if not async_ocr_pdf(GCS_BUCKET_NAME, gcs_filename, output_prefix):
                    return jsonify({"error": "Failed to process OCR"}), 500
                    
                # Download results
                local_output_dir = os.path.join(UPLOAD_FOLDER, "ocr_results")
                if not download_gcs_results(GCS_BUCKET_NAME, output_prefix, local_output_dir):
                    return jsonify({"error": "Failed to download OCR results"}), 500
                    
                # Parse results
                output_text_file = os.path.join(UPLOAD_FOLDER, f"{os.path.splitext(gcs_filename)[0]}_google_ocr.txt")
                json_file = os.path.join(local_output_dir, f"{os.path.splitext(gcs_filename)[0]}-output-1-to-1.json")
                if not parse_ocr_results(json_file, output_text_file):
                    return jsonify({"error": "Failed to parse OCR results"}), 500
                    
                # Read OCR text
                with open(output_text_file, 'r', encoding='utf-8') as f:
                    ocr_text = f.read()
                    
                # Clean up
                delete_gcs_file(GCS_BUCKET_NAME, gcs_filename)
                delete_gcs_results(GCS_BUCKET_NAME, output_prefix)
                os.remove(output_text_file)
                os.remove(json_file)
                
                return jsonify({
                    "text": ocr_text,
                    "confidence": 1.0  # Google Vision doesn't provide confidence scores
                })
                
            except Exception as e:
                logger.error(f"Google Vision OCR error: {e}")
                return jsonify({"error": f"Google Vision OCR error: {str(e)}"}), 500
                
        elif engine.lower() == 'abbyy':
            # Process with ABBYY OCR
            ocr_text, confidence, error = run_abbyy_ocr(file_path)
            if error:
                return jsonify({"error": error}), 500
            return jsonify({
                "text": ocr_text,
                "confidence": confidence
            })
            
        else:
            return jsonify({"error": f"Unsupported OCR engine: {engine}"}), 400
            
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/process_batch', methods=['POST'])
def process_batch():
    data = request.get_json()
    file_paths = data.get('file_paths', [])
    engine = data.get('engine', 'abbyy').lower()
    
    if not file_paths:
        return jsonify({'success': False, 'error': 'No files provided'}), 400
        
    results = []
    for file_path in file_paths:
        if not os.path.exists(file_path):
            results.append({
                'file': file_path,
                'success': False,
                'error': 'File not found'
            })
            continue
            
        if engine == "abbyy":
            text, confidence, error = run_abbyy_ocr(file_path, batch_mode=True)
            results.append({
                'file': file_path,
                'success': error is None,
                'text': text,
                'confidence': confidence,
                'error': error
            })
        else:
            results.append({
                'file': file_path,
                'success': False,
                'error': f'Unsupported engine for batch: {engine}'
            })
            
    return jsonify({
        'success': True,
        'results': results
    })

def processFile(self, file_path, engine="abbyy"):
    """Process a file using the specified OCR engine"""
    try:
        # Get the absolute path of the file
        abs_file_path = os.path.abspath(file_path)
        print(f"Processing file: {abs_file_path}")
        
        if not os.path.exists(abs_file_path):
            raise FileNotFoundError(f"File not found: {abs_file_path}")
        
        # Prepare the request data
        data = {
            "file_path": abs_file_path,
            "engine": engine
        }
        
        # Make the API request
        response = requests.post(
            "http://localhost:8082/api/process",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                return result.get("text", "")
            else:
                raise Exception(result.get("error", "Unknown error"))
        else:
            raise Exception(f"API request failed with status code: {response.status_code}")
            
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        self.showError(f"Error processing file: {str(e)}")
        return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8082)
