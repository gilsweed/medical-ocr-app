// State management
const AppState = {
  selectedFiles: [],
  columnWidths: {
    left: 200,
    right: 200
  },
  currentPage: {},
  confidence: {},
  
  // State update methods
  updateSelectedFiles(files) {
    this.selectedFiles = files;
    this.notifyStateChange('selectedFiles');
  },
  
  updateColumnWidths(widths) {
    this.columnWidths = { ...this.columnWidths, ...widths };
    this.notifyStateChange('columnWidths');
  },
  
  updateCurrentPage(fileName, page) {
    this.currentPage[fileName] = page;
    this.notifyStateChange('currentPage');
  },
  
  updateConfidence(fileName, confidence) {
    this.confidence[fileName] = confidence;
    this.notifyStateChange('confidence');
  },
  
  // State change notification
  listeners: {},
  notifyStateChange(property) {
    if (this.listeners[property]) {
      this.listeners[property].forEach(callback => callback());
    }
  },
  
  // Subscribe to state changes
  subscribe(property, callback) {
    if (!this.listeners[property]) {
      this.listeners[property] = [];
    }
    this.listeners[property].push(callback);
  }
};

// --- Patient ID: Only allow up to 9 digits and show at top of summary panel ---
const patientIdInput = document.getElementById('patient-id');
const summaryPatientId = document.getElementById('summary-patient-id');

// --- Confidence bar dropdowns for Low/High Confidence ---
const lowConfidenceLabel = document.getElementById('low-confidence-label');
const highConfidenceLabel = document.getElementById('high-confidence-label');
const lowConfidenceDropdown = document.getElementById('low-confidence-dropdown');
const highConfidenceDropdown = document.getElementById('high-confidence-dropdown');

// --- File/Folder selection and trash icon logic ---
const selectFilesBtn = document.querySelector('.select-files-btn');
const trashBtn = document.querySelector('.trash-btn');

// Get column elements
const filePreviewsColumn = document.querySelector('.file-previews-column');
const ocrTextsColumn = document.querySelector('.ocr-texts-column');

function updatePatientIdDisplay() {
  const val = patientIdInput.value.replace(/\D/g, '').slice(0, 9);
  patientIdInput.value = val;
  if (summaryPatientId) {
    summaryPatientId.textContent = val ? `Patient ID: ${val}` : '';
    summaryPatientId.style.display = val ? 'block' : 'none';
  }
}

// Ensure patient ID is updated on load and input
patientIdInput.addEventListener('input', updatePatientIdDisplay);
window.addEventListener('DOMContentLoaded', updatePatientIdDisplay);

// --- Dropdowns with checkmark/highlight for selected option, open on click ---
function setupDropdown(btnId, listId, key, defaultValue) {
  const btn = document.getElementById(btnId);
  const list = document.getElementById(listId);
  let selected = localStorage.getItem(key) || defaultValue;

  function updateDropdown() {
    Array.from(list.children).forEach(child => {
      if (child.dataset && child.dataset[key]) {
        child.innerHTML = (child.dataset[key] === selected ? '✔ ' : '') + child.textContent.replace('✔ ', '');
        child.setAttribute('data-selected', child.dataset[key] === selected);
      }
    });
    btn.innerHTML = btn.innerHTML.replace(/:.*?▼/, `: ${selected} ▼`);
  }

  btn.addEventListener('click', (e) => {
    e.stopPropagation();
    list.style.display = list.style.display === 'flex' ? 'none' : 'flex';
    document.querySelectorAll('.menu-dropdown-content').forEach(l => {
      if (l !== list) l.style.display = 'none';
    });
  });

  Array.from(list.children).forEach(child => {
    if (child.dataset && child.dataset[key]) {
      child.onclick = (e) => {
        selected = child.dataset[key];
        localStorage.setItem(key, selected);
        updateDropdown();
        list.style.display = 'none';
      };
    }
  });

  updateDropdown();
}

// Function to update confidence counts and progress
function updateConfidenceCounts() {
  const lowConfidenceFiles = AppState.selectedFiles.filter(f => f.confidence === 'low');
  const highConfidenceFiles = AppState.selectedFiles.filter(f => f.confidence === 'high');
  const totalFiles = AppState.selectedFiles.length;
  const processedFiles = AppState.selectedFiles.filter(f => f.confidence !== '').length;
  const progressPercentage = totalFiles > 0 ? (processedFiles / totalFiles) * 100 : 0;

  // Update labels
  lowConfidenceLabel.textContent = `Low Confidence (${lowConfidenceFiles.length})`;
  highConfidenceLabel.textContent = `High Confidence (${highConfidenceFiles.length})`;

  // Update progress bar
  document.querySelector('.progress').style.width = `${progressPercentage}%`;
  document.querySelector('.progress-label').textContent = `${processedFiles}/${totalFiles} (${Math.round(progressPercentage)}%)`;
}

// Function to render file previews
function renderFilePreview(file) {
    const previewBlock = document.createElement('div');
    previewBlock.className = 'file-preview-block';
    previewBlock.id = `preview-${file.name.replace(/[^a-zA-Z0-9]/g, '')}`;
  
  // File header
    const originalHeader = document.createElement('div');
    originalHeader.className = 'file-original-header';
    const label = document.createElement('span');
  label.textContent = `${file.name} (Page 1 of ${file.pages || 1})`;
    originalHeader.appendChild(label);
    previewBlock.appendChild(originalHeader);
  
  // Preview content
    const originalContent = document.createElement('div');
    originalContent.className = 'file-original-content';
  
  // Create iframe for PDF preview
  if (file.name.toLowerCase().endsWith('.pdf')) {
    const iframe = document.createElement('iframe');
    iframe.src = `file://${file.path}`;
    iframe.style.width = '100%';
    iframe.style.height = '100%';
    iframe.style.border = 'none';
    iframe.style.background = '#181a1b';
    iframe.style.position = 'absolute';
    iframe.style.top = '0';
    iframe.style.left = '0';
    originalContent.appendChild(iframe);
  } else {
    // Create image element for image preview
    const img = document.createElement('img');
    img.src = `file://${file.path}`;
    img.style.width = '100%';
    img.style.height = '100%';
    img.style.objectFit = 'contain';
    img.style.position = 'absolute';
    img.style.top = '0';
    img.style.left = '0';
    originalContent.appendChild(img);
  }
  
    previewBlock.appendChild(originalContent);
  
  // Page navigation
    const pageNav = document.createElement('div');
    pageNav.className = 'file-page-nav';
    const prevBtn = document.createElement('button');
    prevBtn.className = 'page-nav prev';
    prevBtn.textContent = '<';
    prevBtn.disabled = true;
    const pageInfo = document.createElement('span');
  pageInfo.textContent = `Page 1 of ${file.pages || 1}`;
    pageInfo.className = 'file-page-info';
    const nextBtn = document.createElement('button');
    nextBtn.className = 'page-nav next';
    nextBtn.textContent = '>';
  nextBtn.disabled = (file.pages || 1) === 1;
    pageNav.appendChild(prevBtn);
    pageNav.appendChild(pageInfo);
    pageNav.appendChild(nextBtn);
    previewBlock.appendChild(pageNav);
  
  return previewBlock;
}

// Function to render OCR text block
function renderOCRBlock(file) {
    const ocrBlock = document.createElement('div');
    ocrBlock.className = 'ocr-text-block';
    const ocrLabel = document.createElement('div');
    ocrLabel.className = 'file-ocr-header';
    ocrLabel.textContent = `OCRed Text: ${file.name} (Page 1)`;
    ocrBlock.appendChild(ocrLabel);
    const ocrContent = document.createElement('div');
    ocrContent.className = 'file-ocr-content';
  ocrContent.innerHTML = `<div class="file-ocr-placeholder">[OCRed text for page 1 of ${file.name}]</div>`;
    ocrBlock.appendChild(ocrContent);
  return ocrBlock;
}

// Function to render all file rows
function renderAllFileRows(selectedFileName = null) {
  if (!filePreviewsColumn || !ocrTextsColumn) {
    console.error('Required column elements not found');
    return;
  }

  // Clear previous content
  filePreviewsColumn.innerHTML = '';
  ocrTextsColumn.innerHTML = '';
  
  // Sort files: lowest confidence first, then highest
  const sortedFiles = [
    ...AppState.selectedFiles.filter(f => f.confidence === 'low'),
    ...AppState.selectedFiles.filter(f => f.confidence === 'high'),
    ...AppState.selectedFiles.filter(f => f.confidence !== 'low' && f.confidence !== 'high')
  ];
  
  sortedFiles.forEach(file => {
    let currentPage = 1;
    let currentRotation = 0;
    
    // Add preview block
    const previewBlock = renderFilePreview(file);
    filePreviewsColumn.appendChild(previewBlock);
    
    // Add OCR block
    const ocrBlock = renderOCRBlock(file);
    ocrTextsColumn.appendChild(ocrBlock);
    
    // Scroll to selected file if specified
    if (selectedFileName && file.name === selectedFileName) {
      setTimeout(() => {
        previewBlock.scrollIntoView({ behavior: 'smooth', block: 'center' });
        ocrBlock.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }, 100);
    }
    
    // Add event listeners for navigation and rotation
    const label = previewBlock.querySelector('.file-original-header span');
    const originalContent = previewBlock.querySelector('.file-original-content');
    const ocrLabel = ocrBlock.querySelector('.file-ocr-header');
    const ocrContent = ocrBlock.querySelector('.file-ocr-content');
    const prevBtn = previewBlock.querySelector('.page-nav.prev');
    const nextBtn = previewBlock.querySelector('.page-nav.next');
    const pageInfo = previewBlock.querySelector('.file-page-info');
    
    if (label && originalContent && ocrLabel && ocrContent && prevBtn && nextBtn && pageInfo) {
    function updatePreview() {
        label.textContent = `${file.name} (Page ${currentPage} of ${file.pages || 1})`;
      ocrLabel.textContent = `OCRed Text: ${file.name} (Page ${currentPage})`;
        ocrContent.innerHTML = `<div class="file-ocr-placeholder">[OCRed text for page ${currentPage} of ${file.name}]</div>`;
      prevBtn.disabled = currentPage === 1;
        nextBtn.disabled = currentPage === (file.pages || 1);
        pageInfo.textContent = `Page ${currentPage} of ${file.pages || 1}`;
    }
      
    prevBtn.addEventListener('click', () => {
      if (currentPage > 1) {
        currentPage--;
        updatePreview();
      }
    });
      
    nextBtn.addEventListener('click', () => {
        if (currentPage < (file.pages || 1)) {
        currentPage++;
        updatePreview();
      }
    });
    }
  });

  updateConfidenceCounts();
  // Don't reset column widths after rendering
  window.setupDividerDrag(false);
}

function setupDividerDrag(forceReset) {
  const leftDivider = document.getElementById('left-divider');
  const rightDivider = document.getElementById('right-divider');
  const filePreviewsColumn = document.querySelector('.file-previews-column');
  const ocrTextsColumn = document.querySelector('.ocr-texts-column');
  const summaryPanel = document.querySelector('.summary-panel');
  const MIN_WIDTH = 200;
  const GAP = 8;
  let isLeftResizing = false;
  let isRightResizing = false;
  let startX = 0;
  let startLeftWidth = 0;

  // Function to manage pointer events in the preview column
  function setPreviewPointerEvents(value) {
    if (filePreviewsColumn) {
      Array.from(filePreviewsColumn.children).forEach(child => {
        child.style.pointerEvents = value;
      });
    }
  }

  // Set cursor style for dividers
  if (leftDivider && rightDivider) {
    leftDivider.style.cursor = 'ew-resize';
    rightDivider.style.cursor = 'ew-resize';
  }

  // Function to handle left divider drag start
  function startLeftDrag(e) {
    e.preventDefault();
    e.stopPropagation();
    isLeftResizing = true;
    startX = e.clientX;
    startLeftWidth = filePreviewsColumn.offsetWidth;
    document.body.style.cursor = 'col-resize';
    // Disable pointer events in preview column during drag
    setPreviewPointerEvents('none');
  }

  // Add mousedown listener to the divider
  leftDivider.addEventListener('mousedown', startLeftDrag);

  // Right divider logic
  rightDivider.addEventListener('mousedown', function(e) {
    e.preventDefault();
    isRightResizing = true;
    document.body.style.cursor = 'col-resize';
  });

  // Handle mouse movement for both dividers
  document.addEventListener('mousemove', function(e) {
    if (!isLeftResizing && !isRightResizing) return;

    const container = document.querySelector('.main-content');
    const containerWidth = container.offsetWidth;
    const leftDividerWidth = leftDivider.offsetWidth;
    const rightDividerWidth = rightDivider.offsetWidth;

    if (isLeftResizing) {
      // Calculate the delta from the start position
      const deltaX = e.clientX - startX;
      
      // Calculate the absolute maximum width for the left column
      const absoluteMaxLeftWidth = containerWidth - (MIN_WIDTH + GAP + rightDividerWidth + summaryPanel.offsetWidth);
      
      // Calculate the new width based on the start width and delta
      const newLeftWidth = Math.max(MIN_WIDTH, Math.min(
        startLeftWidth + deltaX,
        absoluteMaxLeftWidth
      ));
      
      // Update the left column
      AppState.updateColumnWidths({ left: newLeftWidth });
      filePreviewsColumn.style.width = `${newLeftWidth}px`;
      filePreviewsColumn.style.flex = `0 0 ${newLeftWidth}px`;
      
      // Ensure the right column stays in place
      const rightColumnWidth = summaryPanel.offsetWidth;
      const rightColumnPosition = containerWidth - rightColumnWidth;
      summaryPanel.style.right = '0';
      summaryPanel.style.position = 'absolute';
    }

    if (isRightResizing) {
      // Calculate the minimum allowed position for the right divider
      const minRightPosition = filePreviewsColumn.offsetWidth + MIN_WIDTH + GAP;
      // Ensure the right column stays within container bounds by adding a small buffer
      const maxRightPosition = containerWidth - MIN_WIDTH - 2;
      
      // Calculate the new position based on mouse position
      const mouseX = e.clientX - container.getBoundingClientRect().left;
      const newRightPosition = Math.max(minRightPosition, Math.min(mouseX, maxRightPosition));
      
      // Calculate the new width for the right column
      const newRightWidth = containerWidth - newRightPosition - rightDividerWidth;
      
      // Update the right column
      AppState.updateColumnWidths({ right: newRightWidth });
      summaryPanel.style.width = `${newRightWidth}px`;
      summaryPanel.style.flex = `0 0 ${newRightWidth}px`;
      
      // Ensure the right column stays within bounds
      summaryPanel.style.right = '0';
      summaryPanel.style.position = 'absolute';
    }
  });

  // Handle mouse up for both dividers
  document.addEventListener('mouseup', function() {
    if (isLeftResizing || isRightResizing) {
      isLeftResizing = false;
      isRightResizing = false;
      document.body.style.cursor = '';
      
      // Reset any absolute positioning
      if (summaryPanel) {
        summaryPanel.style.position = '';
        summaryPanel.style.right = '';
      }
      
      // Re-enable pointer events in preview column
      setPreviewPointerEvents('auto');
    }
  });

  // Handle mouse leave
  document.addEventListener('mouseleave', function() {
    if (isLeftResizing || isRightResizing) {
      isLeftResizing = false;
      isRightResizing = false;
      document.body.style.cursor = '';
      
      // Reset any absolute positioning
      if (summaryPanel) {
        summaryPanel.style.position = '';
        summaryPanel.style.right = '';
      }
      
      // Re-enable pointer events in preview column
      setPreviewPointerEvents('auto');
    }
  });

  function initializeLayout() {
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
      // Set initial widths from state
      const { left, right } = AppState.columnWidths;
      filePreviewsColumn.style.width = `${left}px`;
      filePreviewsColumn.style.flex = `0 0 ${left}px`;
      summaryPanel.style.width = `${right}px`;
      summaryPanel.style.flex = `0 0 ${right}px`;
      
      // Ensure middle column takes remaining space
      ocrTextsColumn.style.flex = '1 1 auto';
      ocrTextsColumn.style.minWidth = `${MIN_WIDTH}px`;
    }
  }
  
  // Subscribe to column width changes
  AppState.subscribe('columnWidths', () => {
    const { left, right } = AppState.columnWidths;
    if (filePreviewsColumn) {
      filePreviewsColumn.style.width = `${left}px`;
      filePreviewsColumn.style.flex = `0 0 ${left}px`;
    }
    if (summaryPanel) {
      summaryPanel.style.width = `${right}px`;
      summaryPanel.style.flex = `0 0 ${right}px`;
    }
  });
  
  window.addEventListener('resize', initializeLayout);
  if (forceReset) initializeLayout();
}

function resetColumnWidthsToDefault() {
  const mainContent = document.querySelector('.main-content');
  if (!mainContent) return;
  
  // Calculate equal widths based on container width
  const containerWidth = mainContent.offsetWidth;
  const dividerWidth = 8; // Width of each divider
  const totalDividersWidth = dividerWidth * 2; // Two dividers
  const availableWidth = containerWidth - totalDividersWidth;
  const equalWidth = Math.floor(availableWidth / 3);
  
  // Set equal widths for left and right columns
  AppState.columnWidths.left = equalWidth;
  AppState.columnWidths.right = equalWidth;
  
  // Update the grid template
  mainContent.style.gridTemplateColumns = `${equalWidth}px 8px minmax(200px, 1fr) 8px ${equalWidth}px`;
}

// Make setupDividerDrag available globally
window.setupDividerDrag = setupDividerDrag;

// Initialize layout when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  resetColumnWidthsToDefault();
  setupDividerDrag(true);
});

// Initialize button state
document.addEventListener('DOMContentLoaded', () => {
  console.log('DOM loaded, initializing buttons');
  if (selectFilesBtn) {
    console.log('Select files button found');
    selectFilesBtn.disabled = false;
    selectFilesBtn.style.cursor = 'pointer';
  } else {
    console.error('Select files button not found');
  }
});

// File selection handler
if (selectFilesBtn) {
  console.log('Setting up select files button click handler');
  selectFilesBtn.onclick = async () => {
    console.log('Select files button clicked');
    try {
      if (!window.electron) {
        console.error('Electron API not available');
        return;
      }
      
      console.log('Electron API available, calling selectFiles');
      // Open file selection dialog
      const result = await window.electron.selectFiles();
      console.log('File selection result:', result);
      
      // Check if files were selected
      if (result && result.filePaths && result.filePaths.length > 0) {
        console.log('Files selected:', result.filePaths);
        // Process selected files
        const selectedFiles = result.filePaths.map(path => {
          const fileName = path.split('/').pop();
          return {
            name: fileName,
            path: path,
            confidence: '', // Will be set after OCR processing
            pages: 1 // Will be updated for PDFs
          };
        });
        
        // Update UI
        AppState.updateSelectedFiles(selectedFiles);
        renderAllFileRows();
        updateConfidenceCounts();
        resetColumnWidthsToDefault();
        window.setupDividerDrag(true);
      }
    } catch (error) {
      console.error('Error selecting files:', error);
      // Show error in a more user-friendly way
      const errorMessage = document.createElement('div');
      errorMessage.className = 'error-message';
      errorMessage.textContent = `Error selecting files: ${error.message}`;
      errorMessage.style.position = 'fixed';
      errorMessage.style.top = '20px';
      errorMessage.style.left = '50%';
      errorMessage.style.transform = 'translateX(-50%)';
      errorMessage.style.backgroundColor = '#ff4444';
      errorMessage.style.color = 'white';
      errorMessage.style.padding = '10px 20px';
      errorMessage.style.borderRadius = '5px';
      errorMessage.style.zIndex = '1000';
      
      document.body.appendChild(errorMessage);
      
      // Remove error message after 3 seconds
    setTimeout(() => {
        errorMessage.remove();
      }, 3000);
    }
  };
  } else {
  console.error('Select files button not found during setup');
}

// Trash button handler
trashBtn.addEventListener('click', () => {
  // Clear all file previews and reset state
  AppState.updateSelectedFiles([]);
  filePreviewsColumn.innerHTML = '';
  ocrTextsColumn.innerHTML = '';
  updateConfidenceCounts();
  resetColumnWidthsToDefault();
  window.setupDividerDrag(true);
});

// Initialize dropdowns
window.addEventListener('DOMContentLoaded', () => {
  setupDropdown('prompt-template-btn', 'prompt-template-list', 'template', 'Template 1');
  setupDropdown('export-btn', 'export-list', 'export', 'pdf');
  setupDropdown('ocr-engine-btn', 'ocr-engine-list', 'ocr', 'ABBYY');
  });

// Update summary block with formatted date
function updateSummaryBlock() {
  const now = new Date();
  const formattedDate = now.toLocaleDateString('en-GB', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  }).replace(/\//g, '-');
  
  const summaryTextarea = document.querySelector('.summary-textarea');
  
  if (summaryTextarea) {
    summaryTextarea.value = formattedDate;
  }
}

// Call setupDividerDrag and updateSummaryBlock after DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  setupDividerDrag();
  updateSummaryBlock();
});
