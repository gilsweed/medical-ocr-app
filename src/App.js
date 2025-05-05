import React, { useState, useEffect } from 'react';
import Tesseract from 'tesseract.js';
import * as pdfjsLib from 'pdfjs-dist';
import './App.css';

function App() {
  useEffect(() => {
    // Set up PDF.js worker
    pdfjsLib.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js`;
  }, []);

  const [selectedFile, setSelectedFile] = useState(null);
  const [ocrText, setOcrText] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [errorMessage, setErrorMessage] = useState('');
  const [progress, setProgress] = useState(0);
  const [selectedLanguage, setSelectedLanguage] = useState('heb+eng');
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

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    console.log('Selected file:', file ? {
      name: file.name,
      type: file.type,
      size: file.size
    } : 'No file selected');
    
    setSelectedFile(file);
    setOcrText('');
    setCurrentPage(1);
    setTotalPages(1);
    setErrorMessage('');
    setProgress(0);
  };

  const convertPdfPageToImage = async (pdfDoc, pageNumber) => {
    console.log(`Converting PDF page ${pageNumber} to image...`);
    try {
      const page = await pdfDoc.getPage(pageNumber);
      const viewport = page.getViewport({ scale: 2.0 });
      
      const canvas = document.createElement('canvas');
      const context = canvas.getContext('2d');
      canvas.height = viewport.height;
      canvas.width = viewport.width;

      await page.render({
        canvasContext: context,
        viewport: viewport
      }).promise;

      console.log(`Successfully converted page ${pageNumber} to image`);
      return canvas.toDataURL('image/png');
    } catch (error) {
      console.error(`Error converting page ${pageNumber} to image:`, error);
      throw new Error(`Failed to convert PDF page ${pageNumber} to image: ${error.message}`);
    }
  };

  const performOCR = async () => {
    if (!selectedFile) {
      setErrorMessage('Please select a file first!');
      return;
    }

    setIsProcessing(true);
    setOcrText('');
    setErrorMessage('');
    setProgress(0);
    
    try {
      if (selectedFile.type === 'application/pdf') {
        console.log('Processing PDF file...');
        const fileReader = new FileReader();
        
        fileReader.onload = async function() {
          try {
            console.log('PDF file loaded, creating typed array...');
            const typedarray = new Uint8Array(this.result);
            console.log('Loading PDF document...');
            const pdfDoc = await pdfjsLib.getDocument(typedarray).promise;
            setTotalPages(pdfDoc.numPages);
            console.log(`PDF loaded successfully. Total pages: ${pdfDoc.numPages}`);
            
            let fullText = '';
            for (let pageNum = 1; pageNum <= pdfDoc.numPages; pageNum++) {
              setCurrentPage(pageNum);
              setProgress((pageNum - 1) / pdfDoc.numPages * 100);
              console.log(`Processing page ${pageNum}/${pdfDoc.numPages}`);
              const imageData = await convertPdfPageToImage(pdfDoc, pageNum);
              console.log(`Running OCR on page ${pageNum}...`);
              
              const result = await Tesseract.recognize(
                imageData,
                selectedLanguage,
                {
                  logger: m => {
                    if (m.status === 'recognizing text') {
                      setProgress((pageNum - 1 + m.progress) / pdfDoc.numPages * 100);
                    }
                  },
                  tessedit_pageseg_mode: '1', // Automatic page segmentation with OSD
                  preserve_interword_spaces: '1',
                  textord_heavy_nr: '1', // More aggressive noise removal
                  tessedit_char_blacklist: '[]{}', // Remove common misrecognized characters
                }
              );
              
              fullText += `=== Page ${pageNum} ===\n${result.data.text}\n\n`;
            }
            setOcrText(fullText);
            setProgress(100);
            console.log('PDF processing completed successfully');
          } catch (error) {
            console.error('Error processing PDF:', error);
            setErrorMessage(`Error processing PDF: ${error.message}`);
          }
        };

        fileReader.onerror = (error) => {
          console.error('FileReader error:', error);
          setErrorMessage(`Error reading PDF file: ${error.message}`);
        };
        
        console.log('Starting to read PDF file...');
        fileReader.readAsArrayBuffer(selectedFile);
      } else {
        // Handle image files
        console.log('Processing image file...');
        const result = await Tesseract.recognize(
          selectedFile,
          selectedLanguage,
          {
            logger: m => {
              if (m.status === 'recognizing text') {
                setProgress(m.progress * 100);
              }
            },
            tessedit_pageseg_mode: '1', // Automatic page segmentation with OSD
            preserve_interword_spaces: '1',
            textord_heavy_nr: '1', // More aggressive noise removal
            tessedit_char_blacklist: '[]{}', // Remove common misrecognized characters
          }
        );
        setOcrText(result.data.text);
        setProgress(100);
        console.log('Image processing completed successfully');
      }
    } catch (error) {
      console.error('Error during OCR:', error);
      setErrorMessage(`Error processing file: ${error.message}`);
    } finally {
      setIsProcessing(false);
    }
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
    } catch (error) {
      console.error('Error summarizing text:', error);
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
          <input
            type="file"
            onChange={handleFileChange}
            accept="image/*,.pdf"
            className="file-input"
          />
          <button 
            onClick={performOCR}
            disabled={!selectedFile || isProcessing}
            className="scan-button"
          >
            {isProcessing ? `Processing${selectedFile?.type === 'application/pdf' ? ` (Page ${currentPage}/${totalPages})` : ''}...` : 'Scan Document'}
          </button>
          {isProcessing && (
            <div className="progress-bar-container">
              <div 
                className="progress-bar" 
                style={{ width: `${progress}%` }}
              />
              <div className="progress-text">{Math.round(progress)}%</div>
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
