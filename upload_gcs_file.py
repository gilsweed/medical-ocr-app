from google.cloud import storage

def upload_gcs_file(bucket_name, source_file_path, destination_blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_path)
    print(f"Uploaded {source_file_path} to gs://{bucket_name}/{destination_blob_name}")

if __name__ == "__main__":
    # Example usage:
    # Replace with your bucket name, local file path, and desired blob name
    upload_gcs_file("your-bucket-name", "test.pdf", "test.pdf")
