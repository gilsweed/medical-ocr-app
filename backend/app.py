from flask import Flask, request, jsonify
from flask_cors import CORS
from llama_cpp import Llama
import os
from dotenv import load_dotenv

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

        # Prepare the prompt using the custom prompt if provided
        prompt = f"""{custom_prompt if custom_prompt else default_prompt}

Text to summarize:
{text}

Summary:"""

        print("Generating summary...")
        # Generate summary
        output = llm(
            prompt,
            max_tokens=512,
            temperature=0.7,
            top_p=0.95,
            repeat_penalty=1.2,
            stop=["Text to summarize:", "\n\n"]
        )
        print("Summary generated successfully!")

        summary = output['choices'][0]['text'].strip()
        
        return jsonify({
            'summary': summary
        })

    except Exception as e:
        print(f"Error in summarize endpoint: {str(e)}")
        return jsonify({
            'error': f'Error generating summary: {str(e)}'
        }), 500

if __name__ == '__main__':
    # Add debug output for the model path
    print(f"Starting server with model path: {MODEL_PATH}")
    print(f"Model file exists: {os.path.exists(MODEL_PATH)}")
    
    app.run(debug=True, port=5001, host='0.0.0.0') 