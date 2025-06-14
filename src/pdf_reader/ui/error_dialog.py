"""Enhanced error dialog and user feedback components for better HCI."""

import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QFrame, QWidget, QApplication
)
from PyQt6.QtGui import QIcon, QPixmap, QFont
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve


class UserFeedbackWidget(QWidget):
    """Non-intrusive feedback widget for status messages and actionable notifications."""
    
    action_requested = pyqtSignal(str)  # Emitted when user clicks an action button
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.hide()  # Hidden by default
        
        self.auto_hide_timer = QTimer()
        self.auto_hide_timer.timeout.connect(self.hide_animated)
        self.auto_hide_timer.setSingleShot(True)
        
        # Animation for smooth show/hide
        self.animation = QPropertyAnimation(self, b"maximumHeight")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
    def setup_ui(self):
        """Set up the feedback widget UI."""
        self.setMaximumHeight(0)  # Start hidden
        self.setStyleSheet("""
            UserFeedbackWidget {
                background-color: #e3f2fd;
                border: 1px solid #90caf9;
                border-radius: 6px;
                margin: 2px;
            }
            UserFeedbackWidget[messageType="warning"] {
                background-color: #fff3e0;
                border-color: #ffb74d;
            }
            UserFeedbackWidget[messageType="error"] {
                background-color: #ffebee;
                border-color: #ef5350;
            }
            UserFeedbackWidget[messageType="success"] {
                background-color: #e8f5e8;
                border-color: #66bb6a;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)
        
        # Icon label
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(24, 24)
        layout.addWidget(self.icon_label)
        
        # Message label
        self.message_label = QLabel()
        self.message_label.setWordWrap(True)
        self.message_label.setStyleSheet("border: none; background: transparent; font-weight: 500;")
        layout.addWidget(self.message_label, 1)
        
        # Action button (optional)
        self.action_button = QPushButton()
        self.action_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #1976d2;
                color: #1976d2;
                padding: 4px 12px;
                border-radius: 4px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #1976d2;
                color: white;
            }
        """)
        self.action_button.clicked.connect(self.on_action_clicked)
        self.action_button.hide()
        layout.addWidget(self.action_button)
        
        # Close button
        self.close_button = QPushButton("×")
        self.close_button.setFixedSize(24, 24)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 16px;
                font-weight: bold;
                color: #666;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
            }
        """)
        self.close_button.clicked.connect(self.hide_animated)
        layout.addWidget(self.close_button)
        
    def show_message(self, message, message_type="info", action_text=None, action_data=None, timeout=5000):
        """Show a feedback message."""
        self.message_label.setText(message)
        self.action_data = action_data
        
        # Set icon based on message type
        icon_map = {
            "info": "ℹ️",
            "warning": "⚠️", 
            "error": "❌",
            "success": "✅"
        }
        self.icon_label.setText(icon_map.get(message_type, "ℹ️"))
        
        # Set message type for styling
        self.setProperty("messageType", message_type)
        self.style().unpolish(self)
        self.style().polish(self)
        
        # Configure action button
        if action_text and action_data:
            self.action_button.setText(action_text)
            self.action_button.show()
        else:
            self.action_button.hide()
        
        # Show with animation
        self.show_animated()
        
        # Auto-hide after timeout
        if timeout > 0:
            self.auto_hide_timer.start(timeout)
    
    def show_animated(self):
        """Show the widget with animation."""
        self.show()
        self.animation.setStartValue(0)
        self.animation.setEndValue(50)  # Adjust height as needed
        self.animation.start()
    
    def hide_animated(self):
        """Hide the widget with animation."""
        self.animation.setStartValue(self.height())
        self.animation.setEndValue(0)
        self.animation.finished.connect(self.hide)
        self.animation.start()
        
    def on_action_clicked(self):
        """Handle action button click."""
        if hasattr(self, 'action_data') and self.action_data:
            self.action_requested.emit(self.action_data)
        self.hide_animated()


class ErrorDialog(QDialog):
    """Enhanced error dialog with detailed information and helpful suggestions."""
    
    def __init__(self, parent=None, title="Error", message="", details="", suggestion=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setMaximumWidth(700)
        
        self.setup_ui(message, details, suggestion)
        
    def setup_ui(self, message, details, suggestion):
        """Set up the error dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Header with icon and message
        header_layout = QHBoxLayout()
        
        # Error icon
        icon_label = QLabel()
        icon_label.setPixmap(self.style().standardIcon(
            self.style().StandardPixmap.SP_MessageBoxCritical
        ).pixmap(48, 48))
        header_layout.addWidget(icon_label)
        
        # Message
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        font = QFont()
        font.setPointSize(12)
        font.setWeight(QFont.Weight.Medium)
        message_label.setFont(font)
        header_layout.addWidget(message_label, 1)
        
        layout.addLayout(header_layout)
        
        # Details section
        if details:
            details_frame = QFrame()
            details_frame.setFrameStyle(QFrame.Shape.Box)
            details_frame.setStyleSheet("""
                QFrame {
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 6px;
                    padding: 12px;
                }
            """)
            
            details_layout = QVBoxLayout(details_frame)
            
            details_title = QLabel("Technical Details:")
            details_title.setStyleSheet("font-weight: bold; color: #495057;")
            details_layout.addWidget(details_title)
            
            details_text = QLabel(details)
            details_text.setWordWrap(True)
            details_text.setStyleSheet("color: #6c757d; font-family: monospace;")
            details_layout.addWidget(details_text)
            
            layout.addWidget(details_frame)
        
        # Suggestion section
        if suggestion:
            suggestion_frame = QFrame()
            suggestion_frame.setStyleSheet("""
                QFrame {
                    background-color: #e8f4fd;
                    border: 1px solid #bee5eb;
                    border-radius: 6px;
                    padding: 12px;
                }
            """)
            
            suggestion_layout = QVBoxLayout(suggestion_frame)
            
            suggestion_title = QLabel("💡 Suggestion:")
            suggestion_title.setStyleSheet("font-weight: bold; color: #0c5460;")
            suggestion_layout.addWidget(suggestion_title)
            
            suggestion_text = QLabel(suggestion)
            suggestion_text.setWordWrap(True)
            suggestion_text.setStyleSheet("color: #0c5460;")
            suggestion_layout.addWidget(suggestion_text)
            
            layout.addWidget(suggestion_frame)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Copy details button
        if details:
            copy_button = QPushButton("Copy Details")
            copy_button.clicked.connect(lambda: self.copy_to_clipboard(details))
            copy_button.setStyleSheet("""
                QPushButton {
                    background-color: #6c757d;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #5a6268;
                }
            """)
            button_layout.addWidget(copy_button)
        
        # OK button
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        ok_button.setDefault(True)
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #0d6efd;
                color: white;
                border: none;
                padding: 8px 24px;
                border-radius: 4px;
                font-weight: 500;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #0b5ed7;
            }
        """)
        button_layout.addWidget(ok_button)
        
        layout.addLayout(button_layout)
        
    def copy_to_clipboard(self, text):
        """Copy text to clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        
        # Show brief feedback
        self.setWindowTitle("Error - Copied to clipboard")
        QTimer.singleShot(1000, lambda: self.setWindowTitle("Error"))


def show_error_dialog(parent, title, message, details="", suggestion=""):
    """Show an enhanced error dialog."""
    dialog = ErrorDialog(parent, title, message, details, suggestion)
    dialog.exec()
