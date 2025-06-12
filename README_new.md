# PDF Reader

A modern, feature-rich PDF reader application built with PyQt6 and PyMuPDF. This application provides multiple viewing modes, intuitive navigation, and a clean, user-friendly interface.

## Features

- **Multiple View Modes**:
  - Single page view
  - Double page view
  - Continuous scroll view
  - Fit to page/width modes

- **Navigation**:
  - Page-by-page navigation
  - Jump to specific pages
  - Table of contents support
  - Recent files management

- **User Interface**:
  - Tabbed interface for multiple documents
  - Customizable toolbar
  - Dockable panels (TOC, bookmarks)
  - Modern, responsive design

- **Performance**:
  - Virtualized rendering for large documents
  - Memory-efficient page management
  - Fast zoom and scroll operations

## Project Structure

```
PDF_Reader/
├── app.py                  # Main application entry point
├── main.py                 # Legacy entry point (deprecated)
├── setup.py               # Package installation script
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── run.bat               # Windows batch script to run the app
├── assets/               # Static resources
│   ├── icons/           # Application icons
│   └── themes/          # UI themes and stylesheets
├── docs/                # Documentation
│   ├── README.md        # Documentation index
│   ├── architecture.md  # Architecture overview
│   ├── getting-started.md # Installation and setup
│   ├── development.md   # Development guide
│   └── user-manual.md   # User manual
├── src/                 # Source code
│   └── pdf_reader/      # Main package
│       ├── __init__.py  # Package initialization
│       ├── __main__.py  # Package entry point
│       ├── core/        # Core components
│       │   ├── __init__.py
│       │   ├── config.py    # Configuration management
│       │   ├── models.py    # Data models and enums
│       │   └── utils.py     # Utility functions
│       └── ui/          # User interface components
│           ├── __init__.py
│           ├── main_window.py  # Main application window
│           ├── pdf_viewer.py   # PDF viewing widget
│           └── styling.py      # UI themes and styles
└── tests/               # Test suite
    ├── __init__.py
    ├── test_core.py     # Core component tests
    └── test_ui.py       # UI component tests
```

## Installation

### Prerequisites

- Python 3.8 or higher
- PyQt6
- PyMuPDF (fitz)

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd PDF_Reader
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```
   
   Or using the package:
   ```bash
   python -m src.pdf_reader
   ```

### Installation as Package

For development or system-wide installation:

```bash
# Development installation (editable)
pip install -e .

# Regular installation
pip install .

# With development dependencies
pip install -e .[dev]
```

After installation, you can run:
```bash
pdf-reader
```

## Usage

### Basic Operations

1. **Open a PDF**: File → Open or use Ctrl+O
2. **Navigate Pages**: Use toolbar buttons or keyboard shortcuts
3. **Change View Mode**: View Modes menu or toolbar buttons
4. **Zoom**: Use zoom buttons or mouse wheel
5. **Table of Contents**: Panels → Toggle Table of Contents

### Keyboard Shortcuts

- `Ctrl+O`: Open file
- `Ctrl+W`: Close current tab
- `Ctrl+Q`: Quit application
- `Page Up/Down`: Navigate pages
- `Ctrl++`: Zoom in
- `Ctrl+-`: Zoom out
- `Ctrl+0`: Reset zoom

### View Modes

- **Single Page**: Display one page at a time
- **Double Page**: Display two pages side by side
- **Fit Page**: Zoom to fit entire page in window
- **Fit Width**: Zoom to fit page width
- **Continuous Scroll**: Scrollable view of all pages

## Development

### Setting up Development Environment

1. **Clone and install in development mode:**
   ```bash
   git clone <repository-url>
   cd PDF_Reader
   pip install -e .[dev]
   ```

2. **Run tests:**
   ```bash
   python -m pytest tests/
   ```

3. **Code formatting:**
   ```bash
   black src/ tests/
   ```

4. **Type checking:**
   ```bash
   mypy src/
   ```

### Architecture

The application follows a modular architecture with clear separation between UI and core logic. See [docs/architecture.md](docs/architecture.md) for detailed information.

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Ensure code quality (black, flake8, mypy)
5. Submit a pull request

## Dependencies

- **PyQt6**: Modern GUI framework
- **PyMuPDF**: PDF processing and rendering
- **Python 3.8+**: Programming language

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built for HCI (Human-Computer Interaction) course
- Uses PyMuPDF for PDF processing
- Uses PyQt6 for the user interface

## Support

For issues, questions, or contributions, please refer to:
- [Documentation](docs/)
- [Architecture Guide](docs/architecture.md)
- [Development Guide](docs/development.md)
