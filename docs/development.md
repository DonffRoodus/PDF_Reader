# Development Guide

This guide provides detailed information for developers working on the PDF Reader project.

## Project Overview

The PDF Reader is a modern, modular application built with PyQt6 and PyMuPDF. The project follows best practices for Python development with a clear separation of concerns.

## Architecture

### Core Principles

1. **Separation of Concerns**: UI logic is separated from business logic
2. **Modularity**: Each component has a specific responsibility
3. **Testability**: Code is designed to be easily testable
4. **Extensibility**: New features can be added without major refactoring

### Package Structure

```
src/pdf_reader/
├── core/           # Business logic and data models
│   ├── models.py   # Data structures (ViewMode enum, etc.)
│   ├── config.py   # Configuration management
│   └── utils.py    # Utility functions
│
└── ui/             # User interface components
    ├── main_window.py  # Main application window
    ├── pdf_viewer.py   # PDF viewing widget
    └── styling.py      # UI styling and themes
```

## Development Workflow

### 1. Setting Up Development Environment

```bash
# Clone the repository
git clone <repository-url>
cd PDF_Reader

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install in development mode
pip install -e .
```

### 2. Running the Application

```bash
# Method 1: Direct execution
python app.py

# Method 2: Module execution
python -m src.pdf_reader

# Method 3: After installation
python -m pdf_reader
```

### 3. Testing

```bash
# Run all tests
python run_tests.py

# Run with pytest (if installed)
pytest tests/

# Run with coverage
pytest tests/ --cov=src/pdf_reader --cov-report=html
```

### 4. Code Quality

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

## Component Details

### Core Components

#### ViewMode Enum (`core/models.py`)
Defines the available viewing modes for PDFs:
- `SINGLE_PAGE`: Show one page at a time
- `FIT_PAGE`: Fit entire page in viewport
- `FIT_WIDTH`: Fit page width to viewport
- `DOUBLE_PAGE`: Show two pages side by side
- `CONTINUOUS_SCROLL`: Show all pages in scrollable view

#### Configuration (`core/config.py`)
Manages application settings and user preferences:
- Default view mode
- Window geometry
- Recent files
- Performance settings

#### Utilities (`core/utils.py`)
Common utility functions used across the application.

### UI Components

#### PDFViewer (`ui/pdf_viewer.py`)
The main PDF viewing widget that handles:
- PDF document loading and rendering
- View mode switching
- Page navigation
- Zoom operations
- Virtualized rendering for performance

Key features:
- Memory-efficient page rendering
- Lazy loading for continuous scroll
- Signal-based communication with parent window

#### MainWindow (`ui/main_window.py`)
The main application window that provides:
- Menu bar and toolbar
- Tab management for multiple documents
- Dock widgets (TOC, bookmarks)
- Recent files management
- Status bar and page information

#### Styling (`ui/styling.py`)
Centralized styling and theme management for consistent UI appearance.

## Adding New Features

### 1. Adding a New View Mode

1. Add the new mode to `ViewMode` enum in `core/models.py`
2. Update `PDFViewer.set_view_mode()` to handle the new mode
3. Add UI controls in `MainWindow.create_menus_and_toolbar()`
4. Add tests for the new functionality

### 2. Adding a New UI Component

1. Create the component in the `ui/` package
2. Import and integrate it in `MainWindow`
3. Add styling rules in `styling.py`
4. Create tests in `tests/test_ui.py`

### 3. Adding Configuration Options

1. Define new settings in `core/config.py`
2. Add UI controls for the settings (preferences dialog)
3. Update save/load methods
4. Add tests for configuration persistence

## Performance Considerations

### Memory Management
- Use virtualized rendering for large documents
- Implement page caching with size limits
- Clean up resources when tabs are closed

### Rendering Optimization
- Render only visible pages in continuous mode
- Use appropriate zoom levels for performance
- Implement progressive loading for large pages

### UI Responsiveness
- Use background threads for heavy operations
- Implement progress indicators for long operations
- Cache rendered pages when appropriate

## Testing Strategy

### Unit Tests
- Test individual components in isolation
- Mock external dependencies (file system, PyMuPDF)
- Focus on business logic and data transformations

### Integration Tests
- Test component interactions
- Test UI workflows
- Use PyQt test utilities for UI testing

### Performance Tests
- Memory usage with large documents
- Rendering performance benchmarks
- UI responsiveness under load

## Contributing Guidelines

### Code Style
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write clear, descriptive docstrings
- Keep functions focused and small

### Commit Messages
- Use conventional commit format
- Include clear descriptions of changes
- Reference issue numbers when applicable

### Pull Request Process
1. Create feature branch from main
2. Implement changes with tests
3. Ensure all tests pass
4. Update documentation if needed
5. Submit pull request with clear description

## Debugging

### Common Issues

1. **Import Errors**: Check PYTHONPATH and package structure
2. **PyQt6 Issues**: Ensure QApplication is created before widgets
3. **PDF Rendering**: Check PyMuPDF version compatibility
4. **Memory Issues**: Monitor page cache size and cleanup

### Debug Tools
- Use PyQt6 debug tools for UI issues
- Python debugger (pdb) for logic issues
- Memory profilers for performance issues
- Logging for runtime diagnostics

## Deployment

### Building Distribution
```bash
# Build source distribution
python -m build --sdist

# Build wheel
python -m build --wheel

# Upload to PyPI (test)
twine upload --repository testpypi dist/*
```

### Creating Executables
For standalone executables, consider using:
- PyInstaller
- cx_Freeze
- Nuitka

## Future Enhancements

### Planned Features
- Search functionality within PDFs
- Annotation support
- Print functionality
- Export to other formats
- Plugin system
- Dark mode theme

### Architecture Improvements
- Plugin architecture for extensibility
- Better configuration management
- Improved error handling
- Accessibility features

## Resources

- [PyQt6 Documentation](https://doc.qt.io/qtforpython/)
- [PyMuPDF Documentation](https://pymupdf.readthedocs.io/)
- [Python Packaging Guide](https://packaging.python.org/)
- [Testing with PyQt](https://pytest-qt.readthedocs.io/)
