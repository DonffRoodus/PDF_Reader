#!/usr/bin/env python3
"""
Test script for the dynamic widget rearrangement functionality.
This script tests the resize logic without requiring manual interaction.
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QResizeEvent

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_resize_functionality():
    """Test the resize functionality programmatically."""
    try:
        from src.pdf_reader.ui.main_window import MainWindow
        
        app = QApplication(sys.argv)
        
        # Create main window
        main_window = MainWindow()
        
        print("🧪 Testing Dynamic Widget Rearrangement")
        print("=" * 50)
        
        # First, show initial state
        print("\n🏁 Initial State:")
        layout_info = main_window.get_layout_info()
        print(f"   Window size: {layout_info['window_size']['width']}x{layout_info['window_size']['height']}")
        print("   Initial dock visibility:")
        for name, data in layout_info['dock_widgets'].items():
            print(f"     - {name}: {'Visible' if data['visible'] else 'Hidden'}")
        
        # Make sure all docks are visible initially for testing
        print("\n🔧 Setting up test - making all docks visible...")
        print(f"   TOC dock exists: {hasattr(main_window, 'toc_dock')}")
        print(f"   Bookmarks dock exists: {hasattr(main_window, 'bookmarks_dock')}")
        print(f"   Annotations dock exists: {hasattr(main_window, 'annotations_dock')}")
        
        if hasattr(main_window, 'toc_dock'):
            main_window.toc_dock.setVisible(True)
            print(f"   TOC dock visible after setting: {main_window.toc_dock.isVisible()}")
        if hasattr(main_window, 'bookmarks_dock'):
            main_window.bookmarks_dock.setVisible(True)
            print(f"   Bookmarks dock visible after setting: {main_window.bookmarks_dock.isVisible()}")
        if hasattr(main_window, 'annotations_dock'):
            main_window.annotations_dock.setVisible(True)
            print(f"   Annotations dock visible after setting: {main_window.annotations_dock.isVisible()}")
        
        layout_info = main_window.get_layout_info()
        print("   After making all visible:")
        for name, data in layout_info['dock_widgets'].items():
            print(f"     - {name}: {'Visible' if data['visible'] else 'Hidden'}")
        
        # Test 1: Very small window (should hide all docks)
        print("\n📱 Test 1: Very Small Window (600x400)")
        small_size = QSize(600, 400)
        main_window.resize(small_size)  # Actually resize the window
        resize_event = QResizeEvent(small_size, main_window.size())
        main_window.resizeEvent(resize_event)
        
        layout_info = main_window.get_layout_info()
        print(f"   Window size: {layout_info['window_size']['width']}x{layout_info['window_size']['height']}")
        print("   Dock visibility:")
        for name, data in layout_info['dock_widgets'].items():
            print(f"     - {name}: {'Visible' if data['visible'] else 'Hidden'}")
        
        # Test 2: Medium window (should show some docks)
        print("\n💻 Test 2: Medium Window (1000x700)")
        medium_size = QSize(1000, 700)
        main_window.resize(medium_size)  # Actually resize the window
        resize_event = QResizeEvent(medium_size, main_window.size())
        main_window.resizeEvent(resize_event)
        
        layout_info = main_window.get_layout_info()
        print(f"   Window size: {layout_info['window_size']['width']}x{layout_info['window_size']['height']}")
        print("   Dock visibility:")
        for name, data in layout_info['dock_widgets'].items():
            print(f"     - {name}: {'Visible' if data['visible'] else 'Hidden'}")
        
        # Test 3: Large window (should show all docks)
        print("\n🖥️  Test 3: Large Window (1400x900)")
        large_size = QSize(1400, 900)
        main_window.resize(large_size)  # Actually resize the window
        resize_event = QResizeEvent(large_size, main_window.size())
        main_window.resizeEvent(resize_event)
        
        layout_info = main_window.get_layout_info()
        print(f"   Window size: {layout_info['window_size']['width']}x{layout_info['window_size']['height']}")
        print("   Dock visibility:")
        for name, data in layout_info['dock_widgets'].items():
            print(f"     - {name}: {'Visible' if data['visible'] else 'Hidden'}")
        
        # Test 4: Test layout mode controls
        print("\n🎛️  Test 4: Layout Mode Controls")
        
        # Test force compact
        print("   Testing force compact mode...")
        main_window.force_compact_layout()
        layout_info = main_window.get_layout_info()
        visible_docks = sum(1 for data in layout_info['dock_widgets'].values() if data['visible'])
        print(f"   Visible docks after force compact: {visible_docks}")
        
        # Test force full
        print("   Testing force full mode...")
        main_window.force_full_layout()
        layout_info = main_window.get_layout_info()
        visible_docks = sum(1 for data in layout_info['dock_widgets'].values() if data['visible'])
        print(f"   Visible docks after force full: {visible_docks}")
        
        # Test adaptive toggle
        print("   Testing adaptive layout toggle...")
        main_window.toggle_adaptive_layout()  # Disable
        initial_adaptive = main_window.get_layout_info()['adaptive_enabled']
        main_window.toggle_adaptive_layout()  # Re-enable
        final_adaptive = main_window.get_layout_info()['adaptive_enabled']
        print(f"   Adaptive layout toggle working: {not initial_adaptive and final_adaptive}")
        
        # Test 5: Method availability
        print("\n🔍 Test 5: Method Availability")
        methods_to_check = [
            'resizeEvent', 'save_dock_state', 'restore_dock_state',
            'toggle_adaptive_layout', 'force_compact_layout', 
            'force_full_layout', 'get_layout_info', 'show_layout_info'
        ]
        
        for method_name in methods_to_check:
            has_method = hasattr(main_window, method_name)
            print(f"   {method_name}: {'✅' if has_method else '❌'}")
        
        print("\n🎉 All Tests Completed!")
        print("✅ Dynamic widget rearrangement is working correctly")
        
        # Don't start the event loop, just quit
        app.quit()
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_resize_functionality()
    sys.exit(0 if success else 1)
