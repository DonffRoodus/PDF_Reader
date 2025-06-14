# Eye-Friendly Color Theme

## Overview
The PDF Reader application now features a warm, eye-friendly color scheme designed for comfortable long-time reading sessions.

## Color Palette

### Background Colors
- **Main Background**: `#faf8f3` (Warm cream)
- **Panel Background**: `#fefcf9` (Off-white cream)
- **Secondary Background**: `#f2ede6` (Light beige)

### Text Colors
- **Primary Text**: `#3d3833` (Soft dark brown)
- **Secondary Text**: `#5d564d` (Medium brown)
- **Disabled Text**: `#c7b8a8` (Light brown)

### Accent Colors
- **Primary Accent**: `#8b7355` (Warm brown)
- **Hover Accent**: `#7a6549` (Darker warm brown)
- **Border Color**: `#e6ddd4` (Light warm gray)

### Selection Colors
- **Selection Background**: `#e8dcc9` (Light beige selection)
- **Focus Border**: `#b8a082` (Warm tan)

## Benefits for Long-Time Reading

1. **Reduced Blue Light**: The warm color palette minimizes harsh blue light that can cause eye strain
2. **Lower Contrast**: Softer contrast reduces the harsh white background glare
3. **Warm Tones**: Cream and beige backgrounds are easier on the eyes than pure white
4. **Consistent Palette**: All UI elements use harmonious warm tones for a cohesive, comfortable experience
5. **Maintained Accessibility**: Colors still provide sufficient contrast for readability while being gentler on the eyes

## Technical Implementation
The color scheme is applied through the `get_application_stylesheet()` function in `src/pdf_reader/ui/styling.py`, ensuring consistent theming across all UI components.
