import os
import sys
import json
import logging
import signal
import atexit
import multiprocessing
import threading
from flask import Flask, request, jsonify, g
from flask_cors import CORS
import pytesseract
from pdf2image import convert_from_path
import tempfile
import traceback
from config import HOST, PORT, LOG_LEVEL, LOG_FORMAT, SUPPORTED_FORMATS, cleanup_resources

# Configure multiprocessing to use 'spawn' method
multiprocessing.set_start_method('spawn', force=True)

# Configure logging with more detail
logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global flags and locks
is_shutting_down = False
shutdown_lock = threading.Lock()
cleanup_done = False

def signal_handler(signum, frame):
    """Handle termination signals."""
    global is_shutting_down, cleanup_done
    with shutdown_lock:
        if is_shutting_down:
            return
        is_shutting_down = True
        
        if cleanup_done:
            return
            
        logger.info(f"Received signal {signum}")
        try:
            # Clean up multiprocessing resources
            for child in multiprocessing.active_children():
                child.terminate()
                child.join(timeout=1)
                if child.is_alive():
                    child.kill()
                    child.join()
            
            # Clean up any remaining semaphores
            multiprocessing.resource_tracker._resource_tracker._stop = True
            multiprocessing.resource_tracker._resource_tracker.join()
            
            cleanup_done = True
            sys.exit(0)
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            sys.exit(1)

# Register signal handlers
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

@app.route('/')
@app.route('/health')
def health_check():
    """Health check endpoint."""
    try:
        logger.debug("Health check requested")
        response = jsonify({'status': 'ok'})
        logger.debug(f"Health check response: {response.get_data(as_text=True)}")
        return response, 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

def process_image(image_path):
    """Process an image file using OCR."""
    try:
        logger.info(f"Processing image: {image_path}")
        # Perform OCR on the image
        text = pytesseract.image_to_string(image_path, lang='heb+eng')
        logger.info("Image processing completed successfully")
        return text.strip()
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        return str(e)

def process_pdf(pdf_path):
    """Process a PDF file by converting pages to images and performing OCR."""
    try:
        logger.info(f"Processing PDF: {pdf_path}")
        # Convert PDF to images
        images = convert_from_path(pdf_path)
        text = ""
        
        # Process each page
        for i, image in enumerate(images):
            logger.info(f"Processing page {i+1} of {len(images)}")
            # Save image temporarily
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp:
                image.save(temp.name)
                # Process the image
                page_text = process_image(temp.name)
                text += f"\n--- Page {i+1} ---\n{page_text}\n"
                # Clean up
                os.unlink(temp.name)
        
        logger.info("PDF processing completed successfully")
        return text.strip()
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        return str(e)

@app.route('/api/process', methods=['POST'])
def process_file():
    """Process files from file paths."""
    try:
        logger.info("Received process request")
        data = request.get_json()
        if not data or 'filePath' not in data:
            logger.error("No file path provided in request")
            return jsonify({'error': 'No file path provided'}), 400
        
        file_path = data['filePath']
        logger.info(f"Processing file: {file_path}")
        
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return jsonify({'error': 'File not found'}), 404
        
        # Process based on file type
        if file_path.lower().endswith('.pdf'):
            text = process_pdf(file_path)
        else:
            text = process_image(file_path)
        
        logger.info("File processing completed successfully")
        return jsonify({
            'success': True,
            'text': text
        })
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Add error handler for unhandled exceptions
@app.errorhandler(Exception)
def handle_error(error):
    """Global error handler."""
    try:
        logger.error(f"Unhandled error: {str(error)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(error)
        }), 500
    except Exception as e:
        logger.error(f"Error in error handler: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

# Add before_request handler to track if response was sent
@app.before_request
def before_request():
    """Track if response was sent."""
    g.response_sent = False

# Add after_request handler to mark response as sent
@app.after_request
def after_request(response):
    """Mark response as sent."""
    g.response_sent = True
    return response

# Expose the WSGI application for Gunicorn
application = app 