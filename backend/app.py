import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QPushButton, QLabel, QFileDialog, QProgressBar,
                            QTextEdit, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage
import pytesseract
from pdf2image import convert_from_path
import tempfile

class OCRWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        try:
            if self.file_path.lower().endswith('.pdf'):
                # Convert PDF to images
                images = convert_from_path(self.file_path)
                text = ""
                for i, image in enumerate(images):
                    self.progress.emit(int((i + 1) / len(images) * 100))
                    text += pytesseract.image_to_string(image, lang='heb+eng')
            else:
                # Process single image
                text = pytesseract.image_to_string(self.file_path, lang='heb+eng')
                self.progress.emit(100)
            
            self.finished.emit(text)
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OCR Scanner")
        self.setMinimumSize(800, 600)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create UI elements
        self.select_button = QPushButton("Select File")
        self.select_button.clicked.connect(self.select_file)
        layout.addWidget(self.select_button)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)

        # Initialize worker
        self.worker = None

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select File",
            "",
            "PDF Files (*.pdf);;Image Files (*.png *.jpg *.jpeg)"
        )
        
        if file_path:
            self.process_file(file_path)

    def process_file(self, file_path):
        self.progress_bar.setValue(0)
        self.result_text.clear()
        
        self.worker = OCRWorker(file_path)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.show_results)
        self.worker.error.connect(self.show_error)
        self.worker.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def show_results(self, text):
        self.result_text.setText(text)
        QMessageBox.information(self, "Success", "OCR processing completed!")

    def show_error(self, error_msg):
        QMessageBox.critical(self, "Error", f"An error occurred: {error_msg}")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 