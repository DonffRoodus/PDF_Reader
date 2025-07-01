#!/usr/bin/env python3
"""
Demo script to test the dynamic widget rearrangement feature.
This script will open the PDF reader and allow you to resize the window
to see how widgets automatically rearrange themselves.
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox, QPushButton, QVBoxLayout, QDialog
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QIcon

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def demo_resize_functionality():
    """Demonstrate the resize functionality."""
    try:
        from src.pdf_reader.ui.main_window import MainWindow
        
        app = QApplication(sys.argv)
        
        # Create main window
        main_window = MainWindow()
        main_window.show()
        
        # Create a demo dialog with instructions
        demo_dialog = QDialog(main_window)
        demo_dialog.setWindowTitle("Dynamic Layout Demo")
        demo_dialog.setModal(False)
        demo_dialog.resize(400, 300)
        
        layout = QVBoxLayout(demo_dialog)
        
        instructions = """
        🎯 Dynamic Widget Rearrangement Demo

        This PDF Reader now automatically rearranges its interface 
        based on the window size! Try the following:

        📏 Resize Instructions:
        • Make the window very small (< 800px wide)
          → All dock widgets hide for maximum content space
        
        • Make the window medium size (800-1200px wide)
          → Bookmarks and annotations show, TOC hides
        
        • Make the window large (> 1200px wide)
          → All widgets show with optimal positioning
        
        🔧 What Changes:
        • Dock widgets visibility and positioning
        • Toolbar button styles (icon-only vs text+icon)
        • Tab styling (compact vs standard)
        • Status messages inform you of layout changes
        
        💡 Tips:
        • Try both width and height changes
        • Watch the dock widgets move and hide/show
        • Notice toolbar icons change size
        • Tabs become more compact on small screens
        
        Close this dialog and start resizing the main window!
        """
        
        from PyQt6.QtWidgets import QTextEdit
        text_widget = QTextEdit()
        text_widget.setPlainText(instructions)
        text_widget.setReadOnly(True)
        layout.addWidget(text_widget)
        
        close_button = QPushButton("Start Demo!")
        close_button.clicked.connect(demo_dialog.close)
        layout.addWidget(close_button)
        
        # Position the dialog next to the main window
        demo_dialog.move(main_window.x() + main_window.width() + 10, main_window.y())
        demo_dialog.show()
        
        # Set minimum size for the main window to allow testing
        main_window.setMinimumSize(400, 300)
        
        print("🚀 Dynamic Layout Demo Started!")
        print("📋 Instructions dialog opened - follow the guide to test resizing")
        print("🖱️  Try resizing the main window to see dynamic layout changes")
        
        return app.exec()
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    success = demo_resize_functionality()
    sys.exit(success)
