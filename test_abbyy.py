import requests
import json
import sys

def test_abbyy_ocr(file_path):
    """Test ABBYY OCR on a single file."""
    url = "http://localhost:8082/api/process"
    data = {
        "file_path": file_path,
        "engine": "abbyy",
        "batch_mode": False
    }
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        
        if result.get('success'):
            print("OCR successful!")
            print(f"Confidence: {result.get('confidence')}")
            print("\nText preview (first 200 chars):")
            print(result.get('text')[:200])
        else:
            print("OCR failed!")
            print(f"Error: {result.get('error')}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_abbyy.py <file_path>")
        sys.exit(1)
        
    test_abbyy_ocr(sys.argv[1]) 