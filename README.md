# PDF Reader

A modern, feature-rich PDF reader application built with PyQt6 and PyMuPDF. This application provides multiple viewing modes, tabbed interface, and efficient memory management for handling large PDF documents.

## Features

- **Multiple View Modes:**
  - Single Page View
  - Double Page View
  - Continuous Scroll View
  - Fit to Page
  - Fit to Width

- **User Interface:**
  - Tabbed interface for multiple documents
  - Table of Contents navigation
  - Bookmarks support (planned)
  - Clean, modern UI with customizable themes

- **Performance:**
  - Virtualized page rendering for memory efficiency
  - Lazy loading of pages in continuous scroll mode
  - Optimized zoom and pan operations

- **Navigation:**
  - Page-by-page navigation
  - Jump to specific page
  - Recent files menu
  - Keyboard shortcuts

## Installation

### Prerequisites

- Python 3.8 or higher
- PyQt6
- PyMuPDF (fitz)

### Using pip

1. Clone the repository:
```bash
git clone <repository-url>
cd PDF_Reader
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

### Using setup.py

1. Install the package:
```bash
pip install -e .
```

2. Run as a module:
```bash
python -m pdf_reader
```

## Project Structure

```
PDF_Reader/
├── app.py                 # Main application entry point
├── setup.py              # Package installation script
├── requirements.txt      # Python dependencies
├── README.md            # This file
│
├── src/pdf_reader/      # Main application package
│   ├── __init__.py      # Package initialization
│   ├── __main__.py      # Module execution entry point
│   │
│   ├── core/            # Core functionality
│   │   ├── __init__.py
│   │   ├── models.py    # Data models and enums
│   │   ├── config.py    # Configuration management
│   │   └── utils.py     # Utility functions
│   │
│   └── ui/              # User interface components
│       ├── __init__.py
│       ├── main_window.py    # Main application window
│       ├── pdf_viewer.py     # PDF viewing widget
│       └── styling.py        # Application styling
│
├── tests/               # Unit and integration tests
│   ├── __init__.py
│   ├── test_core.py     # Core functionality tests
│   └── test_ui.py       # UI component tests
│
├── docs/                # Documentation
│   ├── README.md
│   └── architecture.md  # Architecture documentation
│
└── assets/              # Application assets
    ├── icons/           # Application icons
    └── themes/          # Theme files
```

## Usage

### Basic Operations

1. **Opening PDFs:**
   - File → Open (Ctrl+O)
   - Recent Files menu
   - Drag and drop (planned)

2. **Navigation:**
   - Next/Previous page buttons
   - Page number input
   - Table of Contents panel

3. **View Modes:**
   - View Modes menu
   - Toolbar buttons
   - Keyboard shortcuts

4. **Zooming:**
   - Zoom In/Out buttons
   - Fit to Page/Width modes
   - Mouse wheel (planned)

### Keyboard Shortcuts

- `Ctrl+O`: Open file
- `Ctrl+W`: Close tab
- `Page Up/Down`: Navigate pages
- `Ctrl++/-`: Zoom in/out
- `F11`: Toggle fullscreen (planned)

## Configuration

The application uses a configuration system located in `src/pdf_reader/core/config.py`. You can customize:

- Default view mode
- Window geometry
- Theme preferences
- Performance settings

## Development

### Setting up Development Environment

1. Clone the repository
2. Create a virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install in development mode:
```bash
pip install -e .
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_core.py

# Run with coverage
python -m pytest tests/ --cov=src/pdf_reader
```

### Code Structure

The application follows a modular architecture:

- **Core Module**: Contains business logic, data models, and utilities
- **UI Module**: Contains all user interface components
- **Tests**: Comprehensive test suite for all components

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## Dependencies

- **PyQt6**: Modern GUI framework
- **PyMuPDF**: PDF processing and rendering
- **Python 3.8+**: Core runtime

## Architecture

The application uses a Model-View architecture:

- **Models**: Define data structures and business logic
- **Views**: Handle user interface and user interactions
- **Controllers**: Coordinate between models and views

For detailed architecture information, see [docs/architecture.md](docs/architecture.md).

## Performance Notes

- Large PDFs are handled efficiently through virtualized rendering
- Only visible pages are kept in memory during continuous scroll
- Zoom operations are optimized for smooth user experience
- Background processing for non-critical operations

## Known Issues

- High DPI display scaling (in progress)
- Some complex PDF annotations may not render perfectly
- Memory usage with very large documents (>1000 pages)

## Roadmap

- [ ] Search functionality
- [ ] Annotation support
- [ ] Print support
- [ ] Export to other formats
- [ ] Plugin system
- [ ] Dark mode theme
- [ ] Full keyboard navigation
- [ ] Accessibility improvements

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Changelog

### Version 1.0.0
- Initial release
- Basic PDF viewing functionality
- Multiple view modes
- Tabbed interface
- Table of contents navigation

## Support

For bug reports and feature requests, please use the GitHub issue tracker.

For development questions, see the [docs/](docs/) directory for detailed documentation.