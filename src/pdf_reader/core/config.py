"""Configuration and constants for the PDF Reader application."""

import os
import json
from pathlib import Path
from typing import Dict, Any

# Application information
APP_NAME = "PDF Reader"
APP_VERSION = "1.0.0"
APP_AUTHOR = "HCI Course Project"

# Default settings
DEFAULT_ZOOM_FACTOR = 1.0
ZOOM_STEP = 1.2
MAX_RECENT_FILES = 10

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
        recent_files = recent_files[:max_recent]
        
        self.set('files.recent_files', recent_files)


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
