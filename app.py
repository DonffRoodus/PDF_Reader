#!/usr/bin/env python3
"""
PDF Reader Application Entry Point

A modern PDF reader application built with PyQt6 and PyMuPDF.
Supports multiple view modes including single page, double page, 
continuous scroll, and various fit modes.
"""

import sys
from PyQt6.QtWidgets import QApplication

from src.pdf_reader.ui.main_window import MainWindow
from src.pdf_reader.ui.styling import get_application_stylesheet


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    
    # Apply application stylesheet
    app.setStyleSheet(get_application_stylesheet())
    
    # Create and show main window
    main_window = MainWindow()
    main_window.show()
    
    # Start the event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
