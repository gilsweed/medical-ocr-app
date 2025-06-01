from google.cloud import vision

def ocr_image(image_path):
    client = vision.ImageAnnotatorClient()
    with open(image_path, "rb") as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    if texts:
        print("OCR Result:\n", texts[0].description)
    else:
        print("No text detected.")
    if response.error.message:
        print("Error:", response.error.message)

if __name__ == "__main__":
    # Replace with the path to a test image (JPG, PNG, or PDF page as image)
    ocr_image("test.jpg")
