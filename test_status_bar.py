#!/usr/bin/env python3
"""
Test script to verify status bar real-time updates
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.pdf_reader.ui.main_window import MainWindow


def test_status_bar():
    """Test the status bar functionality"""
    app = QApplication(sys.argv)
    
    main_window = MainWindow()
    main_window.show()
    
    def print_status_info():
        """Print current status bar information"""
        print("\n=== Status Bar Information ===")
        print(f"Document name: {main_window.document_name_label.text()}")
        print(f"Page info: {main_window.page_info_label.text()}")
        print(f"Zoom info: {main_window.zoom_info_label.text()}")
        print("==============================\n")
    
    # Print initial status
    print_status_info()
    
    # Set up a timer to periodically print status (for testing)
    timer = QTimer()
    timer.timeout.connect(print_status_info)
    timer.start(5000)  # Print every 5 seconds
    
    print("Test application started. You can:")
    print("1. Open a PDF file to see document name update")
    print("2. Navigate pages to see page numbers update")
    print("3. Zoom in/out to see zoom percentage update")
    print("4. Switch between tabs to see status update")
    print("5. Status info will be printed every 5 seconds")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    test_status_bar()
