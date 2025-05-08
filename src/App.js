import React, { useState, useEffect } from 'react';
import Tesseract from 'tesseract.js';
import * as pdfjsLib from 'pdfjs-dist';
import './App.css';

function App() {
  useEffect(() => {
    // Set up PDF.js worker
    pdfjsLib.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js`;
  }, []);

  const [selectedFiles, setSelectedFiles] = useState([]);
  const [ocrText, setOcrText] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [errorMessage, setErrorMessage] = useState('');
  const [progress, setProgress] = useState(0);
  const [selectedLanguage, setSelectedLanguage] = useState('heb+eng');
  const [ocrQuality, setOcrQuality] = useState('high');
  const [summary, setSummary] = useState('');
  const [isSummarizing, setIsSummarizing] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  
  // Settings state
  const [summaryLanguage, setSummaryLanguage] = useState(() => {
    return localStorage.getItem('summaryLanguage') || 'hebrew';
  });
  const [customPrompt, setCustomPrompt] = useState(() => {
    return localStorage.getItem('customPrompt') || `ל/י כרופא/ה תעסוקתי/ת בכיר/ה.
	•	התבסס על המידע הקיים במסמכים רפואיים מצורפים (בעברית ובאנגלית).
	•	ערוך סיכום מקצועי, מובנה ותמציתי של המסמכים, הכולל אבחנות, טיפולים, מגבלות והשלכות על כשירות תעסוקתית.
	•	בסס את הסיכום על הנחיות וחוקים המופיעים בתקנון קרן הפנסיה העדכני של כלל
	•	כלול פרטים מזהים כגון שם המטופל, גיל ועיסוק, בהינתן שהמערכת מקומית ותואמת רגולציה.
	•	ציין אם חלק מהמידע חסר או בלתי קריא בעקבות זיהוי תווים אופטי (OCR).
	•	סכם את ההיסטוריה הרפואית לפי ציר זמן, ושלב את הסיפור הקליני, ההדמייתי והמעבדתי באופן ברור ומובנה.
	•	חלק את הסיכום לפסקאות לפי נושאים רפואיים. הימנע מהשערות לא מבוססות, והתמקד במסר תעסוקתי ברור עבור מקבל ההחלטה.
	•	וודא שהסיכום כתוב בשפה מקצועית, ברורה, רפואית ותעסוקתית כאחד

לבסוף המלץ האם מגיעה נכות לפי תקנון קרן הפנסיה כלל, חלקית או מלאה ולאיזה תקופה`;
  });

  // Save settings to localStorage
  useEffect(() => {
    localStorage.setItem('summaryLanguage', summaryLanguage);
    localStorage.setItem('customPrompt', customPrompt);
  }, [summaryLanguage, customPrompt]);

  const [currentFile, setCurrentFile] = useState('');
  const [currentFileIndex, setCurrentFileIndex] = useState(0);
  const [fileProgress, setFileProgress] = useState(0);
  const [overallProgress, setOverallProgress] = useState(0);
  const [processedFiles, setProcessedFiles] = useState(0);
  const [totalFiles, setTotalFiles] = useState(0);
  const [currentPageInfo, setCurrentPageInfo] = useState('');
  const [showSpinner, setShowSpinner] = useState(false);
  const [processedPages, setProcessedPages] = useState(0);
  const [globalItemIndex, setGlobalItemIndex] = useState(0);

  const handleFileChange = (event) => {
    const files = Array.from(event.target.files);
    if (files.length > 0) {
      console.log('Selected files:', files.map(file => ({
        name: file.name,
        type: file.type,
        size: file.size
      })));
      
      setSelectedFiles(files);
      setTotalFiles(files.length);
      setProcessedFiles(0);
      setOcrText('');
      setErrorMessage('');
      setOverallProgress(0);
      setFileProgress(0);
      setCurrentFile('');
      setCurrentFileIndex(0);
      setProcessedPages(0);
      setTotalPages(0);
    }
  };

  // Helper to downscale an image to max 1200px width/height
  const downscaleImage = async (imageBitmap, maxDim = 1200) => {
    let scale = Math.min(maxDim / imageBitmap.width, maxDim / imageBitmap.height, 1);
    const canvas = document.createElement('canvas');
    canvas.width = Math.round(imageBitmap.width * scale);
    canvas.height = Math.round(imageBitmap.height * scale);
    const ctx = canvas.getContext('2d');
    ctx.drawImage(imageBitmap, 0, 0, canvas.width, canvas.height);
    return canvas;
  };

  const convertPdfPageToImage = async (pdfDoc, pageNumber) => {
    try {
      const page = await pdfDoc.getPage(pageNumber);
      const viewport = page.getViewport({ scale: 1.0 }); // Lower scale for speed
      const canvas = document.createElement('canvas');
      const context = canvas.getContext('2d');
      canvas.height = viewport.height;
      canvas.width = viewport.width;
      await page.render({ canvasContext: context, viewport: viewport }).promise;
      return canvas.toDataURL('image/png');
    } catch (error) {
      throw new Error(`Failed to convert PDF page ${pageNumber} to image: ${error.message}`);
    }
  };

  // Add language detection function
  const detectLanguage = (text) => {
    const hebrewPattern = /[\u0590-\u05FF]/;
    const englishPattern = /[a-zA-Z]/;
    const hebrewCount = (text.match(/[\u0590-\u05FF]/g) || []).length;
    const englishCount = (text.match(/[a-zA-Z]/g) || []).length;
    
    if (hebrewCount > englishCount) return 'heb';
    if (englishCount > hebrewCount) return 'eng';
    return 'mixed';
  };

  // Add text preprocessing function
  const preprocessText = (text, detectedLang) => {
    // Basic cleaning
    text = text.replace(/[|•]/g, ''); // Remove common OCR artifacts
    
    if (detectedLang === 'heb' || detectedLang === 'mixed') {
      // Hebrew-specific cleaning
      text = text
        .replace(/([א-ת])\s+([א-ת])/g, '$1 $2') // Fix Hebrew spacing
        .replace(/\s*([.?!,])\s*/g, '$1 ') // Fix Hebrew punctuation
        .replace(/[\u0591-\u05C7]/g, '') // Remove Hebrew vowel points if they appear
        .replace(/[״"]/g, '"') // Normalize Hebrew quotation marks
        .replace(/[–—]/g, '-'); // Normalize dashes
    }

    if (detectedLang === 'eng' || detectedLang === 'mixed') {
      // English-specific cleaning
      text = text
        .replace(/([A-Za-z])\s+([A-Za-z])/g, '$1 $2') // Fix English spacing
        .replace(/(\d+)\s+([A-Za-z])/g, '$1 $2') // Fix number-word spacing
        .replace(/([A-Za-z])\s+(\d+)/g, '$1 $2') // Fix word-number spacing
        .replace(/['']/g, "'") // Normalize apostrophes
        .replace(/[""]/g, '"'); // Normalize quotation marks
    }

    return text.trim();
  };

  // Enhanced OCR configuration
  const getOcrConfig = (detectedLang) => ({
    logger: m => {
      if (m.status === 'recognizing text') {
        setFileProgress(Math.round(m.progress * 100));
      }
    },
    tessedit_pageseg_mode: detectedLang === 'mixed' ? '6' : '3',
    preserve_interword_spaces: '1',
    textord_heavy_nr: '1',
    tessedit_char_blacklist: '[]{}',
    tessedit_enable_doc_dict: '0',
    tessedit_write_images: '1',
    tessedit_ocr_engine_mode: '3',
    tessedit_create_hocr: '1',
    textord_force_make_prop_words: '1',
    tessedit_do_invert: '0',
    tessedit_enable_bigram_correction: '1',
    tessedit_enable_dict_correction: '1',
    textord_tabfind_find_tables: '0',
    textord_min_linesize: '2.5',
    tessedit_prefer_joined_chars: detectedLang === 'heb' ? '0' : '1',
    textord_space_size_is_variable: '1',
    textord_noise_certaintity: '1.5',
    language_model_penalty_non_freq_dict_word: '0.15',
    language_model_penalty_non_dict_word: '0.8'
  });

  const performOCR = async () => {
    if (selectedFiles.length === 0) {
      setErrorMessage('Please select at least one file!');
      return;
    }

    setIsProcessing(true);
    setOcrText('');
    setErrorMessage('');
    setOverallProgress(0);
    setFileProgress(0);
    setProcessedFiles(0);
    setCurrentFile('');
    setCurrentFileIndex(0);
    setProcessedPages(0);
    setTotalPages(0);
    setGlobalItemIndex(0);
    
    try {
      let fullText = '';
      let totalPagesCount = 0;
      // Calculate total pages
      for (const file of selectedFiles) {
        if (file.type === 'application/pdf') {
          const typedarray = await new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(new Uint8Array(reader.result));
            reader.onerror = reject;
            reader.readAsArrayBuffer(file);
          });
          const pdfDoc = await pdfjsLib.getDocument(typedarray).promise;
          totalPagesCount += pdfDoc.numPages;
        } else if (file.type.startsWith('image/')) {
          totalPagesCount += 1;
        }
      }
      setTotalPages(totalPagesCount);
      let processedPagesCount = 0;
      let globalIndex = 0;

      for (let fileIndex = 0; fileIndex < selectedFiles.length; fileIndex++) {
        const file = selectedFiles[fileIndex];
        setCurrentFile(file.name);
        setCurrentFileIndex(fileIndex + 1);
        setFileProgress(0);
        setProcessedFiles(fileIndex);

        if (file.type === 'application/pdf') {
          let typedarray;
          try {
            typedarray = await new Promise((resolve, reject) => {
              const reader = new FileReader();
              reader.onload = () => resolve(new Uint8Array(reader.result));
              reader.onerror = reject;
              reader.readAsArrayBuffer(file);
            });
            const pdfDoc = await pdfjsLib.getDocument(typedarray).promise;
            
            for (let pageNum = 1; pageNum <= pdfDoc.numPages; pageNum++) {
              setCurrentPageInfo(`Processing page ${pageNum}/${pdfDoc.numPages} of ${file.name}`);
              setShowSpinner(true);
              
              try {
                const imageData = await convertPdfPageToImage(pdfDoc, pageNum);
                const response = await fetch(imageData);
                const blob = await response.blob();
                
                // Create form data
                const formData = new FormData();
                formData.append('file', blob, `page_${pageNum}.png`);
                
                // Send to backend
                const ocrResponse = await fetch('http://localhost:5001/api/ocr', {
                  method: 'POST',
                  body: formData
                });
                
                if (!ocrResponse.ok) {
                  throw new Error(`OCR failed: ${ocrResponse.statusText}`);
                }
                
                const result = await ocrResponse.json();
                const processedText = preprocessText(result.text, result.language);
                
                fullText += processedText + '\n\n';
                processedPagesCount++;
                setProcessedPages(processedPagesCount);
                setOverallProgress(Math.round((processedPagesCount / totalPagesCount) * 100));
              } catch (error) {
                console.error(`Error processing page ${pageNum}:`, error);
                setErrorMessage(`Error processing page ${pageNum} of ${file.name}: ${error.message}`);
              }
            }
          } catch (error) {
            console.error('Error processing PDF:', error);
            setErrorMessage(`Error processing PDF ${file.name}: ${error.message}`);
          }
        } else if (file.type.startsWith('image/')) {
          setCurrentPageInfo(`Processing ${file.name}`);
          setShowSpinner(true);
          
          try {
            // Create form data
            const formData = new FormData();
            formData.append('file', file);
            
            // Send to backend
            const ocrResponse = await fetch('http://localhost:5001/api/ocr', {
              method: 'POST',
              body: formData
            });
            
            if (!ocrResponse.ok) {
              throw new Error(`OCR failed: ${ocrResponse.statusText}`);
            }
            
            const result = await ocrResponse.json();
            const processedText = preprocessText(result.text, result.language);
            
            fullText += processedText + '\n\n';
            processedPagesCount++;
            setProcessedPages(processedPagesCount);
            setOverallProgress(Math.round((processedPagesCount / totalPagesCount) * 100));
          } catch (error) {
            console.error('Error processing image:', error);
            setErrorMessage(`Error processing ${file.name}: ${error.message}`);
          }
        }
      }
      
      setOcrText(fullText.trim());
      setShowSpinner(false);
    } catch (error) {
      console.error('OCR process failed:', error);
      setErrorMessage(`OCR process failed: ${error.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  // Helper function for Otsu thresholding
  const otsuThreshold = (data) => {
    const histogram = new Array(256).fill(0);
    for (let i = 0; i < data.length; i += 4) {
      const value = Math.floor((data[i] + data[i + 1] + data[i + 2]) / 3);
      histogram[value]++;
    }
    // ... Otsu threshold calculation
    return 128; // Simplified for this example
  };

  // Helper function to apply threshold
  const applyThreshold = (data, threshold) => {
    for (let i = 0; i < data.length; i += 4) {
      const value = Math.floor((data[i] + data[i + 1] + data[i + 2]) / 3);
      const newValue = value > threshold ? 255 : 0;
      data[i] = data[i + 1] = data[i + 2] = newValue;
    }
  };

  // Helper function to estimate token count (roughly 4 chars per token)
  const estimateTokenCount = (text) => Math.ceil(text.length / 4);

  // Helper function to split text into chunks under a token limit
  const splitTextIntoChunks = (text, maxTokens = 8000) => {
    const approxChunkSize = maxTokens * 4; // chars
    const chunks = [];
    let start = 0;
    while (start < text.length) {
      let end = start + approxChunkSize;
      if (end > text.length) end = text.length;
      else {
        // Try to break at a paragraph or line
        let lastBreak = text.lastIndexOf('\n', end);
        if (lastBreak > start) end = lastBreak;
      }
      chunks.push(text.slice(start, end));
      start = end;
    }
    return chunks;
  };

  const handleSummarize = async () => {
    if (!ocrText) {
      setErrorMessage('Please scan a document first!');
      return;
    }

    setIsSummarizing(true);
    setSummary('');
    setErrorMessage('');

    try {
      // Construct the prompt based on settings
      let finalPrompt = customPrompt;
      if (summaryLanguage === 'hebrew') {
        finalPrompt += ' Please provide the summary in Hebrew.';
      } else if (summaryLanguage === 'english') {
        finalPrompt += ' Please provide the summary in English.';
      }

      const tokenCount = estimateTokenCount(ocrText);
      if (tokenCount > 8000) {
        // Automatic chunking
        setSummary('Text is long, summarizing in parts...');
        const chunks = splitTextIntoChunks(ocrText, 8000);
        let allSummaries = [];
        for (let i = 0; i < chunks.length; i++) {
          const chunk = chunks[i];
          setSummary(`Summarizing chunk ${i + 1} of ${chunks.length}...`);
          const response = await fetch('http://localhost:5001/api/summarize', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
              text: chunk,
              prompt: finalPrompt
            }),
          });
          const data = await response.json();
          if (!response.ok) {
            throw new Error(data.error || 'Failed to generate summary');
          }
          allSummaries.push(data.summary);
        }
        // Combine all chunk summaries
        setSummary(allSummaries.join('\n\n'));
      } else {
        // Normal summarization
        const response = await fetch('http://localhost:5001/api/summarize', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ 
            text: ocrText,
            prompt: finalPrompt
          }),
        });
        const data = await response.json();
        if (!response.ok) {
          throw new Error(data.error || 'Failed to generate summary');
        }
        setSummary(data.summary);
      }
    } catch (error) {
      setErrorMessage(`Error generating summary: ${error.message}`);
    } finally {
      setIsSummarizing(false);
    }
  };

  const SettingsMenu = () => (
    <div className="settings-menu">
      <h3>Summary Settings</h3>
      <div className="settings-group">
        <label>Summary Language:</label>
        <select 
          value={summaryLanguage} 
          onChange={(e) => setSummaryLanguage(e.target.value)}
          className="settings-select"
        >
          <option value="hebrew">Hebrew</option>
          <option value="english">English</option>
          <option value="auto">Auto-detect</option>
        </select>
      </div>
      <div className="settings-group">
        <label>Custom Prompt:</label>
        <textarea
          value={customPrompt}
          onChange={(e) => setCustomPrompt(e.target.value)}
          className="settings-textarea"
          rows={4}
          placeholder="Enter your custom prompt for summarization..."
        />
      </div>
    </div>
  );

  return (
    <div className="App">
      <header className="App-header">
        <div className="header-content">
          <h1>OCR Document Scanner</h1>
          <button 
            className="settings-button"
            onClick={() => setIsSettingsOpen(!isSettingsOpen)}
          >
            ⚙️ Settings
          </button>
        </div>
        {isSettingsOpen && <SettingsMenu />}
        <div className="upload-section">
          <select 
            value={selectedLanguage} 
            onChange={(e) => setSelectedLanguage(e.target.value)}
            className="language-select"
          >
            <option value="heb">Hebrew Only</option>
            <option value="heb+eng">Hebrew + English</option>
            <option value="eng">English Only</option>
          </select>
          <div className="file-input-container">
            <input
              type="file"
              onChange={handleFileChange}
              accept="image/*,.pdf"
              className="file-input"
              multiple
              id="file-input"
            />
            <label htmlFor="file-input" className="file-input-label">
              {selectedFiles.length > 0 
                ? `${selectedFiles.length} file(s) selected` 
                : 'Choose Files'}
            </label>
          </div>
          <button 
            onClick={performOCR}
            disabled={!selectedFiles.length || isProcessing}
            className="scan-button"
          >
            {isProcessing ? `Processing (${Math.min(processedFiles + 1, totalFiles)}/${totalFiles} files)...` : 'Scan Documents'}
          </button>
          {isProcessing && (
            <div className="progress-section">
              <div className="progress-bar-container">
                <div 
                  className="progress-bar" 
                  style={{ width: `${overallProgress}%` }}
                />
                <div className="progress-text">Overall Progress: {overallProgress}%</div>
              </div>
              <div className="progress-item-label">
                Processing item {globalItemIndex}/{totalPages}: {currentFile}
              </div>
              {currentFile && (
                <div className="file-progress">
                  <div className="file-progress-bar-container">
                    <div 
                      className="file-progress-bar" 
                      style={{ width: `${fileProgress}%` }}
                    />
                  </div>
                  {showSpinner && <div className="spinner" style={{marginTop: '10px'}}></div>}
                </div>
              )}
            </div>
          )}
        </div>
        {errorMessage && (
          <div className="error-message">
            {errorMessage}
          </div>
        )}
        {ocrText && (
          <div className="result-section">
            <h2>Scanned Text:</h2>
            <div className="text-result">
              {ocrText}
            </div>
            <button 
              onClick={handleSummarize}
              disabled={isSummarizing}
              className="summarize-button"
            >
              {isSummarizing ? 'Generating Summary...' : 'Summarize Text'}
            </button>
            {summary && (
              <div className="summary-section">
                <h3>Summary:</h3>
                <div className="summary-text">
                  {summary}
                </div>
              </div>
            )}
          </div>
        )}
      </header>
    </div>
  );
}

export default App;

// Add spinner CSS at the end of the file
const spinnerStyles = `
.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #4CAF50;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  animation: spin 1s linear infinite;
  margin: 0 auto;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
.page-info {
  text-align: center;
  margin-top: 8px;
  color: #888;
  font-size: 14px;
}
`;
const spinnerStyleSheet = document.createElement("style");
spinnerStyleSheet.innerText = spinnerStyles;
document.head.appendChild(spinnerStyleSheet);

// Add style for .progress-item-label
const progressItemLabelStyles = `
.progress-item-label {
  text-align: center;
  margin-top: 8px;
  color: #888;
  font-size: 15px;
  font-weight: bold;
}
`;
const progressItemLabelStyleSheet = document.createElement("style");
progressItemLabelStyleSheet.innerText = progressItemLabelStyles;
document.head.appendChild(progressItemLabelStyleSheet);
