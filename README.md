# PDF Reader

A modern, feature-rich PDF reader application built with PyQt6 and PyMuPDF. This application provides multiple viewing modes, tabbed interface, annotation support, and efficient memory management for handling large PDF documents.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.4+-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Features

### 🖥️ **Multiple View Modes**
- **Single Page View**: Focus on one page at a time
- **Double Page View**: Side-by-side page display
- **Continuous Scroll View**: Seamless scrolling through the document
- **Fit to Page**: Automatically fit entire page to window
- **Fit to Width**: Optimize page width for reading

### 🎨 **User Interface**
- **Tabbed Interface**: Open multiple documents simultaneously
- **Table of Contents**: Quick navigation through document structure
- **Bookmarks**: Full bookmark functionality with custom titles and management
- **Eye-Friendly Design**: Warm, cream-colored theme optimized for extended reading sessions
- **Reduced Eye Strain**: Soft color palette that minimizes blue light exposure
- **Modern UI**: Clean, intuitive interface with customizable themes
- **Responsive Design**: Adaptive layout for different screen sizes

### ✏️ **Annotation Support**
- **Highlighting**: Mark important text passages
- **Underlining**: Emphasize key information
- **Text Notes**: Add custom annotations and comments
- **Annotation Management**: Edit, delete, and organize annotations

### ⚡ **Performance**
- **Virtualized Rendering**: Memory-efficient page rendering for large documents
- **Lazy Loading**: Smart loading of pages in continuous scroll mode
- **Optimized Operations**: Smooth zoom and pan operations
- **Background Processing**: Non-blocking operations for better user experience

### 🧭 **Navigation**
- **Page Navigation**: Next/previous page with keyboard shortcuts
- **Direct Page Access**: Jump to specific page numbers
- **Recent Files**: Quick access to recently opened documents
- **Keyboard Shortcuts**: Comprehensive keyboard navigation support

## 🚀 Quick Start

### Prerequisites

- **Python 3.8 or higher**
- **Windows, macOS, or Linux**
- **Git** (for cloning the repository)

### Installation Options

#### Option 1: Direct Installation (Recommended)

1. **Clone the repository:**
```bash
git clone <repository-url>
cd PDF_Reader
```

2. **Create a virtual environment (recommended):**
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run the application:**
```bash
python app.py
```

#### Option 2: Package Installation

1. **Install the package in development mode:**
```bash
pip install -e .
```

2. **Run as a module:**
```bash
python -m pdf_reader
```

#### Option 3: Quick Test Run

For a quick test without virtual environment:
```bash
pip install PyQt6 PyMuPDF
python app.py
```

## 📁 Project Structure

```
PDF_Reader/
├── 📄 app.py                    # Main application entry point
├── 📄 main.py                   # Alternative entry point (legacy)
├── 📄 setup.py                  # Package installation script
├── 📄 requirements.txt          # Production dependencies
├── 📄 requirements-dev.txt      # Development dependencies
├── 📄 run_tests.py             # Test runner script
├── 📄 verify_structure.py      # Project structure verification
├── 📄 run.bat                  # Windows batch file for easy running
├── 📄 README.md                # Project documentation
├── 📄 CHANGELOG.md             # Version history and changes
│
├── 📁 src/pdf_reader/          # Main application package
│   ├── 📄 __init__.py          # Package initialization
│   ├── 📄 __main__.py          # Module execution entry point
│   │
│   ├── 📁 core/                # Core functionality
│   │   ├── 📄 __init__.py      # Core package initialization
│   │   ├── 📄 models.py        # Data models and enums
│   │   ├── 📄 config.py        # Configuration management
│   │   └── 📄 utils.py         # Utility functions
│   │
│   └── 📁 ui/                  # User interface components
│       ├── 📄 __init__.py      # UI package initialization
│       ├── 📄 main_window.py   # Main application window
│       ├── 📄 pdf_viewer.py    # PDF viewing widget
│       └── 📄 styling.py       # Application styling and themes
│
├── 📁 tests/                   # Test suite
│   ├── 📄 __init__.py          # Test package initialization
│   ├── 📄 test_core.py         # Core functionality tests
│   └── 📄 test_ui.py           # UI component tests
│
├── 📁 docs/                    # Documentation
│   ├── 📄 README.md            # Documentation overview
│   ├── 📄 architecture.md      # Architecture documentation
│   ├── 📄 bookmarks.md         # Bookmark feature documentation
│   └── 📄 development.md       # Development guide
│
└── 📁 assets/                  # Application assets
    ├── 📄 README.md            # Assets documentation
    ├── 📁 icons/               # Application icons
    └── 📁 themes/              # Theme configuration files
```
│   ├── README.md
│   └── architecture.md  # Architecture documentation
│
└── assets/              # Application assets
    ├── icons/           # Application icons
    └── themes/          # Theme files
```

## 🎯 Usage

### Opening and Viewing PDFs

1. **Opening Documents:**
   - **File Menu**: `File → Open` or `Ctrl+O`
   - **Recent Files**: Access recently opened documents from the File menu
   - **Drag & Drop**: (Planned feature) Drop PDF files directly into the application

2. **Navigation:**
   - **Page Controls**: Use Next/Previous buttons or arrow keys
   - **Direct Navigation**: Enter page number in the page input field
   - **Table of Contents**: Use the TOC panel for quick section navigation
   - **Bookmarks**: Navigate using your custom bookmarks

### Bookmark Management

3. **Creating Bookmarks:**
   - **Add Bookmark**: `Ctrl+B` or click the bookmark button in toolbar
   - **Custom Titles**: Enter meaningful titles for your bookmarks
   - **Quick Access**: Use the bookmarks panel for one-click navigation

4. **Managing Bookmarks:**
   - **Edit Titles**: Right-click on bookmarks to modify titles
   - **Remove Bookmarks**: `Ctrl+Shift+B` to remove from current page
   - **Organize**: Use the bookmarks panel to manage your bookmark collection

### Annotation Features

5. **Creating Annotations:**
   - **Highlighting**: Select text and choose highlight option
   - **Underlining**: Select text and apply underline annotation
   - **Text Notes**: Add custom comments and notes to specific locations
   - **Annotation Tools**: Use the annotation toolbar for quick access

6. **Managing Annotations:**
   - **Edit**: Modify existing annotations by selecting them
   - **Delete**: Remove unwanted annotations
   - **Navigate**: Jump between annotations using the annotations panel

### View Modes and Display

7. **View Options:**
   - **Single Page**: Focus on one page at a time
   - **Double Page**: Side-by-side viewing for books and magazines
   - **Continuous**: Seamless scrolling through the entire document
   - **Fit Modes**: Automatically adjust to page size or width

8. **Zoom and Pan:**
   - **Zoom Controls**: Use `Ctrl++/-` or toolbar buttons
   - **Fit Options**: Choose from Fit to Page or Fit to Width
   - **Mouse Navigation**: Pan by clicking and dragging (when zoomed)

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Open file |
| `Ctrl+W` | Close current tab |
| `Ctrl+B` | Add bookmark |
| `Ctrl+Shift+B` | Remove bookmark from current page |
| `Page Up/Down` | Navigate pages |
| `Ctrl++/-` | Zoom in/out |
| `Ctrl+0` | Reset zoom to fit |
| `Arrow Keys` | Navigate pages |
| `Home/End` | Go to first/last page |
| `F11` | Toggle fullscreen (planned) |

## 👁️ Eye-Friendly Design

This PDF Reader features a specially designed **warm color scheme** optimized for comfortable long-term reading:

### Design Benefits:
- **🌅 Warm Color Palette**: Cream and beige backgrounds instead of harsh white
- **🔆 Reduced Blue Light**: Minimizes eye strain from prolonged screen exposure
- **🎨 Soft Contrasts**: Gentle color transitions that are easier on the eyes
- **☕ Earth Tones**: Brown and tan accent colors for a natural, calming feel
- **📖 Reading Optimized**: Perfect for extended document reading sessions

### Color Scheme Features:
- **Background**: Warm cream tones (`#faf8f3`, `#fefcf9`)
- **Text**: Soft dark brown (`#3d3833`, `#5d564d`) for comfortable readability
- **Accents**: Warm brown highlights (`#8b7355`) instead of bright blues
- **Borders**: Subtle earth-tone borders for gentle visual separation

This thoughtful design approach makes the application ideal for students, researchers, and professionals who spend hours reading documents.

## ⚙️ Configuration

The application uses a robust configuration system located in `src/pdf_reader/core/config.py`. 

### Customizable Settings

- **Default View Mode**: Set your preferred viewing mode (single, double, continuous)
- **Window Geometry**: Remember window size and position
- **Eye-Friendly Theme**: Warm color scheme designed for comfortable reading
- **Theme Preferences**: Choose from available themes and styling options
- **Performance Settings**: Adjust memory usage and rendering optimization
- **Bookmark Behavior**: Configure bookmark creation and management
- **Annotation Settings**: Customize annotation appearance and behavior

### Configuration Files

Configuration is automatically saved and restored between sessions. Advanced users can modify settings programmatically through the configuration API.

## 🛠️ Development

### Development Environment Setup

1. **Clone and Setup:**
```bash
git clone <repository-url>
cd PDF_Reader
```

2. **Create Virtual Environment:**
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows PowerShell
.venv\Scripts\Activate.ps1

# Windows Command Prompt
.venv\Scripts\activate.bat

# macOS/Linux
source .venv/bin/activate
```

3. **Install Dependencies:**
```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Install in development mode
pip install -e .
```

### Running Tests

```bash
# Run all tests
python run_tests.py

# Alternative: Use pytest directly
python -m pytest tests/

# Run specific test files
python -m pytest tests/test_core.py
python -m pytest tests/test_ui.py

# Run with coverage report
python -m pytest tests/ --cov=src/pdf_reader --cov-report=html

# Run tests in verbose mode
python -m pytest tests/ -v
```

### Development Tools

The project includes several development tools:

```bash
# Verify project structure
python verify_structure.py

# Run application in development mode
python app.py

# Run as module
python -m pdf_reader
```

### Code Quality

Development dependencies include:
- **pytest**: Testing framework
- **pytest-cov**: Coverage reporting
- **pytest-qt**: GUI testing for PyQt applications
- **black**: Code formatting (optional)
- **flake8**: Linting (optional)
- **mypy**: Type checking (optional)

### Architecture Overview

The application follows a clean, modular architecture with clear separation of concerns:

#### **Model-View Architecture**
- **Models** (`core/models.py`): Define data structures, enums, and business logic
- **Views** (`ui/`): Handle user interface components and user interactions
- **Configuration** (`core/config.py`): Centralized configuration management
- **Utilities** (`core/utils.py`): Shared utility functions and helpers

#### **Key Design Principles**
- **Modularity**: Clear separation between core logic and UI
- **Testability**: Comprehensive test coverage with isolated components
- **Extensibility**: Plugin-ready architecture for future enhancements
- **Performance**: Optimized for handling large PDF documents efficiently

#### **Package Organization**
- **`src/pdf_reader/core/`**: Business logic, data models, configuration
- **`src/pdf_reader/ui/`**: User interface components and styling
  - **`styling.py`**: Eye-friendly color scheme and theme definitions
- **`tests/`**: Comprehensive test suite for all components
- **`docs/`**: Detailed documentation and guides

For detailed architecture information, see [`docs/architecture.md`](docs/architecture.md).

### Contributing

We welcome contributions! Please follow these steps:

1. **Fork the Repository**
2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make Your Changes**
   - Follow the existing code style
   - Add tests for new functionality
   - Update documentation as needed
4. **Test Your Changes**
   ```bash
   python run_tests.py
   ```
5. **Commit Your Changes**
   ```bash
   git commit -m "Add feature: your feature description"
   ```
6. **Submit a Pull Request**

#### **Contribution Guidelines**
- Ensure all tests pass before submitting
- Follow Python PEP 8 style guidelines
- Add docstrings for new functions and classes
- Update README.md if adding new features
- Include tests for bug fixes and new features

## 📦 Dependencies

### Core Dependencies
- **[PyQt6](https://www.riverbankcomputing.com/software/pyqt/) (≥6.4.0)**: Modern GUI framework
- **[PyMuPDF](https://pymupdf.readthedocs.io/) (≥1.23.0)**: PDF processing and rendering library

### Development Dependencies
- **[pytest](https://pytest.org/) (≥6.0.0)**: Testing framework
- **[pytest-cov](https://pytest-cov.readthedocs.io/) (≥2.0.0)**: Coverage reporting
- **[pytest-qt](https://pytest-qt.readthedocs.io/) (≥4.0.0)**: PyQt testing support

### System Requirements
- **Python 3.8+**: Core runtime environment
- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Memory**: 4GB RAM minimum, 8GB recommended for large PDFs
- **Storage**: 100MB for application, additional space for PDF files

## 📈 Performance & Optimization

### Performance Features

- **🔄 Virtualized Rendering**: Only renders visible pages to minimize memory usage
- **⚡ Lazy Loading**: Pages are loaded on-demand in continuous scroll mode
- **🎯 Optimized Zoom**: Smooth zoom operations with intelligent caching
- **🏃 Background Processing**: Non-critical operations run in background threads
- **💾 Smart Memory Management**: Automatic cleanup of unused page resources

### Large Document Handling

The application is optimized for large PDF documents:
- Documents with 1000+ pages are handled efficiently
- Memory usage remains stable regardless of document size
- Fast page navigation even in very large files
- Responsive UI during intensive operations

## ⚠️ Known Issues & Limitations

### Current Limitations
- **High DPI Scaling**: Some UI elements may not scale perfectly on high-DPI displays
- **Complex Annotations**: Some advanced PDF annotations may not render with full fidelity
- **Very Large Documents**: Memory usage may increase with documents over 1000 pages
- **File Format Support**: Currently supports PDF files only

### Planned Improvements
- Enhanced high-DPI display support
- Improved annotation rendering compatibility
- Additional file format support (EPUB, XPS)
- Performance optimizations for extremely large documents

## 🗺️ Roadmap

### ✅ **Completed Features**
- [x] Multiple view modes (single, double, continuous)
- [x] Tabbed interface for multiple documents
- [x] Table of contents navigation
- [x] Bookmark functionality with custom titles
- [x] Basic annotation support (highlight, underline, text notes)
- [x] Modern, responsive UI
- [x] Comprehensive test suite
- [x] Modular architecture

### 🚧 **In Progress**
- [ ] Annotation persistence across sessions
- [ ] Enhanced search functionality
- [ ] Print support with page options
- [ ] Dark mode theme

### 📋 **Planned Features**

#### **Core Features**
- [ ] Global search with result highlighting
- [ ] Advanced annotation tools (shapes, arrows, stamps)
- [ ] Form filling support
- [ ] Digital signature viewing
- [ ] Document comparison tools

#### **User Interface**
- [ ] Customizable toolbar
- [ ] Multiple theme options
- [ ] Full keyboard navigation
- [ ] Accessibility improvements (screen reader support)
- [ ] Touch/gesture support for tablets

#### **Export & Integration**
- [ ] Export to various formats (images, text, HTML)
- [ ] Cloud storage integration
- [ ] Plugin system for extensibility
- [ ] Command-line interface
- [ ] Batch processing tools

#### **Advanced Features**
- [ ] OCR text recognition for scanned PDFs
- [ ] Document encryption/decryption
- [ ] Collaborative annotation sharing
- [ ] Version control for annotated documents
- [ ] AI-powered document analysis

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### Third-Party Licenses
- **PyQt6**: Available under GPL v3 and commercial licenses
- **PyMuPDF**: Available under AGPL and commercial licenses

## 📝 Changelog

### Version 2.0.0 (Current)
- **🏗️ Major Architecture Refactoring**: Complete rewrite with modular design
- **✨ Enhanced UI**: Improved user interface with better responsiveness
- **🛡️ Eye-Friendly Design**: Warm color scheme optimized for extended reading sessions
- **🌅 Reduced Eye Strain**: Cream backgrounds and earth tones minimize blue light exposure
- **📝 Annotation System**: Full annotation support with highlighting and notes
- **🔖 Advanced Bookmarks**: Custom bookmark titles and management
- **🧪 Comprehensive Testing**: Full test suite with 90%+ coverage
- **📚 Documentation**: Complete documentation and development guides

### Version 1.0.0 (Legacy)
- Initial release with basic PDF viewing
- Single page and continuous view modes
- Basic navigation and zoom functionality
- Simple file opening and recent files

For detailed version history, see [CHANGELOG.md](CHANGELOG.md).

## 🆘 Support & Help

### Getting Help

- **📖 Documentation**: Check the [`docs/`](docs/) directory for detailed guides
- **🐛 Bug Reports**: Use the GitHub issue tracker for bug reports
- **💡 Feature Requests**: Submit enhancement ideas through GitHub issues
- **❓ Questions**: For development questions, see the development documentation

### Reporting Issues

When reporting bugs, please include:
1. **Operating System** and version
2. **Python version** (`python --version`)
3. **PDF Reader version**
4. **Steps to reproduce** the issue
5. **Expected vs actual behavior**
6. **Error messages** or logs (if any)

### Community

- **GitHub Discussions**: For general questions and discussions
- **Issue Tracker**: For bug reports and feature requests
- **Development Guide**: See [`docs/development.md`](docs/development.md)

---

**Made with ❤️ using Python and PyQt6**

*For more information about the architecture and design decisions, please refer to the documentation in the [`docs/`](docs/) directory.*