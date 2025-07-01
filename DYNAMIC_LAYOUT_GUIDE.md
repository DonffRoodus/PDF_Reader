# Dynamic Widget Rearrangement Feature

## Overview

The PDF Reader now includes an intelligent dynamic widget rearrangement system that automatically adapts the user interface based on the window size. This ensures optimal user experience across different screen sizes and window configurations.

## Features

### Automatic Layout Adaptation

The application automatically detects window size changes and rearranges the interface accordingly:

#### Size Categories

1. **Small Windows** (< 800px width OR < 600px height)
   - Hides all dock widgets to maximize content area
   - Uses compact toolbar icons (16px)
   - Compact tab styling with smaller fonts
   - Icon-only toolbar buttons

2. **Medium Windows** (800-1200px width)
   - Shows bookmarks and annotations panels
   - Hides table of contents (space optimization)
   - Moderate toolbar icons (20px)
   - Strategic dock positioning based on height

3. **Large Windows** (> 1200px width)
   - Shows all dock widgets (TOC, bookmarks, annotations)
   - Optimal positioning with tabbed left panels
   - Large toolbar icons (24px) with text labels
   - Full-featured layout

### Layout Positioning Logic

The system intelligently positions dock widgets based on both width and height:

- **Narrow windows**: Annotations dock moves to bottom
- **Wide but short windows**: Annotations dock on right side
- **Large windows**: TOC and bookmarks on left (tabbed), annotations on right
- **Very small windows**: All panels hidden for maximum content space

### Manual Override Controls

Located in `View → Layout` menu:

1. **Adaptive Layout Toggle**: Enable/disable automatic adaptation
2. **Force Compact Mode**: Override window size and force compact layout
3. **Force Full Mode**: Override window size and force full layout with all panels
4. **Show Layout Info**: Display current layout information and thresholds

## Technical Implementation

### Key Methods

- `resizeEvent(event)`: Main handler for window resize events
- `_rearrange_dock_widgets()`: Core logic for dock widget positioning
- `_adjust_toolbar_layout()`: Toolbar styling adaptation
- `_update_tab_styling()`: Tab widget styling changes
- `toggle_adaptive_layout()`: Manual control of adaptive behavior
- `get_layout_info()`: Debugging and information display

### Size Thresholds

```python
SMALL_WIDTH_THRESHOLD = 800px
MEDIUM_WIDTH_THRESHOLD = 1200px
SMALL_HEIGHT_THRESHOLD = 600px
MEDIUM_HEIGHT_THRESHOLD = 800px
```

### State Management

- Saves/restores dock widget states
- Preserves user preferences when adaptive mode is disabled
- Maintains dock widget areas and visibility across sessions

## User Experience Benefits

1. **Responsive Design**: Interface adapts to any window size
2. **Space Optimization**: Maximizes content area on small screens
3. **Accessibility**: Maintains usability across different screen sizes
4. **Customization**: Users can override automatic behavior
5. **Visual Feedback**: Status messages inform users of layout changes

## Testing

### Automated Tests

Run `python test_resize.py` to verify:
- Method availability
- Size threshold logic
- Layout mode controls
- State management functions

### Visual Demo

Run `python visual_demo.py` to see:
- Automatic resizing demonstration
- Live layout adaptation
- Interactive testing capabilities

### Manual Testing

1. Resize the window manually while observing:
   - Dock widget visibility changes
   - Toolbar style adaptations
   - Tab styling modifications
   - Status bar feedback

2. Test override controls:
   - Use View → Layout menu options
   - Verify force compact/full modes
   - Check layout information display

## Integration

The feature integrates seamlessly with existing functionality:

- Preserves document viewing capabilities
- Maintains annotation and bookmark functionality
- Respects user's manual dock arrangements when adaptive mode is off
- Works with all view modes and zoom levels

## Future Enhancements

Potential improvements:
- Touch-friendly mode detection
- Custom threshold configuration
- Per-document layout preferences
- Animation transitions between layouts
- Adaptive font sizing
