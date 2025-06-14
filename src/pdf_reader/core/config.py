"""Configuration and constants for the PDF Reader application."""

import os
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Application information
APP_NAME = "PDF Reader"
APP_VERSION = "1.0.0"
APP_AUTHOR = "HCI Course Project"

# Default settings
DEFAULT_ZOOM_FACTOR = 1.0
ZOOM_STEP = 1.2
MAX_RECENT_FILES = 10
MAX_RECENT_DOCUMENTS = 5  # Maximum number of recent documents to track

# Performance settings
CONTINUOUS_SCROLL_BUFFER_PAGES = 2  # Pages to render around visible area
VIRTUALIZATION_ENABLED = True

# UI settings
DEFAULT_WINDOW_WIDTH = 1200
DEFAULT_WINDOW_HEIGHT = 800
TOOLBAR_ICON_SIZE = 24

# File paths and directories
ASSETS_DIR = Path(__file__).parent.parent.parent.parent / "assets"
ICONS_DIR = ASSETS_DIR / "icons"
THEMES_DIR = ASSETS_DIR / "themes"

# Configuration directory
CONFIG_DIR = Path.home() / ".pdf_reader"
CONFIG_FILE = CONFIG_DIR / "config.json"


class Config:
    """Configuration management class."""
    
    def __init__(self):
        self._config = self._load_default_config()
        self.load()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration values."""
        return {
            "window": {
                "width": DEFAULT_WINDOW_WIDTH,
                "height": DEFAULT_WINDOW_HEIGHT,
                "maximized": False,
            },
            "viewer": {
                "default_zoom": DEFAULT_ZOOM_FACTOR,
                "zoom_step": ZOOM_STEP,
                "virtualization": VIRTUALIZATION_ENABLED,
                "buffer_pages": CONTINUOUS_SCROLL_BUFFER_PAGES,
            },
            "ui": {
                "toolbar_icon_size": TOOLBAR_ICON_SIZE,
                "theme": "default",
            },
            "files": {
                "max_recent": MAX_RECENT_FILES,
                "recent_files": [],
            },
            "document_history": {
                "documents": {},  # file_path: {"last_page": int, "last_opened": str, "total_pages": int}
                "recent_documents": []  # List of recently opened documents with reading progress
            },
            "app": {
                "first_run": True
            }
        }
    
    def load(self):
        """Load configuration from file."""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                self._merge_config(saved_config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config: {e}")
    
    def save(self):
        """Save configuration to file."""
        CONFIG_DIR.mkdir(exist_ok=True)
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2)
        except IOError as e:
            print(f"Error saving config: {e}")

    def _merge_config(self, saved_config: Dict[str, Any]):
        """Merge saved configuration with defaults."""
        def merge_dict(default, saved):
            for key, value in saved.items():
                if key in default:
                    if isinstance(default[key], dict) and isinstance(value, dict):
                        merge_dict(default[key], value)
                    else:
                        default[key] = value
                else:
                    # Allow new keys to be added to dictionaries (especially for documents)
                    default[key] = value
        
        merge_dict(self._config, saved_config)
    
    def get(self, key_path: str, default=None):
        """Get configuration value using dot notation (e.g., 'window.width')."""
        keys = key_path.split('.')
        value = self._config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any):
        """Set configuration value using dot notation."""
        keys = key_path.split('.')
        config = self._config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
    
    def get_recent_files(self):
        """Get list of recent files."""
        return self.get('files.recent_files', [])
    
    def add_recent_file(self, file_path: str):
        """Add a file to the recent files list."""
        recent_files = self.get_recent_files()
        
        # Remove if already exists
        if file_path in recent_files:
            recent_files.remove(file_path)
        
        # Add to beginning
        recent_files.insert(0, file_path)
        
        # Limit to max recent files
        max_recent = self.get('files.max_recent', MAX_RECENT_FILES)
        if len(recent_files) > max_recent:
            recent_files = recent_files[:max_recent]
        
        self.set('files.recent_files', recent_files)

    def clear_recent_files(self):
        """Clear the recent files list."""
        self._config["files"]["recent_files"] = []

    def is_first_run(self):
        """Check if this is the first run of the application."""
        return self._config.get("app", {}).get("first_run", True)

    def mark_first_run_complete(self):
        """Mark that the first run has been completed."""
        if "app" not in self._config:
            self._config["app"] = {}
        self._config["app"]["first_run"] = False

    def save_ui_preferences(self, show_bookmarks_panel=False, show_toc_panel=False):
        """Save UI panel preferences."""
        if "ui" not in self._config:
            self._config["ui"] = {}
        self._config["ui"]["show_bookmarks_panel"] = show_bookmarks_panel
        self._config["ui"]["show_toc_panel"] = show_toc_panel

    def get_recent_documents(self) -> List[Dict]:
        """Get list of recent documents with reading progress."""
        return self.get('document_history.recent_documents', [])
    
    def update_document_progress(self, file_path: str, current_page: int, total_pages: int):
        """Update reading progress for a document."""
        documents = self.get_document_history()
        timestamp = datetime.now().isoformat()
        
        # Update or create document entry
        documents[file_path] = {
            "last_page": current_page,
            "last_opened": timestamp,
            "total_pages": total_pages
        }
        
        self.set('document_history.documents', documents)
        
        # Update recent documents list
        self._update_recent_documents(file_path, current_page, total_pages, timestamp)
    
    def _update_recent_documents(self, file_path: str, current_page: int, total_pages: int, timestamp: str):
        """Update the recent documents list with current document."""
        recent_docs = self.get_recent_documents()
        
        # Remove existing entry for this document
        recent_docs = [doc for doc in recent_docs if doc.get('file_path') != file_path]
        
        # Create new entry
        doc_entry = {
            "file_path": file_path,
            "filename": os.path.basename(file_path),
            "last_page": current_page,
            "total_pages": total_pages,
            "last_opened": timestamp,
            "progress_percent": round((current_page / max(total_pages, 1)) * 100, 1)
        }
          # Add to beginning of list
        recent_docs.insert(0, doc_entry)
        # Keep only the most recent documents
        recent_docs = recent_docs[:MAX_RECENT_DOCUMENTS]
        
        self.set('document_history.recent_documents', recent_docs)

    def get_document_history(self):
        """Get the document history dictionary."""
        return self._config.get("document_history", {}).get("documents", {})

    def get_last_page(self, file_path: str) -> int:
        """Get the last read page for a document."""
        documents = self.get_document_history()
        return documents.get(file_path, {}).get('last_page', 0)
    
    def remove_document_from_history(self, file_path: str):
        """Remove a document from reading history."""
        # Remove from documents history
        documents = self.get_document_history()
        if file_path in documents:
            del documents[file_path]
            self.set('document_history.documents', documents)
        
        # Remove from recent documents
        recent_docs = self.get_recent_documents()
        recent_docs = [doc for doc in recent_docs if doc.get('file_path') != file_path]
        self.set('document_history.recent_documents', recent_docs)
        
    def get_window_state(self):
        """Get window state with defaults."""
        window_config = self._config.get("window", {})
        return {
            "width": window_config.get("width", DEFAULT_WINDOW_WIDTH),
            "height": window_config.get("height", DEFAULT_WINDOW_HEIGHT),
            "x": window_config.get("x", 100),
            "y": window_config.get("y", 100),
            "maximized": window_config.get("maximized", False)
        }

    def save_window_state(self, width, height, x, y, maximized):
        """Save window state."""
        if "window" not in self._config:
            self._config["window"] = {}
        self._config["window"].update({
            "width": width,
            "height": height,
            "x": x,
            "y": y,
            "maximized": maximized
        })


# Global configuration instance
config = Config()

# File filters
PDF_FILE_FILTER = "PDF Files (*.pdf)"

# Color scheme
COLORS = {
    'background': '#f0f0f0',
    'canvas_background': '#e0e0e0',
    'continuous_background': '#d0d0d0',
    'tab_active': 'white',
    'tab_inactive': '#e0e0e0',
    'toolbar': '#e8e8e8',
    'button': '#dcdcdc',
    'button_hover': '#c8c8c8',
    'button_pressed': '#b0b0b0',
}
