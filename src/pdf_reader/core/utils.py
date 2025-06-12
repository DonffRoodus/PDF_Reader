"""Utility functions for the PDF Reader application."""

import os
import sys
import logging
from pathlib import Path
from typing import List, Tuple, Optional
from PyQt6.QtCore import QStandardPaths
from PyQt6.QtGui import QPixmap, QIcon


def setup_logging(debug_mode: bool = False) -> logging.Logger:
    """
    Set up logging for the application.
    
    Args:
        debug_mode: Enable debug logging if True
        
    Returns:
        Configured logger instance
    """
    log_level = logging.DEBUG if debug_mode else logging.INFO
    
    # Create logs directory
    log_dir = Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)) / "pdf_reader" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "pdf_reader.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger("pdf_reader")


def get_application_icon() -> QIcon:
    """
    Get the main application icon.
    
    Returns:
        QIcon instance for the application
    """
    from .config import ICONS_DIR
    
    icon_path = ICONS_DIR / "app_icon.png"
    if icon_path.exists():
        return QIcon(str(icon_path))
    
    # Return default icon if custom icon not found
    return QIcon()


def get_toolbar_icon(icon_name: str) -> QIcon:
    """
    Get a toolbar icon by name.
    
    Args:
        icon_name: Name of the icon (without extension)
        
    Returns:
        QIcon instance for the toolbar
    """
    from .config import ICONS_DIR
    
    # Try different formats
    for ext in ['.svg', '.png', '.ico']:
        icon_path = ICONS_DIR / f"{icon_name}{ext}"
        if icon_path.exists():
            return QIcon(str(icon_path))
    
    # Fallback to system theme icon
    return QIcon.fromTheme(icon_name)


def validate_pdf_file(file_path: str) -> bool:
    """
    Validate if the given file path is a valid PDF file.
    
    Args:
        file_path: Path to the file to validate
        
    Returns:
        True if the file exists and has a .pdf extension, False otherwise
    """
    if not file_path:
        return False
        
    path = Path(file_path)
    return path.exists() and path.suffix.lower() == '.pdf'


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in bytes to human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB", "342 KB")
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"


def get_file_info(file_path: str) -> dict:
    """
    Get basic information about a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary containing file information
    """
    if not os.path.exists(file_path):
        return {}
    
    stat = os.stat(file_path)
    return {
        'name': os.path.basename(file_path),
        'path': file_path,
        'size': stat.st_size,
        'size_formatted': format_file_size(stat.st_size),
        'modified': stat.st_mtime,
    }


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Clamp a value between minimum and maximum bounds.
    
    Args:
        value: Value to clamp
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        Clamped value
    """
    return max(min_val, min(value, max_val))


def calculate_zoom_to_fit(content_size: Tuple[int, int], viewport_size: Tuple[int, int]) -> float:
    """
    Calculate zoom factor to fit content within viewport.
    
    Args:
        content_size: (width, height) of content
        viewport_size: (width, height) of viewport
        
    Returns:
        Zoom factor to fit content in viewport
    """
    if content_size[0] == 0 or content_size[1] == 0:
        return 1.0
    
    zoom_x = viewport_size[0] / content_size[0]
    zoom_y = viewport_size[1] / content_size[1]
    
    return min(zoom_x, zoom_y)


def calculate_zoom_to_fit_width(content_width: int, viewport_width: int) -> float:
    """
    Calculate zoom factor to fit content width within viewport width.
    
    Args:
        content_width: Width of content
        viewport_width: Width of viewport
        
    Returns:
        Zoom factor to fit content width in viewport
    """
    if content_width == 0:
        return 1.0
    
    return viewport_width / content_width
