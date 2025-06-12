"""
Integration tests for UI components.
"""

import unittest
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest
from PyQt6.QtCore import Qt

from src.pdf_reader.ui.main_window import MainWindow
from src.pdf_reader.core.models import ViewMode


class TestMainWindow(unittest.TestCase):
    """Test cases for MainWindow class."""
    
    @classmethod
    def setUpClass(cls):
        """Set up QApplication for testing."""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Set up test fixtures."""
        self.main_window = MainWindow()
    
    def tearDown(self):
        """Clean up after tests."""
        self.main_window.close()
    
    def test_window_initialization(self):
        """Test that the main window initializes correctly."""
        self.assertIsNotNone(self.main_window)
        self.assertEqual(self.main_window.windowTitle(), "PDF Reader")
        self.assertEqual(self.main_window.tab_widget.count(), 0)
    
    def test_menu_creation(self):
        """Test that menus are created correctly."""
        menubar = self.main_window.menuBar()
        menu_titles = [action.text() for action in menubar.actions()]
        
        expected_menus = ["&File", "&View Modes", "&Panels"]
        for menu in expected_menus:
            self.assertIn(menu, menu_titles)
    
    def test_view_mode_actions(self):
        """Test that view mode actions are properly set up."""
        self.assertTrue(self.main_window.single_page_action.isCheckable())
        self.assertTrue(self.main_window.fit_page_action.isCheckable())
        self.assertTrue(self.main_window.fit_width_action.isCheckable())
        self.assertTrue(self.main_window.double_page_action.isCheckable())
        self.assertTrue(self.main_window.continuous_scroll_action.isCheckable())
        
        # Default should be single page
        self.assertTrue(self.main_window.single_page_action.isChecked())


if __name__ == '__main__':
    unittest.main()
