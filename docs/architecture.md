# Architecture Overview

## High-Level Architecture

The PDF Reader application follows a modular architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────────┐
│                        Application Layer                        │
│                         (app.py)                                │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                         UI Layer                                │
│                   (src/pdf_reader/ui/)                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   MainWindow    │  │   PDFViewer     │  │    Styling      │  │
│  │                 │  │                 │  │                 │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                       Core Layer                                │
│                  (src/pdf_reader/core/)                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │     Models      │  │     Config      │  │     Utils       │  │
│  │                 │  │                 │  │                 │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────┬───────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                    External Libraries                           │
│                  PyQt6 | PyMuPDF                               │
└─────────────────────────────────────────────────────────────────┘
```

## Module Responsibilities

### UI Layer (`src/pdf_reader/ui/`)

#### MainWindow
- Application main window and menu management
- Tab management for multiple PDF documents
- Toolbar and status bar
- Event handling and coordination between components

#### PDFViewer
- PDF rendering and display
- View mode management (single page, double page, continuous scroll)
- Zoom controls and page navigation
- Virtualization for performance optimization

#### Styling
- Application themes and stylesheets
- UI appearance customization

### Core Layer (`src/pdf_reader/core/`)

#### Models
- Data structures and enums (ViewMode)
- Domain model definitions

#### Config
- Configuration management
- Settings persistence
- Default values and constants

#### Utils
- Utility functions
- File validation
- Logging setup
- Icon management

## Design Patterns Used

### 1. Model-View-Controller (MVC)
- **Model**: Core layer with business logic and data
- **View**: UI components for presentation
- **Controller**: Event handlers and application flow

### 2. Observer Pattern
- PyQt6 signals and slots for component communication
- Event-driven architecture

### 3. Strategy Pattern
- Different view modes implemented as strategies
- Pluggable rendering approaches

### 4. Singleton Pattern
- Global configuration instance
- Logging setup

## Data Flow

1. **User Interaction** → MainWindow receives events
2. **Event Processing** → MainWindow delegates to appropriate components
3. **PDF Operations** → PDFViewer handles PDF-specific operations
4. **Rendering** → PyMuPDF processes PDF data
5. **Display** → Qt widgets display the rendered content

## Performance Considerations

### Virtualization
- Only visible pages are rendered in continuous scroll mode
- Memory-efficient for large documents

### Caching
- Rendered pages are cached for quick access
- Intelligent cache management based on usage patterns

### Threading
- PDF operations can be moved to background threads
- UI remains responsive during processing

## Error Handling

### Graceful Degradation
- Application continues to function even with partial failures
- User-friendly error messages

### Logging
- Comprehensive logging for debugging
- Configurable log levels

### Recovery
- Automatic recovery from common errors
- State preservation across sessions
