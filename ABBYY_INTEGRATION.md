# ABBYY FineReader Engine 12 for Mac – Integration Reference

## 1. Project Requirements & Call Notes
- **Goal:** Integrate secure, offline, high-accuracy OCR for Hebrew and mixed Hebrew/English medical documents.
- **Priorities:**
  - Strict privacy and compliance (GDPR/HIPAA)
  - Local batch processing (no data leaves the machine)
  - Integration with Electron/Python backend
  - Automation and API/command-line support
  - Platform: macOS (M2/Apple Silicon), but open to Linux/Windows if needed

### Key Questions Asked to ABBYY
- Hebrew OCR quality and feature parity (Mac vs. Windows/Linux)
- Batch/automated processing and CLI/API support
- Local/offline processing, privacy, and data retention
- Licensing, activation, and compliance
- Integration options (Node.js, Python, command-line)
- Support, documentation, and pricing

## 2. ABBYY Responses & Offer
- **Hebrew OCR:** No limitations on Mac; full feature parity with Windows/Linux.
- **Batch Processing:** Supported via CommandLineInterface (C++ sample) and CLI utility. [Guided Tour Samples](https://help.abbyy.com/en-us/finereaderengine_mac/12/user_guide/guidedtour_samples/)
- **Integration:**
  - Use CLI tools from Node.js (`child_process`) or Python (`subprocess`).
  - No native Node.js module, but possible to wrap C++ API if needed.
- **Privacy & Compliance:**
  - All processing is fully local/offline; no data sent to ABBYY servers.
  - Only local page count in license manager; no telemetry.
  - File/data deletion is managed by your workflow.
- **Licensing:**
  - Offline activation via email (send activation request, receive code).
  - License manager supports usage logging and grace periods.
- **Support & Docs:**
  - Code samples in C++/Objective C (CLI, batch, API) in distributive pack.
  - Direct support via ABBYY rep or [Support Portal](https://support.abbyy.com/hc/en-us/requests/new)
- **Pricing:**
  - Yearly subscription, minimum 100k pages/year.
  - Enterprise pack, Hebrew Add-on: 3000 Euro/year (basic) or 1700 Euro/year (special discount, 100 days)
  - 90-day trial license provided.

## 3. Technical Details & Installation
- **Builds Provided:**
  - x86_64 (Intel Macs)
  - arm64 (Apple Silicon/M1/M2/M3)
- **System Requirements:**
  - macOS 10.15.x Catalina, 11.x Big Sur (should work on newer Apple Silicon)
  - 1GB+ RAM, 2GB+ disk space, 15MB per page for multi-page docs
- **Installation Steps:**
  1. Download the correct .dmg for your architecture (arm64 for M2).
  2. Mount the .dmg and copy:
     - `FREngine.framework` (required)
     - `Samples` (optional, recommended)
     - `Help` (optional)
     - `activateFREngine.command` (required)
  3. Run `activateFREngine.command` to activate your license (offline via email).
  4. For macOS Catalina, run the first call from a GUI session as the current user.

## 4. Release Notes Highlights (Release 5, Build 12.5.12.26025)
- **New 'Accurate' recognition mode** for best quality on poor scans/medical docs
- **Improved table and PDF processing** (mixed content, digital signatures, portfolios)
- **Machine learning barcode recognition**
- **NeoML integration** for advanced ML tasks
- **Embedded PDFium** for native PDF handling
- **Expanded API:** new methods for digital signatures, PDF portfolios, text layer quality
- **Export improvements:** PowerPoint, XLS, XPS
- **License management:** grace periods, volume refreshing
- **Deprecated:** old FastMode/BalancedMode, some CLI keys

## 5. Integration Plan (Next Steps)
- **Phase 1:** Download, install, and activate SDK (arm64 build for M2)
- **Phase 2:** Run CLI sample for batch OCR (test with Hebrew/mixed docs)
- **Phase 3:** Integrate CLI calls into backend (Node.js/Python)
- **Phase 4:** Replace Google Vision with ABBYY in app workflow
- **Phase 5:** Test, document, and ensure compliance

## 6. Useful Links
- [ABBYY FineReader Engine for Mac Documentation](https://help.abbyy.com/en-us/finereaderengine_mac/12/user_guide/)
- [Guided Tour Samples](https://help.abbyy.com/en-us/finereaderengine_mac/12/user_guide/guidedtour_samples/)
- [API Reference](https://help.abbyy.com/en-us/finereaderengine_mac/12/user_guide/apireference_engine_startlogging/)
- [Support Portal](https://support.abbyy.com/hc/en-us/requests/new)

## 7. Side-by-Side Comparison: ABBYY vs. Google Vision

It is safe to run a side-by-side comparison of ABBYY FineReader Engine and Google Vision OCR, as long as integrations are kept separate and resources are managed properly.

**Best Practices for Side-by-Side Comparison:**
- Keep ABBYY and Google Vision code paths separate in your backend.
- For each document, call both OCR engines independently (sequentially or in parallel).
- Store results from each engine separately (e.g., `abbyy_result.txt` and `google_result.txt`).
- Clean up any temporary files created by either engine.
- Monitor memory and CPU usage if running both engines on large batches.
- Only use Google Vision on non-sensitive test documents if privacy is a concern (since it sends data to the cloud).

**Summary Table:**
| Approach         | Conflict Risk | Notes                                      |
|------------------|--------------|--------------------------------------------|
| ABBYY only       | None         | Fully local, secure                        |
| Google only      | None         | Cloud-based, less private                  |
| Side-by-side     | Low          | Safe if code is separate and files managed |

**Note:**
Running both engines side-by-side will not cause conflicts as long as you:
- Clearly label and separate the results from each engine
- Use a config flag or UI toggle to control which engine(s) to use for each test
- Manage file access and cleanup properly

This approach allows you to compare accuracy, speed, and reliability before fully switching to ABBYY.

---

**This document is a living reference for ABBYY integration. Update as you proceed with installation, testing, and development.** 