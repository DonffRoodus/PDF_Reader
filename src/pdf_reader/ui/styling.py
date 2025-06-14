"""Application styling and theme configuration with improved HCI design."""


def get_application_stylesheet():
    """Return the main application stylesheet with eye-friendly, warm design for comfortable reading."""
    return """
        /* Main Window and Layout */
        QMainWindow {
            background-color: #faf8f3; /* Warm, cream background */
            color: #3d3833; /* Soft dark brown text */
        }
          /* Tab Widget Styling */
        QTabWidget::pane {
            border: 2px solid #e6ddd4;
            background: #fefcf9;
            border-radius: 4px;
        }
        
        QTabBar::tab {
            background: #f2ede6;
            border: 1px solid #e6ddd4;
            border-bottom: none;
            border-radius: 6px 6px 0 0;
            min-width: 100px;
            padding: 8px 16px;
            margin-right: 2px;
            font-weight: 500;
            color: #5d564d;
        }
        
        QTabBar::tab:selected {
            background: #fefcf9;
            border-color: #8b7355;
            border-bottom: 2px solid #fefcf9;
            color: #8b7355;
            font-weight: 600;
        }
        
        QTabBar::tab:hover:!selected {
            background: #eee8e0;
            color: #3d3833;
        }
          QTabBar::close-button {
            subcontrol-position: right;
            margin: 2px;
            border: 1px solid transparent;
            border-radius: 3px;
            width: 12px;
            height: 12px;
        }
          /* Toolbar Styling */
        QToolBar {
            background: linear-gradient(to bottom, #fefcf9, #faf8f3);
            border: 1px solid #e6ddd4;
            border-radius: 4px;
            spacing: 6px;
            padding: 4px;
            min-height: 48px;
        }
        
        QToolBar::separator {
            background: #e6ddd4;
            width: 1px;
            margin: 8px 4px;
        }
        
        /* Button Styling */
        QPushButton, QToolButton {
            background-color: #fefcf9;
            border: 1px solid #d9cfc3;
            padding: 8px 12px;
            border-radius: 6px;
            font-weight: 500;
            color: #5d564d;
            min-width: 80px;
        }
        
        QPushButton:hover, QToolButton:hover {
            background-color: #f2ede6;
            border-color: #c7b8a8;
            color: #3d3833;
        }
        
        QPushButton:pressed, QToolButton:pressed {
            background-color: #eee8e0;
            border-color: #a89885;
        }
        
        QPushButton:disabled, QToolButton:disabled {
            background-color: #faf8f3;
            border-color: #f2ede6;
            color: #c7b8a8;
        }
        
        /* Primary action buttons */
        QPushButton[primary="true"] {
            background-color: #8b7355;
            border-color: #8b7355;
            color: #fefcf9;
        }
        
        QPushButton[primary="true"]:hover {
            background-color: #7a6549;
            border-color: #6f5a42;
        }
          /* Input Fields */
        QLineEdit {
            background-color: #fefcf9;
            border: 2px solid #d9cfc3;
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 14px;
            color: #5d564d;
        }        
        QLineEdit:focus {
            border-color: #b8a082;
            outline: none;
        }
        
        QLineEdit:disabled {
            background-color: #f2ede6;
            color: #a89885;
        }
        
        QLineEdit::placeholder {
            color: #c7b8a8;
        }
        
        /* Labels */
        QLabel {
            color: #5d564d;
            font-weight: 500;
        }
          /* Status Bar */
        QStatusBar {
            background: linear-gradient(to bottom, #faf8f3, #f2ede6);
            border-top: 1px solid #e6ddd4;
            color: #5d564d;
            font-size: 13px;
        }
        
        QStatusBar::item {
            border: none;
        }
        
        /* Progress Bar */
        QProgressBar {
            border: 2px solid #e6ddd4;
            border-radius: 6px;
            background-color: #faf8f3;
            text-align: center;
            font-weight: 500;
        }
        
        QProgressBar::chunk {
            background-color: #8b7355;
            border-radius: 4px;
        }
          /* Dock Widgets */
        QDockWidget {
            font-weight: 600;
            color: #5d564d;
        }
        
        QDockWidget::title {
            background: linear-gradient(to bottom, #faf8f3, #f2ede6);
            border: 1px solid #e6ddd4;
            border-radius: 4px 4px 0 0;
            padding: 8px;
            text-align: center;
            font-weight: 600;
        }
        
        QDockWidget::close-button, QDockWidget::float-button {
            border: 1px solid transparent;
            border-radius: 3px;
            background: transparent;
            padding: 2px;
        }
        
        QDockWidget::close-button:hover, QDockWidget::float-button:hover {
            background: #eee8e0;
        }
          /* List Views */
        QListView, QListWidget {
            background-color: #fefcf9;
            border: 1px solid #e6ddd4;
            border-radius: 6px;
            selection-background-color: #e8dcc9;
            alternate-background-color: #faf8f3;
            outline: none;
        }
        
        QListView::item, QListWidget::item {
            padding: 8px 12px;
            border-bottom: 1px solid #f2ede6;
            color: #5d564d;
        }
        
        QListView::item:selected, QListWidget::item:selected {
            background: #e8dcc9;
            color: #8b7355;
            border-color: #d4c3a7;
        }
        
        QListView::item:hover, QListWidget::item:hover {
            background: #faf8f3;
        }
          /* Menu Bar and Menus */
        QMenuBar {
            background: #fefcf9;
            border-bottom: 1px solid #e6ddd4;
            padding: 4px;
        }
        
        QMenuBar::item {
            background: transparent;
            padding: 8px 12px;
            border-radius: 4px;
            color: #5d564d;
        }
        
        QMenuBar::item:selected {
            background: #f2ede6;
            color: #3d3833;
        }        
        QMenu {
            background: #fefcf9;
            border: 1px solid #e6ddd4;
            border-radius: 6px;
            padding: 4px;
        }
        
        QMenu::item {
            padding: 8px 24px;
            border-radius: 4px;
            color: #5d564d;
        }
        
        QMenu::item:selected {
            background: #f2ede6;
            color: #3d3833;
        }
        
        QMenu::item:disabled {
            color: #c7b8a8;
        }
        
        QMenu::separator {
            height: 1px;
            background: #e6ddd4;
            margin: 4px 8px;
        }
          /* Scroll Bars */
        QScrollBar:vertical {
            background: #faf8f3;
            width: 16px;
            border-radius: 8px;
        }
        
        QScrollBar::handle:vertical {
            background: #d9cfc3;
            border-radius: 8px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background: #c7b8a8;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            border: none;
            background: none;
        }
        
        QScrollBar:horizontal {
            background: #faf8f3;
            height: 16px;
            border-radius: 8px;
        }
        
        QScrollBar::handle:horizontal {
            background: #d9cfc3;
            border-radius: 8px;
            min-width: 20px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background: #c7b8a8;
        }
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            border: none;
            background: none;
        }
          /* Message Boxes */
        QMessageBox {
            background: #fefcf9;
            color: #5d564d;
        }
        
        QMessageBox QLabel {
            color: #5d564d;
        }
        
        /* Tooltips */
        QToolTip {
            background: #3d3833;
            color: #fefcf9;
            border: 1px solid #5d564d;
            border-radius: 4px;
            padding: 6px 8px;
            font-size: 12px;
        }
          /* Accessibility improvements */
        *:focus {
            outline: 2px solid #b8a082;
            outline-offset: 2px;
        }
    """
