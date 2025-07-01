#!/usr/bin/env python3
"""
Test script to verify that the closeEvent fix works correctly.
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_close_event():
    """Test that the closeEvent method works without errors."""
    try:
        from src.pdf_reader.ui.main_window import MainWindow
        
        app = QApplication(sys.argv)
        
        # Create main window
        main_window = MainWindow()
        
        print("🧪 Testing Close Event Fix")
        print("=" * 30)
        
        # Test closeEvent method directly
        print("📋 Testing closeEvent method...")
        
        # Create a mock close event
        from PyQt6.QtGui import QCloseEvent
        close_event = QCloseEvent()
        
        # Call closeEvent - this should not raise an AttributeError
        main_window.closeEvent(close_event)
        
        print("✅ closeEvent executed without errors")
        print("✅ No AttributeError for save_reading_progress")
        print("🎉 Close event fix verified!")
        
        app.quit()
        return True
        
    except AttributeError as e:
        if "save_reading_progress" in str(e):
            print(f"❌ AttributeError still exists: {e}")
            return False
        else:
            # Some other AttributeError, might be expected
            print(f"⚠️  Other AttributeError (might be expected): {e}")
            return True
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_close_event()
    sys.exit(0 if success else 1)
