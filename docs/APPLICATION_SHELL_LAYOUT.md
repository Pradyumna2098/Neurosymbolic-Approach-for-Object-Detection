# Application Shell and Layout - Visual Documentation

This document provides a visual representation of the implemented application shell and layout for Issue #15.

## Layout Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  Menu Bar: File | Edit | View | Tools | Help                    [☀️/🌙 Theme]  │
├──────────────────────┬──────────────────────────────────────────────────────────┤
│                      │                                                          │
│   📁 Upload Panel    │         🖼️  Results Viewer                              │
│                      │                                                          │
│  ┌────────────────┐  │   ┌──────────────────────────────────────────────┐     │
│  │                │  │   │  [Input] [Labels] [Output] [Compare]         │     │
│  │  Drag & Drop   │  │   └──────────────────────────────────────────────┘     │
│  │  or Browse     │  │                                                          │
│  │                │  │   ┌──────────────────────────────────────────────┐     │
│  └────────────────┘  │   │                                              │     │
│                      │   │                                              │     │
├══════════════════════┤   │         Image Canvas Area                    │     │
│  (resize handle)     │   │                                              │     │
├──────────────────────┤   │                                              │     │
│                      │   │                                              │     │
│   ⚙️  Config Panel   │   └──────────────────────────────────────────────┘     │
│                      │                                                          │
│  ┌────────────────┐  │                                                          │
│  │ Confidence     │  │                                                          │
│  │ IoU Threshold  │  │                                                          │
│  │ Slice Size     │  │                                                          │
│  │ Overlap Ratio  │  │                                                          │
│  └────────────────┘  │                                                          │
│                      │                                                          │
├══════════════════════┴══════════════════════════════════════════════════════════┤
│  (horizontal resize handle)                                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│  👁️  Monitoring Dashboard                           [▲ Collapse] [▼ Expand]    │
│                                                                                  │
│  📊 Prometheus Metrics | 📝 Logs | 📈 Performance Stats                        │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Window Specifications

- **Minimum Size:** 1400×900 pixels
- **Initial Size:** 1400×900 pixels
- **Resizable:** Yes (user can resize window)

## Panel Specifications

### Upload Panel (Top-Left)
- **Location:** Top-left quadrant
- **Default Width:** 25% of window
- **Min Width:** 15% of window
- **Max Width:** 40% of window
- **Default Height:** 50% of left column
- **Min Height:** 20% of left column
- **Resizable:** Yes (both horizontally and vertically)
- **Content:** Placeholder for file upload functionality

### Configuration Panel (Bottom-Left)
- **Location:** Bottom-left quadrant
- **Default Width:** 25% of window (same as Upload Panel)
- **Min Width:** 15% of window
- **Max Width:** 40% of window
- **Default Height:** 50% of left column
- **Min Height:** 20% of left column
- **Resizable:** Yes (both horizontally and vertically)
- **Content:** Placeholder for YOLO/SAHI parameter controls

### Results Panel (Main Content)
- **Location:** Right side of window
- **Default Width:** 75% of window
- **Min Width:** 40% of window
- **Resizable:** Yes (horizontally)
- **Content:** Tabbed interface with Input/Labels/Output/Compare views
- **Features:** Image canvas area for visualization

### Monitoring Dashboard (Bottom)
- **Location:** Bottom of window
- **Default Height:** 25% of window
- **Min Height:** 10% of window
- **Max Height:** 50% of window
- **Resizable:** Yes (vertically)
- **Collapsible:** Yes (click header to expand/collapse)
- **Content:** Placeholder for Prometheus metrics, logs, and performance stats

## Theme Support

### Dark Theme (Default)
- **Background:** #121212 (primary), #1E1E1E (paper)
- **Text:** #FFFFFF (primary), #B0B0B0 (secondary)
- **Primary Accent:** #2196F3 (blue)
- **Secondary Accent:** #FF9800 (orange)
- **Success:** #4CAF50 (green)
- **Error:** #F44336 (red)
- **Borders/Dividers:** #3F3F3F

### Light Theme
- **Background:** #FFFFFF (primary), #F5F5F5 (paper)
- **Text:** #212121 (primary), #666666 (secondary)
- **Primary Accent:** #1976D2 (blue)
- **Secondary Accent:** #F57C00 (orange)
- **Success:** #388E3C (green)
- **Error:** #D32F2F (red)
- **Borders/Dividers:** #E0E0E0

### Theme Toggle
- Located in the top-right corner of the menu bar
- Icon: ☀️ (Sun) for light mode, 🌙 (Moon) for dark mode
- Smooth transition between themes
- Persists across application restart (future feature)

## Menu Bar

### File Menu
- Open
- Save
- Exit

### Edit Menu
- Cut
- Copy
- Paste

### View Menu
- Zoom In
- Zoom Out
- Reset Zoom

### Tools Menu
- Options
- Settings

### Help Menu
- Documentation
- About

## Resize Handles

All resize handles are styled with:
- **Visual Indicator:** 4px divider line
- **Color:** Matches theme divider color
- **Cursor:** Changes to resize cursor on hover
  - `row-resize` for horizontal dividers
  - `col-resize` for vertical dividers
- **Functionality:** Drag to resize adjacent panels

## Technical Implementation

### Technologies Used
- **UI Framework:** Material-UI (MUI) v6
- **Layout System:** react-resizable-panels v2
- **Styling:** Emotion (CSS-in-JS)
- **Icons:** Material Design Icons
- **Theme Management:** MUI ThemeProvider

### Component Structure
```
App.tsx
└── AppShell.tsx
    ├── ThemeProvider (dark/light theme)
    ├── CssBaseline (CSS reset)
    ├── AppBar (menu bar)
    │   ├── File Menu
    │   ├── Edit Menu
    │   ├── View Menu
    │   ├── Tools Menu
    │   ├── Help Menu
    │   └── Theme Toggle Button
    └── Resizable Panel Layout
        ├── Group (vertical)
        │   ├── Panel (top section - 75%)
        │   │   └── Group (horizontal)
        │   │       ├── Panel (left - 25%)
        │   │       │   └── Group (vertical)
        │   │       │       ├── Panel (upload - 50%)
        │   │       │       │   └── UploadPanel.tsx
        │   │       │       ├── Separator (resize handle)
        │   │       │       └── Panel (config - 50%)
        │   │       │           └── ConfigPanel.tsx
        │   │       ├── Separator (resize handle)
        │   │       └── Panel (results - 75%)
        │   │           └── ResultsPanel.tsx
        │   ├── Separator (resize handle)
        │   └── Panel (monitoring - 25%)
        │       └── MonitoringPanel.tsx
```

## Acceptance Criteria Status

✅ **Window launches at 1400×900 minimum**
- Implemented in `frontend/src/main/main.ts`
- Window size set to 1400×900
- Minimum size also set to 1400×900

✅ **Four-panel layout implemented**
- Upload Panel (top-left)
- Configuration Panel (bottom-left)
- Results Panel (main content)
- Monitoring Dashboard (bottom)

✅ **Panels resizable**
- All panels have resize handles
- Appropriate constraints (min/max sizes)
- Smooth drag-and-drop resizing
- Visual feedback with cursors

✅ **Dark/light theme support**
- Dark theme (default)
- Light theme
- Toggle button in menu bar
- Follows visual design guidelines
- Smooth transitions

## Future Enhancements

The following features are placeholders and will be implemented in subsequent issues:

1. **Upload Panel (#16)**
   - File browser integration
   - Drag-and-drop file upload
   - Image preview thumbnails
   - File information display
   - Batch upload support

2. **Configuration Panel (#17)**
   - YOLO model selection
   - Confidence threshold slider
   - IoU threshold slider
   - SAHI slice size controls
   - Overlap ratio controls
   - Run detection button

3. **Results Panel (#18)**
   - Image visualization with bounding boxes
   - Input/Labels/Output/Compare tabs
   - Zoom and pan controls
   - Detection info overlay
   - Export results

4. **Monitoring Dashboard (#19)**
   - Prometheus metrics integration
   - Real-time performance charts
   - Log viewer
   - Processing status
   - Statistics dashboard

## Screenshots

Note: Screenshots cannot be captured in the headless CI environment. To view the application:

1. Clone the repository
2. Navigate to `frontend/` directory
3. Run `npm install`
4. Run `npm start`
5. The application will launch with the implemented layout

## References

- **Feature Specification:** `docs/feature_implementation/frontend_ui_design.md`
- **Visual Guidelines:** `docs/feature_implementation/visual_design_guidelines.md`
- **Progress Tracking:** `docs/feature_implementation_progress/PROGRESS.md`
- **Issue:** #15 - Implement Application Shell and Layout
