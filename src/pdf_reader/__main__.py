"""
Main entry point for the PDF Reader package.

This allows the package to be run with:
    python -m pdf_reader
"""

import sys
from PyQt6.QtWidgets import QApplication

from .ui.main_window import MainWindow
from .ui.styling import get_application_stylesheet


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
