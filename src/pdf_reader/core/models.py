"""Core models and data structures for the PDF Reader."""

from enum import Enum
from dataclasses import dataclass
from typing import Optional
from PyQt6.QtCore import QPoint


class ViewMode(Enum):
    """Enumeration of available view modes for PDF display."""
    SINGLE_PAGE = 1        # Default, respects manual zoom_factor
    FIT_PAGE = 2          # Zooms to fit entire page in view
    FIT_WIDTH = 3         # Zooms to fit page width in view
    DOUBLE_PAGE = 4       # Shows two pages side-by-side
    CONTINUOUS_SCROLL = 5 # All pages in a long scrollable view
    # Future: CONTINUOUS_DOUBLE_PAGE


class AnnotationType(Enum):
    """Enumeration of available annotation types."""
    HIGHLIGHT = 1
    UNDERLINE = 2
    TEXT = 3


@dataclass
class Bookmark:
    """Represents a bookmark in a PDF document."""
    title: str
    page_number: int  # 0-based page number
    file_path: str
    created_at: Optional[str] = None  # ISO format timestamp
    
    def display_title(self) -> str:
        """Get the display title for the bookmark."""
        return f"{self.title} (Page {self.page_number + 1})"


@dataclass
class Annotation:
    """Represents an annotation in a PDF document."""
    type: AnnotationType
    page: int
    start: QPoint
    end: QPoint = None
    text: str = None
    
    def __post_init__(self):
        """Initialize default values after creation."""
        if self.end is None:
            self.end = self.start
        if self.type != AnnotationType.TEXT:
            self.text = None
