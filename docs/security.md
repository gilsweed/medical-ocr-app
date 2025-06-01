# Security & Privacy Guide: OCR Scanner Electron App

## Overview

This document outlines the security and privacy best practices for the OCR Scanner Electron App, including local and cloud workflows, data handling, and compliance considerations.

---

## Security Principles
- **Least Privilege:** Only necessary permissions are granted to services and users.
- **Data Minimization:** Only required data is collected and processed.
- **Encryption:** All sensitive data is encrypted in transit and at rest.
- **Separation of Concerns:** Backend, frontend, and cloud services are modular and isolated.
- **Auditability:** All actions are logged for traceability.

---

## Local Workflow Security
- All OCR processing can be performed locally (no data leaves the user's machine).
- Temporary files are deleted after processing.
- No user data is stored beyond the session unless explicitly exported.
- Tesseract OCR is run in a sandboxed environment.

---

## Cloud Workflow Security (Google Cloud Vision)
- Files are uploaded to a private, access-controlled Google Cloud Storage bucket.
- Service accounts are used with the minimum required permissions (see [README.md](../README.md#cloud-storage-setup-for-pdftiff-ocr)).
- Files are deleted from the bucket immediately after OCR and result download.
- All communication with Google Cloud is encrypted (HTTPS).
- No OCR results are stored in the cloud; results are downloaded and saved locally only.
- Bucket settings:
  - Public access prevention: Enabled
  - Uniform access control: Enabled
  - Object versioning: Disabled
  - Retention: Disabled
  - Encryption: Google-managed (default)

---

## Compliance
- Designed for GDPR and HIPAA compliance.
- No personal data is stored in the cloud.
- All cloud files are deleted after use.
- Logs do not contain sensitive data.

---

## Best Practices
- Regularly review service account permissions.
- Monitor bucket access logs in Google Cloud Console.
- Keep dependencies up to date.
- Use strong passwords and 2FA for all cloud accounts.
- Regularly audit and update documentation.

---

## More Resources
- [README.md](../README.md): Project overview, install/build/run instructions
- [TROUBLESHOOTING.md](../TROUBLESHOOTING.md): Troubleshooting guide
- [CHANGELOG.md](../CHANGELOG.md): Version history
- [docs/DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md): Roadmap and feature map
- [docs/api.md](api.md): API documentation
- [docs/development.md](development.md): Development workflow and best practices
- [docs/project_history.md](project_history.md): Project history and technical improvements

---

## 1. Local OCR Processing (Recommended for Maximum Privacy)
- **All files are processed locally on your machine.**
- **No data leaves your computer** unless you explicitly choose to use a cloud service.
- **File-based workflow:**
  - Original files remain on disk and are never uploaded.
  - OCR results are saved locally and can be reviewed or deleted at any time.
- **Best for:**
  - Medical, legal, or highly sensitive documents (GDPR/HIPAA compliance).
  - Users who require full control over their data.

### Best Practices
- Store files in secure, access-controlled folders.
- Use encrypted disk volumes (e.g., FileVault on macOS).
- Regularly update Tesseract and all dependencies.
- Review and clear temporary files after processing.

---

## 2. Cloud OCR Processing (Google Cloud Vision API)
- **All communication with Google Cloud is encrypted (HTTPS/TLS).**
- **Files can be sent directly in API requests (base64-encoded),** avoiding cloud storage for small files.
- **For large/batch files:**
  - Files are uploaded to a private, access-controlled Google Cloud Storage bucket.
  - All files are encrypted at rest (AES256 by default; Customer-Managed Encryption Keys available).
  - Files are deleted immediately after OCR processing to minimize exposure.
- **Service accounts and IAM roles** restrict access to only the necessary resources.

### Best Practices
- Use direct API calls for small files to avoid cloud storage.
- For batch/large files, automate deletion from Cloud Storage after processing.
- Restrict service account permissions to the minimum required.
- Never share service account keys; store them securely.
- Monitor and audit access to your Google Cloud project.
- Opt out of data being used for training/analytics if possible.

---

## Cloud Storage Bucket Setup for PDF/TIFF OCR

To enable batch/async OCR for PDFs and TIFFs with Google Cloud Vision API, a private Google Cloud Storage bucket must be created with the following settings:
- **Location:** Multi-region (e.g., `us`)
- **Storage class:** Standard
- **Public access prevention:** Enabled
- **Access control:** Uniform
- **Object versioning:** Disabled
- **Retention:** Disabled
- **Encryption:** Google-managed encryption key (default)

This ensures all files are stored securely and privately, and supports compliance with privacy regulations. The bucket is used to upload documents for OCR and to store results temporarily before deletion.

---

## 3. General Security Recommendations
- **Always use the latest version** of the app and all dependencies.
- **Encrypt your device** and use strong passwords.
- **Limit access** to sensitive files and folders.
- **Regularly review logs** and audit trails (if using cloud services).
- **Comply with all relevant regulations** (GDPR, HIPAA, etc.) for your use case.

---

## 4. Data Retention & Deletion
- **Local:** You control all files; delete originals and OCR results as needed.
- **Cloud:** Files are deleted from cloud storage immediately after processing. No files are retained long-term.
- **No data is used for training or analytics** unless you explicitly opt in.

---

## 5. Compliance
- The app is designed to support workflows that comply with GDPR, HIPAA, and other privacy regulations.
- For maximum compliance, use local OCR processing.
- When using cloud OCR, review the provider's privacy policy and data processing agreements.

---

## 6. Cloud Compliance Agreements (DPA/BAA)
To ensure GDPR and HIPAA compliance when using cloud OCR services, you must sign a Data Processing Agreement (DPA) and, for medical data, a Business Associate Agreement (BAA) with your provider before processing real or sensitive data.

**Status:** The Google Cloud Data Processing Addendum (DPA) has been reviewed and accepted for this account, as required for GDPR compliance.

### How to Sign:
- **Google Cloud Platform (GCP):**
  - DPA: Accept electronically in the Cloud Console ("Account Settings" → "Data Processing and Security Terms").
  - BAA: Request via the Cloud Console or contact Google Cloud support.
  - Time: Minutes to 2 days.
- **ABBYY Cloud OCR SDK:**
  - DPA/BAA: Request from ABBYY sales/support, review, and sign.
  - Time: 1–5 business days.
- **Microsoft Azure / Amazon AWS:**
  - DPA/BAA: Accept electronically in the portal.
  - Time: Minutes to 2 days.

### When to Sign:
- You can develop and test with non-sensitive data before signing.
- **You must have a signed DPA/BAA before processing real, sensitive, or production data.**

### Best Practice Workflow:
1. Develop and test with sample data.
2. Initiate and sign DPA/BAA before production.
3. Document the agreement and compliance steps.
4. Begin processing real data only after compliance is confirmed.

### Links:
- [Google Cloud DPA/BAA Info](https://cloud.google.com/terms/data-processing-terms)
- [ABBYY Cloud OCR SDK Privacy](https://www.ocrsdk.com/privacy/)
- [AWS Data Privacy](https://aws.amazon.com/compliance/data-privacy-faq/)
- [Azure Data Privacy](https://azure.microsoft.com/en-us/support/legal/)

---

## 7. Summary Table
| Workflow                | Data Leaves Device | Encryption in Transit | Encryption at Rest | File Retention | Best For                |
|-------------------------|-------------------|----------------------|--------------------|---------------|-------------------------|
| Local OCR (Tesseract)   | No                | N/A                  | Device-level       | User-controlled| Max privacy/compliance  |
| Cloud OCR (Vision API)  | Yes               | Yes (HTTPS/TLS)      | Yes (AES256/CMEK)  | Deleted after  | High accuracy, batch    |

---

## 8. Contact & Support
For questions about security or privacy, see [README.md](../README.md), [TROUBLESHOOTING.md](../TROUBLESHOOTING.md), or contact the project maintainer. 