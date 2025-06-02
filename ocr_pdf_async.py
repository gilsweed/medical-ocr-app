import time
from google.cloud import storage, vision_v1
from google.cloud.vision_v1 import types
import json
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set the environment variable for the service account key file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.path.dirname(__file__), "gil", "ocr-service-account.json")

def check_bucket_exists(bucket_name):
    """Check if the GCS bucket exists and is accessible."""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        return bucket.exists()
    except Exception as e:
        logger.error(f"Error checking bucket existence: {e}")
        return False

def upload_gcs_file(bucket_name, source_file_path, destination_blob_name):
    """Upload a file to GCS bucket."""
    try:
        if not check_bucket_exists(bucket_name):
            logger.error(f"Bucket {bucket_name} does not exist or is not accessible")
            return False

        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        
        # Check if source file exists and is readable
        if not os.path.exists(source_file_path):
            logger.error(f"Source file {source_file_path} does not exist")
            return False
        if not os.access(source_file_path, os.R_OK):
            logger.error(f"Source file {source_file_path} is not readable")
            return False

        blob.upload_from_filename(source_file_path)
        logger.info(f"Uploaded {source_file_path} to gs://{bucket_name}/{destination_blob_name}")
        return True
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return False

def async_ocr_pdf(bucket_name, source_blob_name, output_prefix):
    """Run async OCR on a PDF file in GCS."""
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
        logger.info("Processing OCR... (this may take a while)")
        operation.result(timeout=600)
        logger.info("OCR processing complete.")
        return True
    except Exception as e:
        logger.error(f"Error running OCR: {e}")
        return False

def download_gcs_results(bucket_name, output_prefix, local_output_dir):
    """Download OCR results from GCS."""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blobs = bucket.list_blobs(prefix=output_prefix)
        
        os.makedirs(local_output_dir, exist_ok=True)
        
        for blob in blobs:
            if blob.name.endswith('.json'):
                local_path = os.path.join(local_output_dir, os.path.basename(blob.name))
                blob.download_to_filename(local_path)
                logger.info(f"Downloaded {blob.name} to {local_path}")
        return True
    except Exception as e:
        logger.error(f"Error downloading results: {e}")
        return False

def parse_ocr_results(json_file_path, output_text_file):
    """Parse OCR results from JSON file and save to text file."""
    try:
        with open(json_file_path, 'r') as f:
            response = json.load(f)
        
        text = ""
        if 'fullTextAnnotation' in response:
            text = response['fullTextAnnotation'].get('text', '')
        
        with open(output_text_file, 'w', encoding='utf-8') as f:
            f.write(text)
        
        logger.info(f"Saved OCR text to {output_text_file}")
        return True
    except Exception as e:
        logger.error(f"Error parsing OCR results: {e}")
        return False

def delete_gcs_file(bucket_name, blob_name):
    """Delete a file from GCS bucket."""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.delete()
        logger.info(f"Deleted {blob_name} from bucket {bucket_name}")
        return True
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        return False

def delete_gcs_results(bucket_name, output_prefix):
    """Delete all OCR result files from GCS bucket."""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blobs = bucket.list_blobs(prefix=output_prefix)
        
        for blob in blobs:
            blob.delete()
            logger.info(f"Deleted {blob.name} from bucket {bucket_name}")
        return True
    except Exception as e:
        logger.error(f"Error deleting results: {e}")
        return False
