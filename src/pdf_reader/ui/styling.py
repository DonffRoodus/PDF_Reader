"""Application styling and theme configuration."""


def get_application_stylesheet():
    """Return the main application stylesheet."""
    return """
        QMainWindow {
            background-color: #f0f0f0; /* Light gray background */
        }
        QTabWidget::pane {
            border-top: 2px solid #C2C7CB;
            background: white;
        }
        QTabBar::tab {
            background: #e0e0e0; /* Lighter gray for inactive tabs */
            border: 1px solid #C2C7CB;
            border-bottom-color: #C2C7CB; /* Same as pane border color */
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            min-width: 8ex;
            padding: 5px;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background: white; /* White for active tab */
            border-color: #9B9B9B;
            border-bottom-color: white; /* Make it look like it's part of the pane */
        }
        QTabBar::tab:!selected:hover {
            background: #d0d0d0; /* Slightly darker on hover for inactive tabs */
        }
        QToolBar {
            background: #e8e8e8; /* Slightly darker toolbar */
            border: 1px solid #C2C7CB;
            spacing: 3px; /* Space between items */
        }
        QPushButton, QToolButton {
            background-color: #dcdcdc; /* Light silver */
            border: 1px solid #c0c0c0; /* Silver border */
            padding: 5px;
            border-radius: 3px;
        }
        QPushButton:hover, QToolButton:hover {
            background-color: #c8c8c8; /* Darker silver on hover */
        }
        QPushButton:pressed, QToolButton:pressed {
            background-color: #b0b0b0; /* Even darker when pressed */
        }
        QLabel, QLineEdit {
            padding: 2px;
        }
        QDockWidget {
            titlebar-close-icon: url(close.png); /* Placeholder for icons */
            titlebar-normal-icon: url(float.png); /* Placeholder for icons */
            font-weight: bold;
        }
        QDockWidget::title {
            text-align: left; /* Align the title to the left */
            background: #e0e0e0;
            padding: 5px;
            border: 1px solid #C2C7CB;
        }
        QListView, QListWidget {
            background-color: white;
            border: 1px solid #C2C7CB;
        }
    """
