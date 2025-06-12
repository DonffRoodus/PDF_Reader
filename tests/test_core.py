"""
Unit tests for core models and functionality.
"""

import unittest
from src.pdf_reader.core.models import ViewMode


class TestViewMode(unittest.TestCase):
    """Test cases for ViewMode enum."""
    
    def test_view_mode_values(self):
        """Test that all view modes have expected values."""
        self.assertEqual(ViewMode.SINGLE_PAGE.value, 1)
        self.assertEqual(ViewMode.FIT_PAGE.value, 2)
        self.assertEqual(ViewMode.FIT_WIDTH.value, 3)
        self.assertEqual(ViewMode.DOUBLE_PAGE.value, 4)
        self.assertEqual(ViewMode.CONTINUOUS_SCROLL.value, 5)
    
    def test_view_mode_names(self):
        """Test that all view modes have expected names."""
        modes = [mode.name for mode in ViewMode]
        expected_modes = [
            'SINGLE_PAGE', 'FIT_PAGE', 'FIT_WIDTH', 
            'DOUBLE_PAGE', 'CONTINUOUS_SCROLL'
        ]
        self.assertEqual(sorted(modes), sorted(expected_modes))


if __name__ == '__main__':
    unittest.main()
