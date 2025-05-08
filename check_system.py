import sys
import platform
import os
from PyQt5.QtWidgets import QApplication, QMessageBox

def show_system_info():
    app = QApplication([])
    
    # Get system information
    python_version = sys.version.split()[0]
    macos_version = platform.mac_ver()[0]
    is_app = '.app' in sys.executable
    running_as = "App Bundle" if is_app else "Terminal Script"
    
    # Create message
    message = f"""
    Python Version: {python_version}
    macOS Version: {macos_version}
    Running as: {running_as}
    """
    
    # Show popup
    QMessageBox.information(None, "System Information", message)

if __name__ == "__main__":
    show_system_info() 