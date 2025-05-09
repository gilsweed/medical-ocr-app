#!/usr/bin/env python3
import os
import sys
import json
import argparse
import requests
from pathlib import Path
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OCRTester:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.test_files_dir = Path(__file__).parent / "test_files"
        self.test_files_dir.mkdir(exist_ok=True)

    def test_health(self) -> bool:
        """Test server health endpoint"""
        try:
            response = requests.head(f"{self.base_url}/")
            return response.status_code == 200
        except requests.RequestException as e:
            logger.error(f"Health check failed: {e}")
            return False

    def process_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Process a single file through OCR"""
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(f"{self.base_url}/api/process", files=files)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            return None

    def run_test(self, file_path: str, expected_text: Optional[str] = None) -> Dict[str, Any]:
        """Run a single test case"""
        logger.info(f"Testing file: {file_path}")
        
        # Check if file exists
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }

        # Process the file
        result = self.process_file(file_path)
        if not result:
            return {
                "success": False,
                "error": "Failed to process file"
            }

        # Validate result if expected text is provided
        if expected_text:
            result["expected_text"] = expected_text
            result["text_match"] = expected_text.lower() in result.get("text", "").lower()

        return result

    def run_test_suite(self, test_cases: Dict[str, str]) -> Dict[str, Any]:
        """Run multiple test cases"""
        results = {}
        for file_path, expected_text in test_cases.items():
            results[file_path] = self.run_test(file_path, expected_text)
        return results

def main():
    parser = argparse.ArgumentParser(description="OCR Testing Tool")
    parser.add_argument("--url", default="http://localhost:8080", help="Server URL")
    parser.add_argument("--file", help="Single file to test")
    parser.add_argument("--expected", help="Expected text in the file")
    parser.add_argument("--suite", help="JSON file containing test cases")
    parser.add_argument("--visual", action="store_true", help="Show visual results")
    
    args = parser.parse_args()
    
    tester = OCRTester(args.url)
    
    # Check server health first
    if not tester.test_health():
        logger.error("Server is not healthy. Please check if the server is running.")
        sys.exit(1)
    
    if args.file:
        # Single file test
        result = tester.run_test(args.file, args.expected)
        print(json.dumps(result, indent=2))
    elif args.suite:
        # Test suite
        with open(args.suite) as f:
            test_cases = json.load(f)
        results = tester.run_test_suite(test_cases)
        print(json.dumps(results, indent=2))
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 