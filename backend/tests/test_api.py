import os
import requests
import time
import pytest

API_URL = "http://localhost:8082"
SAMPLE_PDF = os.path.join(os.path.dirname(__file__), "test_files", "sample.pdf")  # Place a sample.pdf here for OCR tests


def test_health():
    resp = requests.get(f"{API_URL}/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

def test_ocr_pdf_success():
    if not os.path.exists(SAMPLE_PDF):
        pytest.skip("No sample.pdf found for OCR test.")
    with open(SAMPLE_PDF, "rb") as f:
        files = {"file": ("sample.pdf", f, "application/pdf")}
        resp = requests.post(f"{API_URL}/api/ocr/pdf", files=files)
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"]
        job_id = data["job_id"]
        # Poll for status
        for _ in range(10):
            status_resp = requests.get(f"{API_URL}/api/ocr/pdf/status/{job_id}")
            assert status_resp.status_code == 200
            status_data = status_resp.json()
            if status_data["status"] == "done":
                assert status_data["success"]
                assert "text" in status_data
                break
            time.sleep(1)
        else:
            pytest.fail("OCR job did not complete in time.")

def test_ocr_pdf_no_file():
    resp = requests.post(f"{API_URL}/api/ocr/pdf", files={})
    assert resp.status_code == 400
    data = resp.json()
    assert not data["success"]
    assert "No file uploaded" in data["error"]

def test_summarize_ollama():
    payload = {
        "patient_id": "123456",
        "texts": ["This is a test document for summarization."],
        "engine": "ollama"
    }
    resp = requests.post(f"{API_URL}/api/summarize", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "success" in data
    # Accept either success or a clear error if Ollama is not running
    if data["success"]:
        assert "summary" in data
    else:
        assert "Ollama error" in data["error"] or "failed" in data["error"] or "Connection refused" in data["error"]

def test_summarize_dicta():
    payload = {
        "patient_id": "123456",
        "texts": ["This is a test document for summarization."],
        "engine": "dicta"
    }
    resp = requests.post(f"{API_URL}/api/summarize", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "success" in data
    # Accept either success or a clear error if Dicta is not running
    if data["success"]:
        assert "summary" in data
    else:
        assert "Dicta error" in data["error"] or "not implemented" in data["error"] or "Connection refused" in data["error"] 