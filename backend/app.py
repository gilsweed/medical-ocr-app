from flask import Flask, request, jsonify
from flask_cors import CORS
from llama_cpp import Llama
import os
from dotenv import load_dotenv
import requests
from PIL import Image
import io
import base64
from langdetect import detect
import pytesseract

load_dotenv()

app = Flask(__name__)
# Enable CORS for all routes and origins
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Initialize Llama model - look in backend/models directory
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models', 'llama-2-7b-chat.Q2_K.gguf')
print(f"Loading model from: {MODEL_PATH}")

try:
    if not os.path.exists(MODEL_PATH):
        print(f"Error: Model file not found at {MODEL_PATH}")
        llm = None
    else:
        llm = Llama(
            model_path=MODEL_PATH,
            n_ctx=8192,  # Increased context window to handle larger documents
            n_threads=os.cpu_count(),  # Use all CPU cores
        )
        print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    llm = None

def split_text_into_chunks(text, max_chunk_size=4000):
    """Split text into chunks of approximately max_chunk_size characters."""
    chunks = []
    current_chunk = []
    current_size = 0
    
    # Split text into paragraphs
    paragraphs = text.split('\n\n')
    
    for paragraph in paragraphs:
        # If a single paragraph is too long, split it into sentences
        if len(paragraph) > max_chunk_size:
            sentences = paragraph.split('. ')
            for sentence in sentences:
                if current_size + len(sentence) > max_chunk_size:
                    chunks.append('\n\n'.join(current_chunk))
                    current_chunk = [sentence]
                    current_size = len(sentence)
                else:
                    current_chunk.append(sentence)
                    current_size += len(sentence)
        else:
            if current_size + len(paragraph) > max_chunk_size:
                chunks.append('\n\n'.join(current_chunk))
                current_chunk = [paragraph]
                current_size = len(paragraph)
            else:
                current_chunk.append(paragraph)
                current_size += len(paragraph)
    
    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))
    
    return chunks

def ocr_dicta(image: Image.Image) -> str:
    """
    Send a PIL Image to Dicta OCR API and return the recognized Hebrew text.
    """
    # Convert image to JPEG and base64 encode it
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    # Dicta API endpoint
    url = "https://services.dicta.org.il/api/ocr/recognize"
    payload = {
        "image": img_str,
        "lang": "hebrew_printed"
    }
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result.get("text", "")
    except Exception as e:
        print(f"Dicta OCR error: {e}")
        return ""

def detect_language(text):
    try:
        lang = detect(text)
        return lang  # 'he' for Hebrew, 'en' for English, etc.
    except Exception:
        return 'unknown'

def ocr_best(image: Image.Image) -> str:
    """
    Run both Dicta and Tesseract OCR, and return the best result for mixed Hebrew/English pages.
    """
    try:
        print("Starting OCR processing...")
        
        # Convert RGBA to RGB if needed
        if image.mode == 'RGBA':
            print("Converting RGBA to RGB")
            image = image.convert('RGB')
        
        print("Starting Tesseract OCR...")
        # Run Tesseract with both languages
        text_tess = pytesseract.image_to_string(image, lang='eng+heb')
        print(f"Tesseract result length: {len(text_tess)}")
        
        print("Starting Dicta OCR...")
        # Run Dicta (Hebrew only)
        text_dicta = ocr_dicta(image)
        print(f"Dicta result length: {len(text_dicta)}")

        # Detect language of each result
        lang_tess = detect_language(text_tess)
        lang_dicta = detect_language(text_dicta)
        print(f"Tesseract detected language: {lang_tess}")
        print(f"Dicta detected language: {lang_dicta}")

        # Heuristic: If Dicta result is mostly Hebrew and not empty, prefer Dicta.
        # If Tesseract result is mostly English, prefer Tesseract.
        # If both are short or empty, return the longer one.
        if lang_dicta == 'he' and len(text_dicta.strip()) > 10:
            # If Dicta found Hebrew, but Tesseract found English, combine both
            if lang_tess == 'en' and len(text_tess.strip()) > 10:
                print("Combining Hebrew (Dicta) and English (Tesseract) results")
                return text_dicta + "\n\n" + text_tess
            print("Using Dicta result (Hebrew)")
            return text_dicta
        elif lang_tess == 'en' and len(text_tess.strip()) > 10:
            print("Using Tesseract result (English)")
            return text_tess
        else:
            # Fallback: return the longer result
            print("Using longer result as fallback")
            return text_dicta if len(text_dicta) > len(text_tess) else text_tess
    except Exception as e:
        print(f"Error in ocr_best: {str(e)}")
        raise Exception(f"OCR processing failed: {str(e)}")

@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({"status": "ok", "message": "Backend is running"})

@app.route('/api/summarize', methods=['POST', 'OPTIONS'])
def summarize():
    if request.method == 'OPTIONS':
        return '', 204
        
    if not llm:
        return jsonify({
            'error': 'Model not loaded. Please ensure the model file is present and correctly configured.'
        }), 500

    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No JSON data received'}), 400
            
        text = data.get('text', '')
        custom_prompt = data.get('prompt', '')
        print(f"Received text of length: {len(text)}")
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400

        default_prompt = """ל/י כרופא/ה תעסוקתי/ת בכיר/ה.
	•	התבסס על המידע הקיים במסמכים רפואיים מצורפים (בעברית ובאנגלית).
	•	ערוך סיכום מקצועי, מובנה ותמציתי של המסמכים, הכולל אבחנות, טיפולים, מגבלות והשלכות על כשירות תעסוקתית.
	•	בסס את הסיכום על הנחיות וחוקים המופיעים בתקנון קרן הפנסיה העדכני של כלל
	•	כלול פרטים מזהים כגון שם המטופל, גיל ועיסוק, בהינתן שהמערכת מקומית ותואמת רגולציה.
	•	ציין אם חלק מהמידע חסר או בלתי קריא בעקבות זיהוי תווים אופטי (OCR).
	•	סכם את ההיסטוריה הרפואית לפי ציר זמן, ושלב את הסיפור הקליני, ההדמייתי והמעבדתי באופן ברור ומובנה.
	•	חלק את הסיכום לפסקאות לפי נושאים רפואיים. הימנע מהשערות לא מבוססות, והתמקד במסר תעסוקתי ברור עבור מקבל ההחלטה.
	•	וודא שהסיכום כתוב בשפה מקצועית, ברורה, רפואית ותעסוקתית כאחד

לבסוף המלץ האם מגיעה נכות לפי תקנון קרן הפנסיה כלל, חלקית או מלאה ולאיזה תקופה"""

        # Split text into chunks if it's too long
        chunks = split_text_into_chunks(text)
        summaries = []
        
        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i+1} of {len(chunks)}")
            
            # Prepare the prompt using the custom prompt if provided
            prompt = f"""{custom_prompt if custom_prompt else default_prompt}

Text to summarize (Part {i+1} of {len(chunks)}):
{chunk}

Summary:"""

            # Generate summary for this chunk
            output = llm(
                prompt,
                max_tokens=512,
                temperature=0.7,
                top_p=0.95,
                repeat_penalty=1.2,
                stop=["Text to summarize:", "\n\n"]
            )
            
            chunk_summary = output['choices'][0]['text'].strip()
            summaries.append(chunk_summary)
        
        # Combine all summaries
        final_summary = "\n\n".join(summaries)
        
        return jsonify({
            'summary': final_summary
        })

    except Exception as e:
        print(f"Error in summarize endpoint: {str(e)}")
        return jsonify({
            'error': f'Error generating summary: {str(e)}'
        }), 500

@app.route('/api/ocr', methods=['POST', 'OPTIONS'])
def process_ocr():
    if request.method == 'OPTIONS':
        return '', 204

    try:
        if 'file' not in request.files:
            print("Error: No file in request")
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            print("Error: Empty filename")
            return jsonify({'error': 'No file selected'}), 400

        print(f"Processing file: {file.filename}")
        
        # Read the image file
        try:
            image_data = file.read()
            image = Image.open(io.BytesIO(image_data))
            print(f"Image opened successfully. Size: {image.size}, Mode: {image.mode}")
        except Exception as e:
            print(f"Error opening image: {str(e)}")
            return jsonify({'error': f'Error opening image: {str(e)}'}), 400

        # Process the image using ocr_best
        try:
            print("Starting OCR processing...")
            result = ocr_best(image)
            print(f"OCR completed. Result length: {len(result)}")
            
            if not result.strip():
                print("Warning: Empty OCR result")
                return jsonify({
                    'text': '',
                    'language': 'unknown',
                    'warning': 'No text was detected in the image'
                })
            
            detected_lang = detect_language(result)
            print(f"Detected language: {detected_lang}")
            
            return jsonify({
                'text': result,
                'language': detected_lang
            })
        except Exception as e:
            print(f"Error during OCR processing: {str(e)}")
            return jsonify({'error': f'Error during OCR processing: {str(e)}'}), 500

    except Exception as e:
        print(f"Unexpected error in OCR endpoint: {str(e)}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

if __name__ == '__main__':
    # Add debug output for the model path
    print(f"Starting server with model path: {MODEL_PATH}")
    print(f"Model file exists: {os.path.exists(MODEL_PATH)}")
    
    app.run(debug=True, port=5001, host='0.0.0.0') 