"""Application styling and theme configuration with improved HCI design."""


def get_application_stylesheet():
    """Return the main application stylesheet with modern, accessible design."""
    return """
        /* Main Window and Layout */
        QMainWindow {
            background-color: #f8f9fa; /* Light, modern background */
            color: #212529; /* High contrast text */
        }
        
        /* Tab Widget Styling */
        QTabWidget::pane {
            border: 2px solid #dee2e6;
            background: #ffffff;
            border-radius: 4px;
        }
        
        QTabBar::tab {
            background: #e9ecef;
            border: 1px solid #dee2e6;
            border-bottom: none;
            border-radius: 6px 6px 0 0;
            min-width: 100px;
            padding: 8px 16px;
            margin-right: 2px;
            font-weight: 500;
            color: #495057;
        }
        
        QTabBar::tab:selected {
            background: #ffffff;
            border-color: #0d6efd;
            border-bottom: 2px solid #ffffff;
            color: #0d6efd;
            font-weight: 600;
        }
        
        QTabBar::tab:hover:!selected {
            background: #dee2e6;
            color: #212529;
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
            background: linear-gradient(to bottom, #ffffff, #f8f9fa);
            border: 1px solid #dee2e6;
            border-radius: 4px;
            spacing: 6px;
            padding: 4px;
            min-height: 48px;
        }
        
        QToolBar::separator {
            background: #dee2e6;
            width: 1px;
            margin: 8px 4px;
        }
        
        /* Button Styling */
        QPushButton, QToolButton {
            background-color: #ffffff;
            border: 1px solid #ced4da;
            padding: 8px 12px;
            border-radius: 6px;
            font-weight: 500;
            color: #495057;
            min-width: 80px;
        }
        
        QPushButton:hover, QToolButton:hover {
            background-color: #e9ecef;
            border-color: #adb5bd;
            color: #212529;
        }
        
        QPushButton:pressed, QToolButton:pressed {
            background-color: #dee2e6;
            border-color: #6c757d;
        }
        
        QPushButton:disabled, QToolButton:disabled {
            background-color: #f8f9fa;
            border-color: #e9ecef;
            color: #adb5bd;
        }
        
        /* Primary action buttons */
        QPushButton[primary="true"] {
            background-color: #0d6efd;
            border-color: #0d6efd;
            color: white;
        }
        
        QPushButton[primary="true"]:hover {
            background-color: #0b5ed7;
            border-color: #0a58ca;
        }
        
        /* Input Fields */
        QLineEdit {
            background-color: #ffffff;
            border: 2px solid #ced4da;
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 14px;
            color: #495057;
        }        
        QLineEdit:focus {
            border-color: #86b7fe;
            outline: none;
        }
        
        QLineEdit:disabled {
            background-color: #e9ecef;
            color: #6c757d;
        }
        
        QLineEdit::placeholder {
            color: #adb5bd;
        }
        
        /* Labels */
        QLabel {
            color: #495057;
            font-weight: 500;
        }
        
        /* Status Bar */
        QStatusBar {
            background: linear-gradient(to bottom, #f8f9fa, #e9ecef);
            border-top: 1px solid #dee2e6;
            color: #495057;
            font-size: 13px;
        }
        
        QStatusBar::item {
            border: none;
        }
        
        /* Progress Bar */
        QProgressBar {
            border: 2px solid #dee2e6;
            border-radius: 6px;
            background-color: #f8f9fa;
            text-align: center;
            font-weight: 500;
        }
        
        QProgressBar::chunk {
            background-color: #0d6efd;
            border-radius: 4px;
        }
        
        /* Dock Widgets */
        QDockWidget {
            font-weight: 600;
            color: #495057;
        }
        
        QDockWidget::title {
            background: linear-gradient(to bottom, #f8f9fa, #e9ecef);
            border: 1px solid #dee2e6;
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
            background: #dee2e6;
        }
        
        /* List Views */
        QListView, QListWidget {
            background-color: #ffffff;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            selection-background-color: #cfe2ff;
            alternate-background-color: #f8f9fa;
            outline: none;
        }
        
        QListView::item, QListWidget::item {
            padding: 8px 12px;
            border-bottom: 1px solid #f1f3f4;
            color: #495057;
        }
        
        QListView::item:selected, QListWidget::item:selected {
            background: #cfe2ff;
            color: #0d6efd;
            border-color: #9ec5fe;
        }
        
        QListView::item:hover, QListWidget::item:hover {
            background: #f8f9fa;
        }
        
        /* Menu Bar and Menus */
        QMenuBar {
            background: #ffffff;
            border-bottom: 1px solid #dee2e6;
            padding: 4px;
        }
        
        QMenuBar::item {
            background: transparent;
            padding: 8px 12px;
            border-radius: 4px;
            color: #495057;
        }
        
        QMenuBar::item:selected {
            background: #e9ecef;
            color: #212529;
        }        
        QMenu {
            background: #ffffff;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 4px;
        }
        
        QMenu::item {
            padding: 8px 24px;
            border-radius: 4px;
            color: #495057;
        }
        
        QMenu::item:selected {
            background: #e9ecef;
            color: #212529;
        }
        
        QMenu::item:disabled {
            color: #adb5bd;
        }
        
        QMenu::separator {
            height: 1px;
            background: #dee2e6;
            margin: 4px 8px;
        }
        
        /* Scroll Bars */
        QScrollBar:vertical {
            background: #f8f9fa;
            width: 16px;
            border-radius: 8px;
        }
        
        QScrollBar::handle:vertical {
            background: #ced4da;
            border-radius: 8px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background: #adb5bd;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            border: none;
            background: none;
        }
        
        QScrollBar:horizontal {
            background: #f8f9fa;
            height: 16px;
            border-radius: 8px;
        }
        
        QScrollBar::handle:horizontal {
            background: #ced4da;
            border-radius: 8px;
            min-width: 20px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background: #adb5bd;
        }
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            border: none;
            background: none;
        }
        
        /* Message Boxes */
        QMessageBox {
            background: #ffffff;
            color: #495057;
        }
        
        QMessageBox QLabel {
            color: #495057;
        }
        
        /* Tooltips */
        QToolTip {
            background: #212529;
            color: #ffffff;
            border: 1px solid #495057;
            border-radius: 4px;
            padding: 6px 8px;
            font-size: 12px;
        }
          /* Accessibility improvements */
        *:focus {
            outline: 2px solid #86b7fe;
            outline-offset: 2px;
        }
    """
