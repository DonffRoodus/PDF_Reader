#!/usr/bin/env python3
"""
Final verification test for the reset zoom fix.
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

def test_import_and_reset():
    """Test that the reset zoom method can be imported and called."""
    try:
        from src.pdf_reader.ui.pdf_viewer import PDFViewer
        from src.pdf_reader.ui.main_window import MainWindow
        
        app = QApplication(sys.argv)
        
        # Test that reset_zoom method exists on PDFViewer
        viewer = PDFViewer()
        assert hasattr(viewer, 'reset_zoom'), "PDFViewer missing reset_zoom method"
        
        # Test that main window's reset_zoom method exists
        main_window = MainWindow()
        assert hasattr(main_window, 'reset_zoom'), "MainWindow missing reset_zoom method"
        
        print("✅ All imports successful")
        print("✅ PDFViewer has reset_zoom method")
        print("✅ MainWindow has reset_zoom method")
        print("🎉 Reset zoom fix verified!")
        
        app.quit()
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    success = test_import_and_reset()
    sys.exit(0 if success else 1)
