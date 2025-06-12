# Bookmark Functionality

The PDF Reader now includes comprehensive bookmark functionality that allows users to mark important pages for quick navigation.

## Features

### Adding Bookmarks
- **Menu**: Bookmarks → Add Bookmark (Ctrl+B)
- **Toolbar**: Click the bookmark icon in the toolbar
- **Custom Title**: When adding a bookmark, users can specify a custom title or use the default "Page X" format

### Viewing Bookmarks
- **Bookmarks Panel**: Access via Panels → Toggle Bookmarks
- **List View**: All bookmarks are displayed in a list showing the title and page number
- **Sorted by Page**: Bookmarks are automatically sorted by page number

### Navigating with Bookmarks
- **Single Click**: Click any bookmark in the panel to jump to that page
- **Double Click**: Double-click for quick navigation
- **Context Menu**: Right-click on bookmarks for additional options

### Managing Bookmarks
- **Remove Current**: Bookmarks → Remove Bookmark (Ctrl+Shift+B) removes bookmark from current page
- **Context Menu**: Right-click on any bookmark to remove it
- **Automatic Cleanup**: Bookmarks are document-specific and cleared when documents are closed

## Technical Implementation

### Data Model
```python
@dataclass
class Bookmark:
    title: str           # User-defined or auto-generated title
    page_number: int     # 0-based page number
    file_path: str      # Path to the PDF file
    created_at: str     # ISO timestamp of creation
```

### Key Methods
- `add_bookmark(title, page_number)`: Add a new bookmark
- `remove_bookmark(page_number)`: Remove bookmark by page
- `get_bookmarks()`: Get all bookmarks for current document
- `has_bookmark(page_number)`: Check if page is bookmarked
- `jump_to_bookmark(bookmark)`: Navigate to bookmark location

### Signals
- `bookmarks_changed`: Emitted when bookmarks are added or removed
- Connected to UI for automatic updates

## Usage Tips

1. **Quick Bookmarking**: Use Ctrl+B to quickly bookmark the current page
2. **Custom Names**: Give bookmarks meaningful names like "Introduction", "Chapter 3", etc.
3. **Panel Docking**: The bookmarks panel can be docked to any side of the window
4. **Context Actions**: Right-click bookmarks for quick actions like removal
5. **Persistence**: Bookmarks are maintained while the document is open

## Future Enhancements

- [ ] Bookmark persistence across sessions
- [ ] Export/import bookmark collections
- [ ] Bookmark categories or tags
- [ ] Search within bookmarks
- [ ] Bookmark synchronization across devices
