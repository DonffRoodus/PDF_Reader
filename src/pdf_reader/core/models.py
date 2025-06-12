"""Core models and data structures for the PDF Reader."""

from enum import Enum


class ViewMode(Enum):
    """Enumeration of available view modes for PDF display."""
    SINGLE_PAGE = 1        # Default, respects manual zoom_factor
    FIT_PAGE = 2          # Zooms to fit entire page in view
    FIT_WIDTH = 3         # Zooms to fit page width in view
    DOUBLE_PAGE = 4       # Shows two pages side-by-side
    CONTINUOUS_SCROLL = 5 # All pages in a long scrollable view
    # Future: CONTINUOUS_DOUBLE_PAGE
