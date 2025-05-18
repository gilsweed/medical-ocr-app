from google.cloud import storage

def delete_gcs_file(bucket_name, blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.delete()
    print(f"Deleted {blob_name} from bucket {bucket_name}")

if __name__ == "__main__":
    # Example usage:
    # Replace with your bucket name and file name (blob name)
    delete_gcs_file("your-bucket-name", "your-file-name.pdf")
