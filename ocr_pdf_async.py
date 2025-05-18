import time
from google.cloud import storage, vision_v1
from google.cloud.vision_v1 import types
import json
import os

def upload_gcs_file(bucket_name, source_file_path, destination_blob_name):
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(source_file_path)
        print(f"Uploaded {source_file_path} to gs://{bucket_name}/{destination_blob_name}")
        return True
    except Exception as e:
        print(f"[ERROR] Upload step failed: {e}")
        return False

def async_ocr_pdf(bucket_name, source_blob_name, output_prefix):
    try:
        client = vision_v1.ImageAnnotatorClient()
        gcs_source_uri = f"gs://{bucket_name}/{source_blob_name}"
        gcs_destination_uri = f"gs://{bucket_name}/{output_prefix}/"

        mime_type = "application/pdf" if source_blob_name.lower().endswith(".pdf") else "image/tiff"
        feature = vision_v1.Feature(type_=vision_v1.Feature.Type.DOCUMENT_TEXT_DETECTION)
        gcs_source = vision_v1.GcsSource(uri=gcs_source_uri)
        input_config = vision_v1.InputConfig(gcs_source=gcs_source, mime_type=mime_type)
        gcs_destination = vision_v1.GcsDestination(uri=gcs_destination_uri)
        output_config = vision_v1.OutputConfig(gcs_destination=gcs_destination, batch_size=1)
        async_request = vision_v1.AsyncAnnotateFileRequest(
            features=[feature], input_config=input_config, output_config=output_config
        )
        operation = client.async_batch_annotate_files(requests=[async_request])
        print("Processing OCR... (this may take a while)")
        operation.result(timeout=600)
        print("OCR processing complete.")
        return True
    except Exception as e:
        print(f"[ERROR] OCR step failed: {e}")
        return False

def download_gcs_results(bucket_name, output_prefix, local_dir):
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blobs = list(bucket.list_blobs(prefix=output_prefix))
        local_files = []
        for blob in blobs:
            if blob.name.endswith('.json'):
                local_path = os.path.join(local_dir, os.path.basename(blob.name))
                blob.download_to_filename(local_path)
                print(f"Downloaded result: {local_path}")
                local_files.append(local_path)
        if not local_files:
            raise Exception("No result JSON files found in bucket.")
        return local_files
    except Exception as e:
        print(f"[ERROR] Download step failed: {e}")
        return []

def parse_ocr_results(json_files, output_txt):
    try:
        all_text = ""
        for json_file in json_files:
            with open(json_file, "r", encoding="utf-8") as f:
                response = json.load(f)
                for resp in response["responses"]:
                    if "fullTextAnnotation" in resp:
                        all_text += resp["fullTextAnnotation"]["text"] + "\n"
        with open(output_txt, "w", encoding="utf-8") as out_f:
            out_f.write(all_text)
        print(f"OCR text saved to {output_txt}")
        return True
    except Exception as e:
        print(f"[ERROR] Parse step failed: {e}")
        return False

def delete_gcs_file(bucket_name, blob_name):
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.delete()
        print(f"Deleted {blob_name} from bucket {bucket_name}")
        return True
    except Exception as e:
        print(f"[ERROR] Deletion step failed for {blob_name}: {e}")
        return False

def delete_gcs_results(bucket_name, output_prefix):
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blobs = list(bucket.list_blobs(prefix=output_prefix))
        for blob in blobs:
            blob.delete()
            print(f"Deleted {blob.name} from bucket {bucket_name}")
        return True
    except Exception as e:
        print(f"[ERROR] Deletion step failed for result files: {e}")
        return False

if __name__ == "__main__":
    # --- CONFIGURE THESE ---
    bucket_name = "hebrew-ocr-app-bucket-gilsweed-20240516"
    local_pdf = "test.pdf"
    gcs_pdf = "test.pdf"
    output_prefix = "ocr_results/test"
    local_dir = "."
    output_txt = "test_ocr_output.txt"
    # -----------------------

    # 1. Upload
    if not upload_gcs_file(bucket_name, local_pdf, gcs_pdf):
        exit(1)

    # 2. OCR
    if not async_ocr_pdf(bucket_name, gcs_pdf, output_prefix):
        delete_gcs_file(bucket_name, gcs_pdf)
        exit(1)

    # 3. Download results
    json_files = download_gcs_results(bucket_name, output_prefix, local_dir)
    if not json_files:
        delete_gcs_file(bucket_name, gcs_pdf)
        exit(1)

    # 4. Parse and save text
    if not parse_ocr_results(json_files, output_txt):
        print("[ERROR] Could not parse OCR results.")
    
    # 5. Delete original PDF and result JSONs from bucket
    if not delete_gcs_file(bucket_name, gcs_pdf):
        print("[ERROR] Could not delete original PDF from bucket.")
    if not delete_gcs_results(bucket_name, output_prefix):
        print("[ERROR] Could not delete result JSON files from bucket.")

    print("Workflow complete.")
