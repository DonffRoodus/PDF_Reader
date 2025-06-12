# PDF Reader

A feature-rich PDF viewer application built with PyQt6 and PyMuPDF, designed for Human-Computer Interaction (HCI) coursework.

## Project Structure

```
PDF_Reader/
├── app.py                    # Main application entry point
├── main.py                   # Legacy single-file version (deprecated)
├── requirements.txt          # Python dependencies
├── README.md                # Project documentation
└── src/
    └── pdf_reader/          # Main application package
        ├── __init__.py      # Package initialization
        ├── core/            # Core models and data structures
        │   ├── __init__.py
        │   └── models.py    # ViewMode enum and data models
        └── ui/              # User interface components
            ├── __init__.py
            ├── main_window.py    # Main application window
            ├── pdf_viewer.py     # PDF viewing widget
            └── styling.py        # Application styles and themes
```

## Features

- **Multiple View Modes**:
  - Single Page View
  - Double Page View
  - Fit to Page
  - Fit to Width
  - Continuous Scroll with virtualization for performance

- **Navigation**:
  - Page-by-page navigation
  - Jump to specific page
  - Table of Contents (TOC) navigation

- **Zoom Controls**:
  - Zoom in/out functionality
  - Automatic zoom fitting modes

- **User Interface**:
  - Tabbed interface for multiple PDFs
  - Dockable panels (TOC, Bookmarks)
  - Recent files menu
  - Modern, clean UI with custom styling

- **Performance Optimizations**:
  - Virtualized rendering for continuous scroll mode
  - Lazy loading of pages to reduce memory usage

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd PDF_Reader
```

2. Create a virtual environment (recommended):
```bash
python -m venv .venv
.venv\Scripts\activate  # On Windows
# source .venv/bin/activate  # On Linux/macOS
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python main.py
```

## Installation and Usage

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Clone or download the project
2. Navigate to the project directory:
   ```bash
   cd PDF_Reader
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

#### Using the new modular structure (recommended):
```bash
python app.py
```

#### Using the legacy single file (deprecated):
```bash
python main.py
```

### Basic Operations

- **Open PDF**: File → Open or use the toolbar button
- **Navigate**: Use Previous/Next buttons or arrow keys
- **Zoom**: Use zoom in/out buttons or scroll wheel
- **View Modes**: Access through View Modes menu
- **Go to Page**: Enter page number in the toolbar input field

### View Modes

- **Single Page**: Default view showing one page at a time
- **Double Page**: Shows two pages side-by-side
- **Fit Page**: Automatically fits the entire page in the viewport
- **Fit Width**: Automatically fits page width to the viewport
- **Continuous Scroll**: Shows all pages in a scrollable view with virtualization

## Architecture

### Module Organization

- **core/models.py**: Contains the `ViewMode` enum and core data structures
- **ui/pdf_viewer.py**: Main PDF viewing widget with rendering and navigation logic
- **ui/main_window.py**: Application main window with menus, toolbars, and tabs
- **ui/styling.py**: Application-wide styling and themes

### Key Design Principles

- **Separation of Concerns**: UI components are separated from core logic
- **Modularity**: Each component has a specific responsibility
- **Maintainability**: Clear structure makes the code easy to understand and modify
- **Performance**: Virtualized rendering in continuous scroll mode for large PDFs

## Dependencies

- Python 3.8+
- PyQt6
- PyMuPDF (fitz)

## Development Notes

This project was refactored from a single-file application (`main.py`) into a modular structure to improve:
- Code organization and readability
- Maintainability and extensibility
- Testing capabilities
- Collaboration workflow

## Development

This project was developed as part of an HCI (Human-Computer Interaction) course, focusing on creating an intuitive and efficient PDF viewing experience.

## License

This project is for educational purposes.
