from google.cloud import vision_v1
import os

# Set the environment variable for the service account key file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.path.dirname(__file__), "gil", "ocr-service-account.json")

def test_vision_ocr(image_path):
    """Test Google Vision OCR with a direct API call."""
    try:
        # Create a client
        client = vision_v1.ImageAnnotatorClient()

        # Read the image file
        with open(image_path, 'rb') as image_file:
            content = image_file.read()

        # Create the image object
        image = vision_v1.Image(content=content)

        # Perform OCR
        response = client.document_text_detection(image=image)
        text = response.full_text_annotation.text

        print("OCR Text:")
        print(text)
        return text

    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    # Test with a sample image
    test_vision_ocr("test.jpg")
