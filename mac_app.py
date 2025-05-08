import sys
import os
import logging
import platform
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                            QWidget, QFileDialog, QTextEdit, QLabel, QProgressBar,
                            QComboBox, QMessageBox, QCheckBox, QHBoxLayout, QDialog, QTreeView, QListWidget)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
import pytesseract
from PIL import Image, UnidentifiedImageError
import tempfile
from pdf2image import convert_from_path
import shutil
from PyQt6.QtWidgets import QFileSystemModel
from tkinter import Tk, filedialog
from AppKit import NSApplication, NSApp, NSOpenPanel, NSURL
from Foundation import NSObject

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ocr_app.log'),
        logging.StreamHandler()
    ]
)

# Log environment information
logging.info("=== Environment Information ===")
logging.info(f"Python Version: {sys.version}")
logging.info(f"macOS Version: {platform.mac_ver()[0]}")
logging.info(f"Running in terminal: {bool(os.environ.get('TERM'))}")
logging.info(f"Running in app bundle: {'.app' in sys.executable}")
logging.info(f"Executable path: {sys.executable}")
logging.info(f"Current working directory: {os.getcwd()}")
logging.info(f"PyQt Version: {QApplication.instance().applicationVersion() if QApplication.instance() else 'Not initialized'}")
logging.info("============================")

def is_pdf_file(file_path):
    """Check if a file is actually a PDF by examining its content."""
    try:
        logging.debug(f"Checking if file is a valid PDF: {file_path}")
        with open(file_path, 'rb') as f:
            # Read more bytes to ensure we catch the PDF header
            header = f.read(1024)
            # Look for the PDF signature anywhere in the first 1024 bytes
            is_pdf = b'%PDF-' in header
            logging.debug(f"PDF header check result: {is_pdf}")
            if is_pdf:
                # Try to convert the first page to verify it's a valid PDF
                try:
                    images = convert_from_path(file_path, first_page=1, last_page=1)
                    if images:
                        logging.debug("Successfully converted first page of PDF")
                        return True
                    else:
                        logging.error("PDF appears to be empty or corrupted")
                        return False
                except Exception as e:
                    logging.error(f"Error converting PDF first page: {str(e)}")
                    return False
            return False
    except Exception as e:
        logging.error(f"Error checking PDF header: {str(e)}")
        return False

def is_valid_file(file_path):
    """Check if the file is a valid image."""
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            logging.error(f"File does not exist: {file_path}")
            return False

        # Check file extension
        file_ext = os.path.splitext(file_path)[1].lower()
        supported_images = ['.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp']
        
        if file_ext not in supported_images:
            logging.error(f"Invalid image extension: {file_ext}. Supported extensions: {', '.join(supported_images)}")
            return False

        # For image files
        try:
            with Image.open(file_path) as img:
                img.verify()  # Verify it's an image
                
                # For TIFF files, check frames
                if file_ext in ['.tiff', '.tif']:
                    if not hasattr(img, 'n_frames') or img.n_frames < 1:
                        logging.error("Invalid TIFF file: No frames found")
                        return False
                
                # Try to actually load the image data
                img = Image.open(file_path)
                img.load()
                
                # Convert RGBA to RGB if needed
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                
                # Additional validation based on image properties
                if img.size[0] < 1 or img.size[1] < 1:
                    logging.error("Invalid image dimensions")
                    return False
                
                return True
                
        except (UnidentifiedImageError, IOError) as e:
            logging.error(f"Invalid image file: {str(e)}")
            return False

    except Exception as e:
        logging.error(f"Error validating file: {str(e)}")
        return False

class OCRThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    debug = pyqtSignal(str)

    def __init__(self, file_path, language, debug_mode=False):
        super().__init__()
        self.file_path = file_path
        self.language = language
        self.debug_mode = debug_mode
        self.temp_dir = None

    def run(self):
        try:
            self.debug.emit(f"Starting OCR process for file: {self.file_path}")
            self.progress.emit(10)
            
            # Create temporary directory for processing
            self.temp_dir = tempfile.mkdtemp()
            
            if self.file_path.lower().endswith('.pdf'):
                self.debug.emit("Processing PDF file...")
                try:
                    # Convert PDF to images
                    images = convert_from_path(
                        self.file_path,
                        dpi=300,
                        output_folder=self.temp_dir,
                        fmt="png"
                    )
                    self.debug.emit(f"Converted PDF to {len(images)} images")
                    
                    full_text = ""
                    for i, image in enumerate(images):
                        self.progress.emit(int(10 + (i / len(images)) * 80))
                        self.debug.emit(f"Processing page {i+1} of {len(images)}")
                        
                        # Save image temporarily
                        temp_image_path = os.path.join(self.temp_dir, f"page_{i+1}.png")
                        image.save(temp_image_path, "PNG")
                        
                        # Perform OCR on the image
                        text = pytesseract.image_to_string(image, lang=self.language)
                        full_text += f"\n--- Page {i+1} ---\n{text}\n"
                    
                    self.progress.emit(90)
                    
                    if not full_text.strip():
                        raise ValueError("No text was detected in the PDF. Please try a different file or adjust the quality.")
                    
                    self.debug.emit("PDF OCR process completed successfully")
                    self.finished.emit(full_text)
                    self.progress.emit(100)
                    
                except Exception as e:
                    raise ValueError(f"Error processing PDF: {str(e)}")
            else:
                # Process single image
                self.debug.emit("Opening image file...")
                try:
                    image = Image.open(self.file_path)
                    
                    # Handle multi-page TIFF
                    if image.format in ['TIFF', 'TIF'] and hasattr(image, 'n_frames') and image.n_frames > 1:
                        self.debug.emit(f"Processing multi-page TIFF with {image.n_frames} frames")
                        full_text = ""
                        for i in range(image.n_frames):
                            self.progress.emit(int(10 + (i / image.n_frames) * 80))
                            image.seek(i)
                            # Convert to RGB if needed
                            if image.mode != 'RGB':
                                self.debug.emit(f"Converting frame {i+1} from {image.mode} to RGB")
                                frame = image.convert('RGB')
                            else:
                                frame = image
                            
                            # Process frame
                            text = pytesseract.image_to_string(frame, lang=self.language)
                            full_text += f"\n--- Page {i+1} ---\n{text}\n"
                            
                        self.progress.emit(90)
                        if not full_text.strip():
                            raise ValueError("No text was detected in the image. Please try a different file or adjust the quality.")
                        
                        self.debug.emit("Multi-page TIFF processing completed successfully")
                        self.finished.emit(full_text)
                        self.progress.emit(100)
                    else:
                        # Single image processing
                        if image.mode != 'RGB':
                            self.debug.emit(f"Converting image from {image.mode} to RGB")
                            image = image.convert('RGB')
                        
                        self.progress.emit(30)
                        
                        # Log image details in debug mode
                        if self.debug_mode:
                            self.debug.emit(f"Image size: {image.size}")
                            self.debug.emit(f"Image mode: {image.mode}")
                            self.debug.emit(f"Image format: {image.format}")
                        
                        # Perform OCR
                        self.debug.emit(f"Performing OCR with language: {self.language}")
                        text = pytesseract.image_to_string(image, lang=self.language)
                        self.progress.emit(90)
                        
                        if not text.strip():
                            raise ValueError("No text was detected in the image. Please try a different file or adjust the quality.")
                        
                        self.debug.emit("Image OCR process completed successfully")
                        self.finished.emit(text)
                        self.progress.emit(100)
                        
                except Exception as e:
                    raise ValueError(f"Error processing image: {str(e)}")
                
        except Exception as e:
            self.error.emit(str(e))
            self.debug.emit(f"Error in OCR process: {str(e)}")
        finally:
            # Clean up temporary files
            if self.temp_dir and os.path.exists(self.temp_dir):
                try:
                    shutil.rmtree(self.temp_dir)
                except Exception as e:
                    self.debug.emit(f"Error cleaning up temp files: {str(e)}")

def check_tesseract_installation():
    """Check if Tesseract is properly installed and accessible."""
    try:
        pytesseract.get_tesseract_version()
        return True
    except Exception as e:
        logging.error(f"Tesseract not found or not properly installed: {str(e)}")
        return False

class CustomFileDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Document")
        self.setMinimumSize(600, 400)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Create file type filter
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("File Type:"))
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All Supported Files", "PDF Files", "Image Files"])
        self.filter_combo.currentTextChanged.connect(self.update_file_list)
        filter_layout.addWidget(self.filter_combo)
        layout.addLayout(filter_layout)
        
        # Create split view
        split_layout = QHBoxLayout()
        
        # Directory tree
        self.dir_tree = QTreeView()
        self.dir_model = QFileSystemModel()
        self.dir_model.setRootPath(os.path.expanduser("~"))
        self.dir_tree.setModel(self.dir_model)
        self.dir_tree.setRootIndex(self.dir_model.index(os.path.expanduser("~")))
        self.dir_tree.clicked.connect(self.on_directory_selected)
        split_layout.addWidget(self.dir_tree)
        
        # File list
        self.file_list = QListWidget()
        self.file_list.itemDoubleClicked.connect(self.accept)
        split_layout.addWidget(self.file_list)
        
        layout.addLayout(split_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.open_button = QPushButton("Open")
        self.open_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.open_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        # Set styles
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
            }
            QLabel {
                color: #e0e0e0;
            }
            QComboBox {
                background-color: #363636;
                color: #e0e0e0;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 5px;
            }
            QTreeView, QListWidget {
                background-color: #363636;
                color: #e0e0e0;
                border: 1px solid #555555;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #3a7d44;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton#cancel_button {
                background-color: #555555;
            }
            QPushButton#cancel_button:hover {
                background-color: #666666;
            }
        """)
        
        self.selected_file = None
        self.update_file_list()
    
    def on_directory_selected(self, index):
        path = self.dir_model.filePath(index)
        self.update_file_list(path)
    
    def update_file_list(self, path=None):
        if path is None:
            path = self.dir_model.filePath(self.dir_tree.currentIndex())
        
        self.file_list.clear()
        try:
            files = os.listdir(path)
            for file in files:
                full_path = os.path.join(path, file)
                if os.path.isfile(full_path):
                    ext = os.path.splitext(file)[1].lower()
                    supported_images = ['.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp']
                    
                    if self.filter_combo.currentText() == "All Supported Files":
                        if ext == '.pdf' or ext in supported_images:
                            self.file_list.addItem(file)
                    elif self.filter_combo.currentText() == "PDF Files" and ext == '.pdf':
                        self.file_list.addItem(file)
                    elif self.filter_combo.currentText() == "Image Files" and ext in supported_images:
                        self.file_list.addItem(file)
        except Exception as e:
            logging.error(f"Error updating file list: {str(e)}")
    
    def accept(self):
        if self.file_list.currentItem():
            current_dir = self.dir_model.filePath(self.dir_tree.currentIndex())
            self.selected_file = os.path.join(current_dir, self.file_list.currentItem().text())
            super().accept()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OCR Document Scanner")
        self.setMinimumSize(800, 600)
        
        # Initialize NSApplication at startup
        self.ns_app = NSApplication.sharedApplication()
        
        # Show system information
        system_info = f"""
        Python Version: {sys.version.split()[0]}
        macOS Version: {platform.mac_ver()[0]}
        Running as: {'App Bundle' if '.app' in sys.executable else 'Terminal Script'}
        """
        QMessageBox.information(self, "System Information", system_info)
        
        # Check Tesseract installation
        if not check_tesseract_installation():
            QMessageBox.critical(
                self,
                "Tesseract Not Found",
                "Tesseract OCR is not installed or not properly configured.\n\n"
                "Please install Tesseract using:\n"
                "brew install tesseract\n\n"
                "For Hebrew support, also install:\n"
                "brew install tesseract-lang"
            )
            sys.exit(1)
        
        # Set window icon
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                'Resources', 'AppIcon.icns')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Development mode flag - set to True by default
        self.debug_mode = True
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Development mode toggle - checked by default
        dev_layout = QHBoxLayout()
        self.debug_checkbox = QCheckBox("Development Mode")
        self.debug_checkbox.setChecked(True)  # Set checked by default
        self.debug_checkbox.stateChanged.connect(self.toggle_debug_mode)
        dev_layout.addWidget(self.debug_checkbox)
        layout.addLayout(dev_layout)
        
        # Language selection
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Hebrew Only", "Hebrew + English", "English Only"])
        layout.addWidget(QLabel("Select Language:"))
        layout.addWidget(self.language_combo)
        
        # File input area with custom styling
        file_input_layout = QHBoxLayout()
        
        # File path display
        self.file_path_label = QLabel("No file selected")
        self.file_path_label.setStyleSheet("""
            QLabel {
                background-color: #363636;
                color: #e0e0e0;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
        """)
        self.file_path_label.setMinimumHeight(40)
        file_input_layout.addWidget(self.file_path_label)
        
        # Browse button
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_file)
        self.browse_button.setStyleSheet("""
            QPushButton {
                background-color: #3a7d44;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        file_input_layout.addWidget(self.browse_button)
        
        # Clear button
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_file)
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #555555;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #666666;
            }
        """)
        file_input_layout.addWidget(self.clear_button)
        
        layout.addLayout(file_input_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        # Text display
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        layout.addWidget(self.text_display)
        
        # Debug output - visible by default
        self.debug_display = QTextEdit()
        self.debug_display.setReadOnly(True)
        self.debug_display.setVisible(True)  # Set visible by default
        layout.addWidget(self.debug_display)
        
        # Status label
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
        
        # Set styles
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QWidget {
                background-color: #2b2b2b;
                color: #e0e0e0;
            }
            QPushButton {
                background-color: #3a7d44;
                color: #ffffff;
                padding: 8px;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
            QTextEdit {
                background-color: #363636;
                color: #e0e0e0;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
            QComboBox {
                background-color: #363636;
                color: #e0e0e0;
                padding: 5px;
                border: 1px solid #555555;
                border-radius: 4px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
            QProgressBar {
                background-color: #363636;
                color: #e0e0e0;
                border: 1px solid #555555;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3a7d44;
            }
            QCheckBox {
                color: #e0e0e0;
                font-size: 14px;
            }
            QCheckBox::indicator {
                width: 15px;
                height: 15px;
            }
            QCheckBox::indicator:unchecked {
                background-color: #363636;
                border: 1px solid #555555;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                background-color: #3a7d44;
                border: 1px solid #3a7d44;
                border-radius: 3px;
            }
            QLabel {
                color: #e0e0e0;
            }
        """)
        
        logging.info("Application started")

    def toggle_debug_mode(self, state):
        self.debug_mode = bool(state)
        self.debug_display.setVisible(self.debug_mode)
        logging.info(f"Development mode {'enabled' if self.debug_mode else 'disabled'}")

    def log_debug(self, message):
        if self.debug_mode:
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.debug_display.append(f"[{timestamp}] {message}")
            logging.debug(message)

    def browse_file(self):
        try:
            # Create and configure NSOpenPanel
            panel = NSOpenPanel.openPanel()
            panel.setCanChooseFiles_(True)
            panel.setCanChooseDirectories_(False)
            panel.setAllowsMultipleSelection_(False)
            panel.setTitle_("Select Document")
            
            # Set up allowed file types
            allowed_types = ["pdf", "png", "jpg", "jpeg", "tiff", "tif", "bmp"]
            panel.setAllowedFileTypes_(allowed_types)
            
            # Show the panel
            if panel.runModal() == 1:  # NSModalResponseOK
                selected_url = panel.URLs()[0]
                file_name = selected_url.path()
                self.file_path_label.setText(file_name)
                self.log_debug(f"File selected: {file_name}")
                self.handle_file_selection(file_name)
        except Exception as e:
            error_msg = f"Error opening file dialog: {str(e)}"
            self.log_debug(error_msg)
            QMessageBox.critical(self, "Error", error_msg)

    def clear_file(self):
        self.file_path_label.setText("No file selected")
        self.text_display.clear()
        self.progress_bar.setValue(0)
        self.status_label.setText("Ready")
        self.log_debug("File selection cleared")

    def handle_file_selection(self, file_name):
        self.file_path_label.setText(file_name)
        self.log_debug(f"Selected file: {file_name}")
        
        try:
            # Check file extension first
            file_ext = os.path.splitext(file_name)[1].lower()
            self.log_debug(f"File extension: {file_ext}")
            
            supported_images = ['.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp']
            
            if file_ext not in ['.pdf'] + supported_images:
                raise ValueError("Unsupported file type. Please select a PDF or image file.")
            
            # Validate the file based on its type
            if file_ext == '.pdf':
                self.log_debug("PDF file detected, validating...")
                if not is_pdf_file(file_name):
                    raise ValueError("The selected file is not a valid PDF document")
                self.log_debug("PDF validation successful")
            else:
                self.log_debug("Image file detected, validating...")
                if not is_valid_file(file_name):
                    raise ValueError("The selected file is not a valid image")
                self.log_debug("Image validation successful")
            
            # If we get here, the file is valid
            self.log_debug("File validation successful, starting processing...")
            self.process_file(file_name)
            
        except Exception as e:
            error_msg = str(e)
            self.log_debug(f"Error validating file: {error_msg}")
            QMessageBox.warning(
                self,
                "Invalid File",
                f"Error: {error_msg}\n\nPlease ensure:\n"
                "1. The file exists and is not corrupted\n"
                "2. The file is one of the supported formats:\n"
                "   - PDF (.pdf)\n"
                "   - Images (.png, .jpg, .jpeg, .tiff, .tif, .bmp)\n"
                "3. The file is readable and not empty"
            )

    def process_file(self, file_path):
        try:
            # Get selected language
            language_map = {
                "Hebrew Only": "heb",
                "Hebrew + English": "heb+eng",
                "English Only": "eng"
            }
            selected_language = language_map[self.language_combo.currentText()]
            self.log_debug(f"Selected language: {selected_language}")
            
            # Create and start OCR thread
            self.ocr_thread = OCRThread(file_path, selected_language, self.debug_mode)
            self.ocr_thread.progress.connect(self.update_progress)
            self.ocr_thread.finished.connect(self.show_results)
            self.ocr_thread.error.connect(self.show_error)
            self.ocr_thread.debug.connect(self.log_debug)
            
            # Update UI
            self.status_label.setText("Processing...")
            self.browse_button.setEnabled(False)
            self.clear_button.setEnabled(False)
            self.progress_bar.setValue(0)
            self.text_display.clear()
            if self.debug_mode:
                self.debug_display.clear()
            
            self.ocr_thread.start()
            
        except Exception as e:
            error_msg = f"Error processing file: {str(e)}"
            self.log_debug(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
            self.status_label.setText("Error occurred")
            self.browse_button.setEnabled(True)
            self.clear_button.setEnabled(True)

    def update_progress(self, value):
        self.progress_bar.setValue(value)
        self.log_debug(f"Progress: {value}%")

    def show_results(self, text):
        self.text_display.setText(text)
        self.status_label.setText("Processing complete")
        self.browse_button.setEnabled(True)
        self.clear_button.setEnabled(True)
        self.log_debug("Processing completed successfully")

    def show_error(self, error_message):
        QMessageBox.critical(self, "Error", error_message)
        self.status_label.setText("Error occurred")
        self.browse_button.setEnabled(True)
        self.clear_button.setEnabled(True)
        logging.error(error_message)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 