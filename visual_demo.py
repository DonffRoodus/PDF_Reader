#!/usr/bin/env python3
"""
Visual demo of the dynamic widget rearrangement.
This script actually shows the PDF reader window so you can see the layout changes.
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer, QSize
from PyQt6.QtGui import QResizeEvent

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def run_visual_demo():
    """Run a visual demonstration of the resize functionality."""
    try:
        from src.pdf_reader.ui.main_window import MainWindow
        
        app = QApplication(sys.argv)
        
        # Create main window
        main_window = MainWindow()
        main_window.show()
        
        print("🎬 Visual Demo of Dynamic Widget Rearrangement")
        print("=" * 50)
        print("📺 Watch the main window as it automatically resizes and rearranges widgets...")
        
        def demo_sequence():
            """Demonstrate different window sizes automatically."""
            sizes = [
                (600, 400, "📱 Very Small (600x400) - All docks should hide"),
                (900, 600, "📱 Small but taller (900x600) - Only annotations should show at bottom"),
                (1100, 700, "💻 Medium (1100x700) - Bookmarks and annotations should show"),
                (1500, 900, "🖥️  Large (1500x900) - All docks should show optimally positioned"),
                (1200, 500, "📺 Wide but short (1200x500) - Layout adjusts for height constraint"),
            ]
            
            current_index = [0]  # Use list to allow modification in nested function
            
            def resize_demo():
                if current_index[0] < len(sizes):
                    width, height, description = sizes[current_index[0]]
                    print(f"\n{current_index[0] + 1}. {description}")
                    
                    main_window.resize(width, height)
                    
                    # Also trigger our custom resize event
                    new_size = QSize(width, height)
                    resize_event = QResizeEvent(new_size, main_window.size())
                    main_window.resizeEvent(resize_event)
                    
                    # Show layout info
                    layout_info = main_window.get_layout_info()
                    print(f"   Window: {layout_info['window_size']['width']}x{layout_info['window_size']['height']}")
                    for name, data in layout_info['dock_widgets'].items():
                        area_names = {1: "Left", 2: "Right", 4: "Top", 8: "Bottom"}
                        area = area_names.get(data['area'], "Unknown") if data['area'] else ""
                        status = f"Visible ({area})" if data['visible'] else "Hidden"
                        print(f"   {name.title()}: {status}")
                    
                    current_index[0] += 1
                    # Schedule next resize in 3 seconds
                    QTimer.singleShot(3000, resize_demo)
                else:
                    print(f"\n🎯 Demo complete! Window is now in large layout mode.")
                    print(f"💡 Try manually resizing the window to see live adaptation!")
                    print(f"🎛️  Use View → Layout menu to control adaptive behavior")
            
            # Start the demo sequence
            resize_demo()
        
        # Start demo after a short delay
        QTimer.singleShot(1000, demo_sequence)
        
        # Show instructions
        print(f"")
        print(f"🎮 Interactive Controls:")
        print(f"• View → Layout → Adaptive Layout: Toggle automatic adaptation")
        print(f"• View → Layout → Force Compact: Force compact mode")
        print(f"• View → Layout → Force Full: Force full mode")
        print(f"• View → Layout → Show Layout Info: See current layout details")
        print(f"")
        print(f"🎯 What to watch for:")
        print(f"• Dock widgets hiding/showing based on window size")
        print(f"• Dock widgets moving to different areas (left/right/bottom)")
        print(f"• Toolbar icons changing size and style")
        print(f"• Tab styling becoming more compact")
        print(f"• Status bar messages indicating layout changes")
        print(f"")
        print(f"▶️  Demo starting in 1 second...")
        
        return app.exec()
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = run_visual_demo()
    sys.exit(exit_code)
