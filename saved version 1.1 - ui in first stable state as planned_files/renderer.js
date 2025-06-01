// --- Patient ID: Only allow up to 9 digits and show at top of summary panel ---
const patientIdInput = document.getElementById('patient-id');
const summaryPatientId = document.getElementById('summary-patient-id');
function updatePatientIdDisplay() {
  const val = patientIdInput.value.replace(/\D/g, '').slice(0, 9);
  patientIdInput.value = val;
  summaryPatientId.textContent = val ? `Patient ID: ${val}` : '';
}
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
window.addEventListener('DOMContentLoaded', () => {
  setupDropdown('prompt-template-btn', 'prompt-template-list', 'template', 'Template 1');
  setupDropdown('export-btn', 'export-list', 'export', 'pdf');
  setupDropdown('ocr-engine-btn', 'ocr-engine-list', 'ocr', 'ABBYY');
  document.body.addEventListener('click', () => {
    document.querySelectorAll('.menu-dropdown-content').forEach(l => l.style.display = 'none');
  });

  // --- Knowledge Files button dropdown logic ---
  const knowledgeBtn = document.getElementById('knowledge-btn');
  if (knowledgeBtn) {
    const knowledgeDropdown = knowledgeBtn.nextElementSibling;
    knowledgeBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      // Toggle this dropdown
      if (knowledgeDropdown.style.display === 'flex') {
        knowledgeDropdown.style.display = 'none';
      } else {
        document.querySelectorAll('.menu-dropdown-content').forEach(l => {
          if (l !== knowledgeDropdown) l.style.display = 'none';
        });
        knowledgeDropdown.style.display = 'flex';
      }
    });
  }
});

// --- Demo files for confidence bar dropdowns ---
const demoFiles = [
  { name: 'file3.pdf', confidence: 'high', pages: 2 },
  { name: 'file4.pdf', confidence: 'high', pages: 1 },
  { name: 'file5.pdf', confidence: 'high', pages: 1 },
  { name: 'file6.pdf', confidence: 'high', pages: 1 },
  { name: 'file7.pdf', confidence: 'high', pages: 1 },
  { name: 'file1.pdf', confidence: 'low', pages: 2 },
  { name: 'file2.pdf', confidence: 'low', pages: 1 },
  { name: 'file8.pdf', confidence: '', pages: 3 }
];

// --- Confidence bar dropdowns for Low/High Confidence ---
const lowConfidenceLabel = document.getElementById('low-confidence-label');
const highConfidenceLabel = document.getElementById('high-confidence-label');
const lowConfidenceDropdown = document.getElementById('low-confidence-dropdown');
const highConfidenceDropdown = document.getElementById('high-confidence-dropdown');

function renderConfidenceDropdown(confidence, dropdown) {
  dropdown.innerHTML = '';
  demoFiles.filter(f => f.confidence === confidence).forEach((file, idx) => {
    const div = document.createElement('div');
    div.className = `file-dropdown-item ${confidence}`;
    div.textContent = file.name + (file.pages > 1 ? ` (${file.pages} pages)` : '');
    div.onclick = () => {
      scrollToFilePreview(file);
      closeAllConfidenceDropdowns();
    };
    dropdown.appendChild(div);
  });
}

function closeAllConfidenceDropdowns() {
  lowConfidenceDropdown.style.display = 'none';
  highConfidenceDropdown.style.display = 'none';
}

lowConfidenceLabel.addEventListener('click', (e) => {
  e.stopPropagation();
  if (lowConfidenceDropdown.style.display === 'block') {
    lowConfidenceDropdown.style.display = 'none';
  } else {
    renderConfidenceDropdown('low', lowConfidenceDropdown);
    lowConfidenceDropdown.classList.add('low');
    lowConfidenceDropdown.classList.remove('high');
    highConfidenceDropdown.classList.remove('low', 'high');
    // Left-align dropdown with label
    lowConfidenceDropdown.style.left = lowConfidenceLabel.offsetLeft + 'px';
    lowConfidenceDropdown.style.display = 'block';
    highConfidenceDropdown.style.display = 'none';
  }
});
highConfidenceLabel.addEventListener('click', (e) => {
  e.stopPropagation();
  if (highConfidenceDropdown.style.display === 'block') {
    highConfidenceDropdown.style.display = 'none';
  } else {
    renderConfidenceDropdown('high', highConfidenceDropdown);
    highConfidenceDropdown.classList.add('high');
    highConfidenceDropdown.classList.remove('low');
    lowConfidenceDropdown.classList.remove('low', 'high');
    // Left-align dropdown with label
    highConfidenceDropdown.style.left = highConfidenceLabel.offsetLeft + 'px';
    highConfidenceDropdown.style.display = 'block';
    lowConfidenceDropdown.style.display = 'none';
  }
});
document.body.addEventListener('click', closeAllConfidenceDropdowns);

// --- Two-column Files Preview and OCR Texts with draggable divider ---
const filePreviewsColumn = document.getElementById('file-previews-column');
const ocrTextsColumn = document.getElementById('ocr-texts-column');
const leftDivider = document.getElementById('left-divider');
const rightDivider = document.getElementById('right-divider');
const filesPanel = document.getElementById('files-panel');
const summaryPanel = document.getElementById('summary-panel');

// Store current widths
let previewsW, ocrW, summaryW;

function setColumnWidths(previews, ocr, summary) {
  filePreviewsColumn.style.flexBasis = previews + 'px';
  filePreviewsColumn.style.flex = '0 0 ' + previews + 'px';
  ocrTextsColumn.style.flexBasis = ocr + 'px';
  ocrTextsColumn.style.flex = '0 0 ' + ocr + 'px';
  summaryPanel.style.flexBasis = summary + 'px';
  summaryPanel.style.flex = '0 0 ' + summary + 'px';
  previewsW = previews;
  ocrW = ocr;
  summaryW = summary;
}

function getColumnWidths() {
  return {
    previewsW: filePreviewsColumn.getBoundingClientRect().width,
    ocrW: ocrTextsColumn.getBoundingClientRect().width,
    summaryW: summaryPanel.getBoundingClientRect().width
  };
}

// Initial layout
window.addEventListener('DOMContentLoaded', () => {
  const container = document.querySelector('.main-content');
  const total = container.offsetWidth;
  const leftDividerW = leftDivider.offsetWidth;
  const rightDividerW = rightDivider.offsetWidth;
  previewsW = Math.floor(total * 0.25);
  ocrW = Math.floor(total * 0.35);
  summaryW = total - previewsW - ocrW - leftDividerW - rightDividerW;
  setColumnWidths(previewsW, ocrW, summaryW);

  // Set current date in current summary box
  const currentDate = new Date();
  const dateStr = currentDate.toISOString().slice(0, 10);
  const currentSummaryDate = document.getElementById('current-summary-date');
  if (currentSummaryDate) currentSummaryDate.textContent = dateStr;

  renderAllFileRows();
  renderSummaryHistory();
});

// On window resize, adjust only the OCR column to absorb the difference
window.addEventListener('resize', () => {
  const container = document.querySelector('.main-content');
  const total = container.offsetWidth;
  const leftDividerW = leftDivider.offsetWidth;
  const rightDividerW = rightDivider.offsetWidth;
  const minOcr = 300;
  const minSummary = 350;
  let newOcrW = total - previewsW - summaryW - leftDividerW - rightDividerW;
  if (newOcrW < minOcr) newOcrW = minOcr;
  setColumnWidths(previewsW, newOcrW, summaryW);
});

// Left divider logic (file previews <-> ocr text)
let isLeftResizing = false;
leftDivider.addEventListener('mousedown', function(e) {
  isLeftResizing = true;
  document.body.style.cursor = 'col-resize';
});
document.addEventListener('mousemove', function(e) {
  if (!isLeftResizing) return;
  const container = document.querySelector('.main-content');
  const minPreviews = 180;
  const minOcr = 300;
  const leftDividerW = leftDivider.offsetWidth;
  const rightDividerW = rightDivider.offsetWidth;
  const total = container.offsetWidth;
  // summaryW is fixed
  let newPreviewsW = e.clientX - container.getBoundingClientRect().left;
  if (newPreviewsW < minPreviews) newPreviewsW = minPreviews;
  let newOcrW = total - newPreviewsW - summaryW - leftDividerW - rightDividerW;
  if (newOcrW < minOcr) {
    newOcrW = minOcr;
    newPreviewsW = total - newOcrW - summaryW - leftDividerW - rightDividerW;
    if (newPreviewsW < minPreviews) newPreviewsW = minPreviews;
  }
  setColumnWidths(newPreviewsW, newOcrW, summaryW);
});
document.addEventListener('mouseup', function() {
  isLeftResizing = false;
  document.body.style.cursor = '';
});

// Right divider logic (ocr text <-> summary)
let isRightResizing = false;
rightDivider.addEventListener('mousedown', function(e) {
  isRightResizing = true;
  document.body.style.cursor = 'col-resize';
});
document.addEventListener('mousemove', function(e) {
  if (!isRightResizing) return;
  const container = document.querySelector('.main-content');
  const minOcr = 300;
  const minSummary = 350;
  const leftDividerW = leftDivider.offsetWidth;
  const rightDividerW = rightDivider.offsetWidth;
  const previewsW = filePreviewsColumn.getBoundingClientRect().width;
  const total = container.offsetWidth;
  // Calculate the maximum allowed summary width so that previews and ocr columns are at least their minimums
  let maxSummaryW = total - previewsW - minOcr - leftDividerW - rightDividerW;
  let newSummaryW = total - e.clientX - rightDividerW;
  if (newSummaryW < minSummary) newSummaryW = minSummary;
  if (newSummaryW > maxSummaryW) newSummaryW = maxSummaryW;
  let newOcrW = total - previewsW - newSummaryW - leftDividerW - rightDividerW;
  if (newOcrW < minOcr) newOcrW = minOcr;
  setColumnWidths(previewsW, newOcrW, newSummaryW);
});
document.addEventListener('mouseup', function() {
  isRightResizing = false;
  document.body.style.cursor = '';
});

function renderAllFileRows(selectedFileName = null) {
  // Remove previous blocks
  filePreviewsColumn.innerHTML = '';
  ocrTextsColumn.innerHTML = '';

  // Sort files: lowest confidence first, then highest
  const sortedFiles = [
    ...demoFiles.filter(f => f.confidence === 'low'),
    ...demoFiles.filter(f => f.confidence === 'high'),
    ...demoFiles.filter(f => f.confidence !== 'low' && f.confidence !== 'high')
  ];

  sortedFiles.forEach(file => {
    let currentPage = 1;
    let currentRotation = 0;
    // File preview block (left)
    const previewBlock = document.createElement('div');
    previewBlock.className = 'file-preview-block';
    previewBlock.id = `preview-${file.name.replace(/[^a-zA-Z0-9]/g, '')}`;
    const originalHeader = document.createElement('div');
    originalHeader.className = 'file-original-header';
    const label = document.createElement('span');
    label.textContent = `${file.name} (Page 1 of ${file.pages})`;
    originalHeader.appendChild(label);
    const rotateBtn = document.createElement('button');
    rotateBtn.className = 'rotate-btn';
    rotateBtn.title = 'Rotate';
    rotateBtn.textContent = '⟳';
    originalHeader.appendChild(rotateBtn);
    previewBlock.appendChild(originalHeader);
    const originalContent = document.createElement('div');
    originalContent.className = 'file-original-content';
    originalContent.innerHTML = `<div class=\"file-original-placeholder\">[Original page 1 preview here]</div>`;
    previewBlock.appendChild(originalContent);
    // Page nav
    const pageNav = document.createElement('div');
    pageNav.className = 'file-page-nav';
    const prevBtn = document.createElement('button');
    prevBtn.className = 'page-nav prev';
    prevBtn.textContent = '<';
    prevBtn.disabled = true;
    const pageInfo = document.createElement('span');
    pageInfo.textContent = `Page 1 of ${file.pages}`;
    pageInfo.className = 'file-page-info';
    const nextBtn = document.createElement('button');
    nextBtn.className = 'page-nav next';
    nextBtn.textContent = '>';
    nextBtn.disabled = file.pages === 1;
    pageNav.appendChild(prevBtn);
    pageNav.appendChild(pageInfo);
    pageNav.appendChild(nextBtn);
    previewBlock.appendChild(pageNav);
    filePreviewsColumn.appendChild(previewBlock);
    // OCRed text block (right)
    const ocrBlock = document.createElement('div');
    ocrBlock.className = 'ocr-text-block';
    const ocrLabel = document.createElement('div');
    ocrLabel.className = 'file-ocr-header';
    ocrLabel.textContent = `OCRed Text: ${file.name} (Page 1)`;
    ocrBlock.appendChild(ocrLabel);
    const ocrContent = document.createElement('div');
    ocrContent.className = 'file-ocr-content';
    ocrContent.innerHTML = `<div class=\"file-ocr-placeholder\">[OCRed text for page 1 of ${file.name}]</div>`;
    ocrBlock.appendChild(ocrContent);
    ocrTextsColumn.appendChild(ocrBlock);
    // Scroll to selected
    if (selectedFileName && file.name === selectedFileName) {
      setTimeout(() => {
        previewBlock.scrollIntoView({ behavior: 'smooth', block: 'center' });
        ocrBlock.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }, 100);
    }
    // Event listeners for rotate and page navigation
    function updatePreview() {
      label.textContent = `${file.name} (Page ${currentPage} of ${file.pages})`;
      originalContent.innerHTML = `<div class=\"file-original-placeholder\" style=\"transform: rotate(${currentRotation}deg);\">[Original page ${currentPage} preview here]</div>`;
      ocrLabel.textContent = `OCRed Text: ${file.name} (Page ${currentPage})`;
      ocrContent.innerHTML = `<div class=\"file-ocr-placeholder\">[OCRed text for page ${currentPage} of ${file.name}]</div>`;
      prevBtn.disabled = currentPage === 1;
      nextBtn.disabled = currentPage === file.pages;
      pageInfo.textContent = `Page ${currentPage} of ${file.pages}`;
    }
    prevBtn.addEventListener('click', () => {
      if (currentPage > 1) {
        currentPage--;
        updatePreview();
      }
    });
    nextBtn.addEventListener('click', () => {
      if (currentPage < file.pages) {
        currentPage++;
        updatePreview();
      }
    });
    rotateBtn.addEventListener('click', () => {
      currentRotation = (currentRotation + 90) % 360;
      updatePreview();
    });
  });
}

// --- Helper to format date as DD-MM-YYYY ---
function formatDateDDMMYYYY(date) {
  function pad(n) { return n.toString().padStart(2, '0'); }
  if (typeof date === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(date)) {
    const [y, m, d] = date.split('-');
    return `${pad(d)}-${pad(m)}-${y}`;
  } else if (date instanceof Date) {
    return `${pad(date.getDate())}-${pad(date.getMonth() + 1)}-${date.getFullYear()}`;
  }
  return date;
}

// --- Demo summary history for the summary panel (Hebrew, right-aligned) ---
const demoSummaries = [
  { date: '2024-06-01', text: 'המטופל התקבל לבדיקה שגרתית. לא נמצאו בעיות.' },
  { date: '2024-05-15', text: 'ביקור מעקב. לחץ הדם היה מעט גבוה.' },
  { date: '2024-04-20', text: 'פגישה ראשונית. נרשמה תרופה ללחץ דם גבוה.' }
];

function renderSummaryHistory() {
  const historyDiv = document.getElementById('summary-history');
  if (!historyDiv) return;
  historyDiv.innerHTML = '';
  // Sort summaries by date descending (newest first)
  const sortedSummaries = [...demoSummaries].sort((a, b) => b.date.localeCompare(a.date));
  sortedSummaries.forEach(summary => {
    const block = document.createElement('div');
    block.className = 'summary-block';
    block.style.direction = 'rtl';
    block.style.textAlign = 'right';
    const header = document.createElement('div');
    header.className = 'summary-block-header';
    header.style.direction = 'rtl';
    header.style.textAlign = 'right';
    const dateSpan = document.createElement('span');
    dateSpan.className = 'summary-block-date';
    dateSpan.textContent = formatDateDDMMYYYY(summary.date);
    header.appendChild(dateSpan);
    block.appendChild(header);
    const textDiv = document.createElement('div');
    textDiv.className = 'summary-block-text';
    textDiv.style.direction = 'rtl';
    textDiv.style.textAlign = 'right';
    textDiv.textContent = summary.text;
    block.appendChild(textDiv);
    historyDiv.appendChild(block);
  });
}

// When a file is clicked in the dropdown, scroll to its preview
function scrollToFilePreview(file) {
  renderAllFileRows(file.name);
}

// --- File/Folder selection and trash icon logic (for demo, just clears preview) ---
const selectFilesBtn = document.querySelector('.select-files-btn');
const trashBtn = document.querySelector('.trash-btn');
selectFilesBtn.addEventListener('click', () => {
  // For demo, do nothing (real file selection would go here)
});
trashBtn.addEventListener('click', () => {
  // Remove all file previews from the files panel
  filePreviewsColumn.innerHTML = '';
  ocrTextsColumn.innerHTML = '';
});

// --- AI Assist Dialog (floating, draggable, resizable, chat, prompt management) ---
const aiAssistBtn = document.getElementById('ai-assist-btn');
const aiDialog = document.getElementById('ai-dialog');
const closeAiDialog = document.getElementById('close-ai-dialog');
const aiDialogMessages = document.getElementById('ai-dialog-messages');
const aiDialogInput = document.getElementById('ai-dialog-input');
const aiDialogSend = document.getElementById('ai-dialog-send');
let isDragging = false, dragOffsetX = 0, dragOffsetY = 0;

aiAssistBtn.addEventListener('click', () => {
  aiDialog.style.display = 'flex';
});
closeAiDialog.addEventListener('click', () => {
  aiDialog.style.display = 'none';
});
aiDialog.querySelector('.ai-dialog-header').addEventListener('mousedown', function(e) {
  isDragging = true;
  dragOffsetX = e.clientX - aiDialog.offsetLeft;
  dragOffsetY = e.clientY - aiDialog.offsetTop;
  document.body.style.userSelect = 'none';
});
document.addEventListener('mousemove', function(e) {
  if (!isDragging) return;
  aiDialog.style.left = (e.clientX - dragOffsetX) + 'px';
  aiDialog.style.top = (e.clientY - dragOffsetY) + 'px';
});
document.addEventListener('mouseup', function() {
  isDragging = false;
  document.body.style.userSelect = '';
});
aiDialogSend.addEventListener('click', () => {
  const msg = aiDialogInput.value.trim();
  if (!msg) return;
  const userMsg = document.createElement('div');
  userMsg.textContent = "You: " + msg;
  aiDialogMessages.appendChild(userMsg);
  aiDialogInput.value = '';
  // For demo, echo back
  setTimeout(() => {
    const aiMsg = document.createElement('div');
    aiMsg.textContent = "AI: " + msg.split('').reverse().join('');
    aiDialogMessages.appendChild(aiMsg);
    aiDialogMessages.scrollTop = aiDialogMessages.scrollHeight;
  }, 500);
});

// --- Knowledge file upload ---
const addKnowledgeBtn = document.getElementById('add-knowledge-btn');
const knowledgeFileInput = document.getElementById('knowledge-file-input');
addKnowledgeBtn.addEventListener('click', () => {
  knowledgeFileInput.value = '';
  knowledgeFileInput.click();
});
knowledgeFileInput.addEventListener('change', () => {
  if (knowledgeFileInput.files.length > 0) {
    alert('Knowledge file added: ' + knowledgeFileInput.files[0].name + '\nSupported formats: .txt, .pdf, .docx');
  }
});

// --- Save All Corrections, Export, and Start button logic (placeholders) ---
document.getElementById('save-btn').addEventListener('click', () => {
  alert('All corrections saved!');
});
document.getElementById('export-summary-btn').addEventListener('click', () => {
  alert('Summary exported!');
});
document.getElementById('start-btn').addEventListener('click', () => {
  alert('OCR and summarization started!');
});

// --- Set current date in current summary textarea, right-aligned, Hebrew placeholder ---
function setCurrentSummaryDateInTextarea() {
  const textarea = document.getElementById('summary-textarea');
  if (!textarea) return;
  textarea.style.direction = 'rtl';
  textarea.style.textAlign = 'right';
  textarea.placeholder = 'הקלד או ערוך סיכום...';
  const currentDate = new Date();
  const dateStr = formatDateDDMMYYYY(currentDate);
  // Remove any existing date at the top
  let lines = textarea.value.split('\n');
  if (lines.length > 0 && (/^\d{4}-\d{2}-\d{2}$/.test(lines[0].trim()) || /^\d{1,2}-\d{1,2}-\d{4}$/.test(lines[0].trim()))) {
    lines.shift();
  }
  let userText = lines.join('\n').replace(/^\n+/, '');
  // If the textarea is empty or only contains the date, set value to date + blank line
  if (!userText.trim()) {
    textarea.value = `${dateStr}\n`;
    setTimeout(() => {
      textarea.setSelectionRange(textarea.value.length, textarea.value.length);
    }, 0);
  } else {
    textarea.value = `${dateStr}\n${userText}`;
  }
}
window.addEventListener('DOMContentLoaded', () => {
  setCurrentSummaryDateInTextarea();
  document.getElementById('summary-textarea').addEventListener('input', setCurrentSummaryDateInTextarea);
});

// DictaLM 2.0 button handler
const dictalmBtn = document.getElementById('dictalm-btn');
if (dictalmBtn) {
  dictalmBtn.addEventListener('click', () => {
    alert('DictaLM 2.0 action triggered!');
  });
}

// --- Chat dropdown logic for confidence bar ---
const chatDropdownBtn = document.getElementById('chat-dropdown-btn');
const chatDropdownList = document.getElementById('chat-dropdown-list');
const chatDropdownContainer = document.getElementById('chat-dropdown-container');
let currentChat = localStorage.getItem('chatEngine') || 'DictaLM 2.0';

function updateChatDropdown() {
  Array.from(chatDropdownList.children).forEach(child => {
    if (child.dataset && child.dataset.chat) {
      child.classList.toggle('selected', child.dataset.chat === currentChat);
      child.setAttribute('data-selected', child.dataset.chat === currentChat);
      child.innerHTML = (child.dataset.chat === currentChat ? '✔ ' : '') + child.textContent.replace('✔ ', '');
    }
  });
  chatDropdownBtn.innerHTML = 'CHAT Engine: ' + currentChat + ' ▼';
}

chatDropdownBtn.addEventListener('click', (e) => {
  e.stopPropagation();
  chatDropdownContainer.classList.toggle('open');
  // Close other dropdowns
  document.querySelectorAll('.menu-dropdown-content').forEach(l => {
    if (!chatDropdownList.contains(l)) l.style.display = 'none';
  });
});
Array.from(chatDropdownList.children).forEach(child => {
  if (child.dataset && child.dataset.chat) {
    child.onclick = (e) => {
      currentChat = child.dataset.chat;
      localStorage.setItem('chatEngine', currentChat);
      updateChatDropdown();
      chatDropdownContainer.classList.remove('open');
    };
  }
});
document.body.addEventListener('click', () => {
  chatDropdownContainer.classList.remove('open');
});
updateChatDropdown();
