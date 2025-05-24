# Next Steps Roadmap (Purpose-Driven)

**Main Purpose:**  
This application is designed for secure, offline processing of medical documents. It performs OCR (Hebrew/English), extracts text, and summarizes content using a local GPT model via Ollama. Privacy, compliance, and reliability are top priorities.

---

## 1. Core Secure Processing Features
- **File Input Improvements**
  - Multi-file and folder drag-and-drop (with recursive file finding)
  - File type validation and user-friendly error messages
  - Ensure all file handling is strictly local and secure
  - **Add drag-and-drop support for files and folders**
- **Batch Processing**
  - Process multiple medical documents at once, with clear progress and error reporting
  - Guarantee no data leaves the local machine

---

## 2. Medical OCR & Summarization
- **OCR Engine Integration**
  - Robust Hebrew/English OCR for medical documents (using Tesseract or similar)
  - Easy engine swapping (e.g., ABBYY, Tesseract)
- **Summarization Engine**
  - Local model via Ollama for secure, offline summarization
  - Accepts `prompt.txt` and `prompt-manual.pdf` as input for custom instructions
  - Generates `summary.txt` for each document, including:
    - OCR reliability report
    - Medical insights and summary

---

## 3. Feedback Learning
- **User Feedback Integration**
  - Accepts `feedback.txt` to learn user's preferred summarization styles
  - Learning data stays within the main folder by default
  - Option to share feedback data only if user enables sharing in settings

---

## 4. User Experience & Trust
- **Status & Feedback**
  - Detailed status indicators for each processing step (input, OCR, summarization)
  - Clear notifications and logs for user confidence
- **Manual Review**
  - "Open File" button for manual inspection if OCR or summary quality is low
- **UI Polish**
  - Modern, accessible interface with clear privacy/compliance messaging

---

## 5. Security, Privacy & Compliance
- **Encryption**
  - Encrypt files at rest and in transit within the app
- **Compliance**
  - Add features and documentation for GDPR/HIPAA compliance
  - Ensure all processing is local and no data is sent to the cloud

---

## 6. Advanced Features & Flexibility
- **Export Options**
  - Export OCR and summary results to secure formats (Word, PDF, etc.)
- **Settings/Preferences**
  - Let users configure OCR languages, output formats, summarization options, and feedback sharing
- **History/Logs**
  - Keep a secure, local history of processed files and results

---

## 7. Documentation, Support & Testing
- **Expand Documentation**
  - User guides, compliance documentation, troubleshooting
- **Automated Tests**
  - Ensure reliability and security with test coverage for all core features

---

**Prioritization Table**

| Step | Area                        | Why First?                                 |
|------|-----------------------------|--------------------------------------------|
| 1    | Secure File Input/Batch     | Foundation for all secure processing       |
| 2    | OCR & Summarization         | Delivers main value: text extraction/summ. |
| 3    | Feedback Learning           | Improves summary quality, stays local      |
| 4    | UX & Trust                  | User confidence, transparency              |
| 5    | Security/Compliance         | Protects sensitive medical data            |
| 6    | Advanced Features           | Flexibility for power users                |
| 7    | Docs/Testing                | Maintainability, support, compliance       |

**Questions to Guide Prioritization:**
- What is your top priority: new features, polish, performance, or something else?
- Are there any pain points or "wishes" you have for the app?
- Do you want to focus on user experience, technical improvements, or both?
- Is there a specific workflow or user story you want to improve?

---

## ABBYY Call Notes (May 2025)

**Introduction & Requirements Stated:**
- Developing a secure, offline desktop application for automated OCR processing of medical documents, with a strong focus on high-accuracy recognition of Hebrew and mixed Hebrew/English text.
- Top priorities: strict privacy, compliance (GDPR/HIPAA), local batch processing, and integration options for automation.
- Sought ABBYY solutions for macOS, with clarification on local processing, privacy guarantees, and integration options.

**Key Questions Asked:**
1. Confirm Hebrew OCR Quality
   - Is FineReader Engine SDK for Mac (or Linux/Windows) capable of high-accuracy OCR for Hebrew and mixed Hebrew/English documents (PDFs/images)?
   - Any known limitations or language model differences on Mac vs. Linux/Windows?
2. Batch & Automated Processing
   - Does the SDK support fully automated, batch OCR (multiple files/folders at once)?
   - Is there a command-line interface or API for integration?
3. Local/Offline Processing & Privacy
   - Can all OCR processing be performed 100% locally/offline, with no data sent to ABBYY servers?
   - Any telemetry features, and can they be disabled?
   - Any cloud fallback or dependency?
4. Data Handling, Security & Compliance
   - Are files/results ever retained, cached, or logged by the SDK or ABBYY service?
   - Can you guarantee files are deleted immediately after processing and not used for training/analytics?
   - Special compliance options/documentation for medical/legal (GDPR/HIPAA) use cases?
5. Platform & Integration
   - Is the Mac SDK fully supported and up to date, or is Linux/Windows recommended for production?
   - Can the SDK be triggered from other applications (command-line, AppleScript, Automator, API)?
   - Code samples/documentation for Mac integration?
6. Licensing & Support
   - Licensing options for medical/legal use?
   - Trial version for SDK on Mac?
   - Support for Mac users (vs. Linux/Windows)?

**Short Call Goals Summary:**
- Confirm high-accuracy Hebrew OCR (Mac vs. Linux/Windows)
- Ensure full local/offline batch processing (no cloud, no data retention)
- Clarify integration options (API, command-line, scripting)
- Verify strict privacy/compliance (GDPR/HIPAA, no analytics/training)
- Ask about Mac SDK support, limitations, and sample code
- Discuss licensing, trial, and support for medical/legal use

**ABBYY Responses & Offer:**
- FineReader Engine 12 for Mac is available for testing, with a fully functional 90-day (minimum) trial.
- Tech requirements: https://help.abbyy.com/en-us/finereaderengine_mac/12/user_guide/specifications_systemrequirements/
- SDK is a set of low-level libraries, detailed manual, and code samples.
- Code samples available in C++ and Objective C, compiled and open source: https://help.abbyy.com/en-us/finereaderengine_mac/12/user_guide/guidedtour_samples/
- Batch processing, command-line, and API integration are supported.
- Hebrew OCR works well on Mac (tested and confirmed).
- Pricing: Yearly subscription based on page volume. Minimum SKU: 100k pages/year.
  - Enterprise pack, 100k ppy, Hebrew Add-on: 3000 Euro/year (basic) or 1700 Euro/year (special discount, valid 100 days)
  - Enterprise package includes developer toolkit (1 network license for 3 concurrent users, 10K PPM limit) and runtime license of certain volume.
- Special offer valid for 100 days.
- Support and code samples are more extensive for Linux/Windows, but Mac is supported.

**Next Steps:**
- Begin product testing with trial SDK.
- Review code samples and documentation.
- Evaluate integration and compliance for your use case.
- Follow up with ABBYY for any additional questions or clarifications. 