from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
from PIL import Image
import pytesseract
from langdetect import detect
from llama_cpp import Llama
import gc
import atexit
import signal
from io import BytesIO
import base64
import time
import sys
import socket
import subprocess

app = Flask(__name__)
CORS(app)

# Initialize global variables at module level
MODEL_PATH = 'backend/models/llama-2-7b-chat.Q2_K.gguf'
llm = None

def cleanup_resources():
    global llm
    try:
        if llm:
            del llm
        gc.collect()
    except Exception as e:
        print(f"Error during cleanup: {str(e)}")

def signal_handler(signum, frame):
    cleanup_resources()
    exit(0)

# Register cleanup handlers
atexit.register(cleanup_resources)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def load_model():
    global llm
    try:
        model_path = os.path.join(os.path.dirname(__file__), 'models', 'llama-2-7b-chat.Q2_K.gguf')
        print(f"Loading model from: {model_path}")
        print("Initializing model with optimized parameters...")
        
        # Further reduced memory parameters
        llm = Llama(
            model_path=model_path,
            n_ctx=1024,      # Reduced from 2048
            n_batch=1,       # Reduced from 2
            n_threads=1,     # Keep at 1
            n_gpu_layers=0,  # CPU only
            verbose=False,
            offload_kqv=True # Enable offloading to reduce memory usage
        )
        print("Model loaded successfully!")
    except Exception as e:
        print(f"Error loading model: {str(e)}")
        raise

def split_text_into_chunks(text, max_chunk_size=300):
    if not text or not text.strip():
        return []
        
    # Split into sentences first
    sentences = text.split('.')
    chunks = []
    current_chunk = []
    current_size = 0
    
    for sentence in sentences:
        sentence = sentence.strip() + '.'
        sentence_size = len(sentence)
        
        if current_size + sentence_size > max_chunk_size and current_chunk:
            chunks.append(' '.join(current_chunk))
            current_chunk = [sentence]
            current_size = sentence_size
        else:
            current_chunk.append(sentence)
            current_size += sentence_size
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

@app.route('/api/summarize', methods=['POST'])
def summarize():
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
            
        print(f"Received text of length: {len(text)}")
        
        # Split text into smaller chunks
        chunks = split_text_into_chunks(text)
        total_chunks = len(chunks)
        print(f"Processing {total_chunks} chunks")
        
        summaries = []
        for i, chunk in enumerate(chunks, 1):
            print(f"Processing chunk {i} of {total_chunks}")
            try:
                # Generate summary for each chunk
                prompt = f"Summarize the following text in Hebrew:\n\n{chunk}"
                response = llm(prompt, max_tokens=150, stop=["</s>"], echo=False)
                summary = response['choices'][0]['text'].strip()
                summaries.append(summary)
                
                # Add a small delay between chunks to prevent memory pressure
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error processing chunk {i}: {str(e)}")
                continue
        
        # Combine summaries
        final_summary = ' '.join(summaries)
        return jsonify({"summary": final_summary})
        
    except Exception as e:
        print(f"Error in summarization: {str(e)}")
        return jsonify({"error": str(e)}), 500

def process_image_with_ocr(image_path):
    try:
        print(f"Processing file: {os.path.basename(image_path)}")
        img = Image.open(image_path)
        print(f"Image opened successfully. Size: {img.size}, Mode: {img.mode}")
        
        # Convert RGBA to RGB if needed
        if img.mode == 'RGBA':
            print("Converting RGBA to RGB")
            img = img.convert('RGB')
        
        # Try Tesseract first since it's more reliable
        print("Starting Tesseract OCR...")
        tesseract_result = pytesseract.image_to_string(img, lang='heb+eng')
        tesseract_length = len(tesseract_result)
        print(f"Tesseract result length: {tesseract_length}")
        
        # Only try Dicta if Tesseract result is too short
        if tesseract_length < 100:
            print("Starting Dicta OCR...")
            try:
                dicta_result = process_with_dicta(img)
                dicta_length = len(dicta_result)
                print(f"Dicta result length: {dicta_length}")
                
                # Use Dicta result if it's significantly longer
                if dicta_length > tesseract_length * 1.5:
                    return dicta_result
            except Exception as e:
                print(f"Dicta OCR error: {str(e)}")
        
        return tesseract_result
        
    except Exception as e:
        print(f"Error in OCR processing: {str(e)}")
        return ""

def process_with_dicta(image):
    try:
        # Convert image to base64
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        # Prepare request
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        data = {
            'image': img_str,
            'language': 'he'
        }
        
        # Try multiple DNS servers
        dns_servers = ['8.8.8.8', '1.1.1.1', '9.9.9.9']
        for dns in dns_servers:
            try:
                # Configure session with specific DNS
                session = requests.Session()
                session.mount('https://', requests.adapters.HTTPAdapter(
                    max_retries=3,
                    pool_connections=1,
                    pool_maxsize=1
                ))
                
                # Make request with timeout and DNS configuration
                response = session.post(
                    'https://services.dicta.org.il/api/ocr/recognize',
                    headers=headers,
                    json=data,
                    timeout=10,
                    verify=True
                )
                
                if response.status_code == 200:
                    return response.json().get('text', '')
                else:
                    print(f"Dicta API error: {response.status_code}")
                    continue
                    
            except requests.exceptions.RequestException as e:
                print(f"Dicta API request error with DNS {dns}: {str(e)}")
                continue
                
        print("All DNS attempts failed, falling back to Tesseract")
        return ""
            
    except Exception as e:
        print(f"Dicta processing error: {str(e)}")
        return ""

@app.route('/api/ocr', methods=['POST'])
def ocr():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
            
        print(f"Processing file: {file.filename}")
        image = Image.open(file)
        print(f"Image opened successfully. Size: {image.size}, Mode: {image.mode}")
        
        # Convert RGBA to RGB if needed
        if image.mode == 'RGBA':
            print("Converting RGBA to RGB")
            image = image.convert('RGB')
        
        print("Starting OCR processing...")
        text = process_image_with_ocr(file.filename)
        
        if not text.strip():
            return jsonify({"error": "No text detected"}), 400
            
        try:
            lang = detect(text)
        except:
            lang = "unknown"
            
        return jsonify({
            "text": text,
            "language": lang
        })
        
    except Exception as e:
        print(f"Error in OCR endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    try:
        print(f"Starting server with model path: {MODEL_PATH}")
        print(f"Model file exists: {os.path.exists(MODEL_PATH)}")
        
        # Try to load model with reduced memory footprint
        load_model()
        
        # Use a specific port for the application
        PORT = 5006
        
        # Check if port is in use
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('0.0.0.0', PORT))
            sock.close()
            print(f"Port {PORT} is available")
        except OSError:
            print(f"Port {PORT} is in use, attempting to kill existing process...")
            subprocess.run(['lsof', '-ti', f':{PORT}', '-sTCP:LISTEN', '-kill'], capture_output=True)
            print(f"Killed process on port {PORT}")
        
        print(f"Starting server on port {PORT}")
        app.run(debug=False, port=PORT, host='0.0.0.0')
        
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        # Try different ports if the default is in use
        ports = [5006, 5007, 5008, 5009]
        for port in ports:
            try:
                print(f"Attempting to start server on port {port}")
                app.run(debug=False, port=port, host='0.0.0.0')
                break
            except OSError as e:
                if "Address already in use" in str(e):
                    print(f"Port {port} is in use, trying next port...")
                    continue
                else:
                    raise
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        cleanup_resources()
        sys.exit(1) 