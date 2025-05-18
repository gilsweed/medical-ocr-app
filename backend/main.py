from flask import Flask, request, jsonify
from google.cloud import storage
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import os
import uuid

app = Flask(__name__)

GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME")
UPLOAD_FOLDER = "/tmp"
ocr_results = {}

def upload_to_gcs(local_path, gcs_filename):
    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(gcs_filename)
    blob.upload_from_filename(local_path)
    return blob

def delete_from_gcs(gcs_filename):
    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(gcs_filename)
    blob.delete()

def file_exists_in_gcs(gcs_filename):
    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(gcs_filename)
    return blob.exists()

def real_ocr(local_path):
    text = ""
    ext = os.path.splitext(local_path)[1].lower()
    if ext == ".pdf":
        images = convert_from_path(local_path)
        for img in images:
            text += pytesseract.image_to_string(img, lang="eng+heb") + "\n"
    else:
        img = Image.open(local_path)
        text = pytesseract.image_to_string(img, lang="eng+heb")
    return text.strip()

@app.route("/api/ocr/pdf", methods=["POST"])
def ocr_pdf():
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"}), 400
    file = request.files["file"]
    job_id = str(uuid.uuid4())
    filename = f"{job_id}_{file.filename}"
    local_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(local_path)

    try:
        upload_to_gcs(local_path, filename)
        ocr_text = real_ocr(local_path)
        ocr_results[job_id] = ocr_text
        delete_from_gcs(filename)
        if file_exists_in_gcs(filename):
            warning = f"WARNING: File {filename} was NOT deleted from bucket {GCS_BUCKET_NAME}!"
        else:
            warning = ""
        os.remove(local_path)
        return jsonify({"success": True, "job_id": job_id, "warning": warning})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/ocr/pdf/status/<job_id>", methods=["GET"])
def ocr_pdf_status(job_id):
    text = ocr_results.get(job_id, "")
    return jsonify({"job_id": job_id, "status": "done", "success": True, "text": text})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8082)
