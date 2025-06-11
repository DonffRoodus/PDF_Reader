# PDF Reader

A feature-rich PDF viewer application built with PyQt6 and PyMuPDF, designed for Human-Computer Interaction (HCI) coursework.

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

## Requirements

- Python 3.8+
- PyQt6
- PyMuPDF (fitz)

## Project Structure

```
PDF_Reader/
├── main.py          # Main application file
├── README.md        # This file
├── requirements.txt # Python dependencies
└── .gitignore      # Git ignore file
```

## Development

This project was developed as part of an HCI (Human-Computer Interaction) course, focusing on creating an intuitive and efficient PDF viewing experience.

## License

This project is for educational purposes.
