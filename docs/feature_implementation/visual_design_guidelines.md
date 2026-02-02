# Visual Design Guidelines

**Version:** 1.0  
**Date:** February 2, 2026  
**Related:** [Frontend UI Design](frontend_ui_design.md)

## Table of Contents
1. [Design Principles](#design-principles)
2. [Color Palette](#color-palette)
3. [Typography](#typography)
4. [Icons and Assets](#icons-and-assets)
5. [Spacing and Layout](#spacing-and-layout)
6. [Component Styling](#component-styling)
7. [Animations and Transitions](#animations-and-transitions)
8. [Accessibility](#accessibility)
9. [Responsive Design](#responsive-design)
10. [Asset Requirements](#asset-requirements)

---

## Design Principles

### 1. Clarity
- **Clear Visual Hierarchy**: Important elements stand out
- **Consistent Patterns**: Similar actions look and behave the same way
- **Readable Text**: High contrast, appropriate sizing
- **Uncluttered Layout**: Focus on essential information

### 2. Efficiency
- **Quick Access**: Frequent actions require fewer clicks
- **Smart Defaults**: Reasonable default values for all parameters
- **Keyboard Shortcuts**: Support power users
- **Batch Operations**: Handle multiple items efficiently

### 3. Feedback
- **Immediate Response**: UI reacts instantly to user actions
- **Progress Indicators**: Show status of long-running operations
- **Error Messages**: Clear, actionable error descriptions
- **Success Confirmation**: Positive feedback for completed actions

### 4. Professionalism
- **Modern Aesthetic**: Clean, contemporary design
- **Consistent Branding**: Cohesive visual identity
- **Attention to Detail**: Polished, refined appearance
- **Technical Credibility**: Suitable for ML/AI professional context

---

## Color Palette

### Primary Colors

#### Dark Theme (Default)
```
Background Colors:
- Primary Background:   #121212  (Main app background)
- Secondary Background: #1E1E1E  (Panels, cards)
- Elevated Surface:     #2D2D2D  (Hover states, dialogs)
- Border Color:         #3F3F3F  (Dividers, borders)

Text Colors:
- Primary Text:         #FFFFFF  (Headings, primary content)
- Secondary Text:       #B0B0B0  (Descriptions, labels)
- Disabled Text:        #6B6B6B  (Disabled controls)
- Hint Text:            #808080  (Placeholders, hints)

Accent Colors:
- Primary Accent:       #2196F3  (Buttons, links, focus)
- Primary Accent Hover: #1976D2  (Hover state)
- Secondary Accent:     #FF9800  (Warnings, highlights)
- Success:              #4CAF50  (Success states)
- Error:                #F44336  (Errors, destructive actions)
- Warning:              #FF9800  (Warnings)
- Info:                 #2196F3  (Information)
```

#### Light Theme (Optional)
```
Background Colors:
- Primary Background:   #FFFFFF
- Secondary Background: #F5F5F5
- Elevated Surface:     #FAFAFA
- Border Color:         #E0E0E0

Text Colors:
- Primary Text:         #212121
- Secondary Text:       #666666
- Disabled Text:        #9E9E9E
- Hint Text:            #757575

Accent Colors:
- Primary Accent:       #1976D2
- Primary Accent Hover: #1565C0
- Secondary Accent:     #F57C00
- Success:              #388E3C
- Error:                #D32F2F
- Warning:              #F57C00
- Info:                 #1976D2
```

### Semantic Colors

#### Object Detection Classes
Use distinct, color-blind friendly colors for bounding boxes:

```
Class Colors (HSL for easy adjustment):
- Class 0 (Vehicle):    #E91E63  (Pink)
- Class 1 (Person):     #2196F3  (Blue)
- Class 2 (Animal):     #4CAF50  (Green)
- Class 3 (Building):   #FF9800  (Orange)
- Class 4 (Other):      #9C27B0  (Purple)
- Class 5:              #00BCD4  (Cyan)
- Class 6:              #FFEB3B  (Yellow)
- Class 7:              #795548  (Brown)
- Class 8:              #607D8B  (Blue Grey)
- Class 9+:             Auto-generate from HSL with even distribution
```

**Color-Blind Friendly Palette**:
For accessibility, provide alternative palette using IBM's color-blind safe colors:
```
- Safe Blue:    #648FFF
- Safe Cyan:    #785EF0
- Safe Magenta: #DC267F
- Safe Orange:  #FE6100
- Safe Yellow:  #FFB000
```

### Chart Colors
```
Chart Palette:
- Line 1:   #2196F3  (Primary Blue)
- Line 2:   #4CAF50  (Green)
- Line 3:   #FF9800  (Orange)
- Line 4:   #9C27B0  (Purple)
- Line 5:   #F44336  (Red)
- Line 6:   #00BCD4  (Cyan)
```

---

## Typography

### Font Family

**Primary Font**: Roboto (included with Material-UI)
- Modern, clean, excellent readability
- Multiple weights available
- Good support for UI elements

**Monospace Font**: Roboto Mono
- Code blocks, file paths
- Configuration values
- Log output

### Font Sizes and Weights

```
Typography Scale:
h1:  32px / 500 weight  (Page titles)
h2:  24px / 500 weight  (Section headers)
h3:  20px / 500 weight  (Subsection headers)
h4:  18px / 500 weight  (Component titles)
h5:  16px / 500 weight  (Small headers)
h6:  14px / 500 weight  (Labels, captions)

body1:   16px / 400 weight / 1.5 line-height (Primary text)
body2:   14px / 400 weight / 1.43 line-height (Secondary text)
button:  14px / 500 weight / uppercase (Button text)
caption: 12px / 400 weight / 1.66 line-height (Captions, hints)
overline: 12px / 400 weight / uppercase (Overlines, labels)
```

### Text Styling

```css
/* Primary Heading */
.heading-primary {
  font-family: 'Roboto', sans-serif;
  font-size: 32px;
  font-weight: 500;
  line-height: 1.2;
  letter-spacing: -0.5px;
  color: #FFFFFF;
}

/* Body Text */
.text-body {
  font-family: 'Roboto', sans-serif;
  font-size: 16px;
  font-weight: 400;
  line-height: 1.5;
  color: #FFFFFF;
}

/* Monospace (Code) */
.text-mono {
  font-family: 'Roboto Mono', monospace;
  font-size: 14px;
  font-weight: 400;
  line-height: 1.5;
  color: #B0B0B0;
}
```

---

## Icons and Assets

### Icon Style

**Icon Library**: Material Icons (Material Design Icons)
- Consistent style across application
- Comprehensive icon set
- Well-tested and accessible

### Icon Sizes
```
Sizes:
- Small:    16px (Inline with text)
- Medium:   24px (Default, buttons)
- Large:    32px (Feature icons)
- XLarge:   48px (Empty states)
```

### Key Icons

```
Navigation & Actions:
- Upload:           📁 upload, cloud_upload
- Folder:           📂 folder, folder_open
- Settings:         ⚙️ settings, tune
- Play:             ▶️ play_arrow
- Pause:            ⏸ pause
- Stop:             ⏹ stop
- Close:            ✕ close
- Expand:           ▼ expand_more
- Collapse:         ▲ expand_less

Features:
- Detection:        🎯 my_location, center_focus_strong
- Image:            🖼️ image, photo
- Chart:            📊 bar_chart, show_chart
- Metrics:          📈 trending_up
- Monitoring:       👁️ visibility
- Export:           💾 save, download
- Filter:           🔍 filter_list
- Zoom:             🔍 zoom_in, zoom_out

Status:
- Success:          ✓ check_circle
- Error:            ⚠️ error, warning
- Info:             ℹ️ info
- Loading:          ⏳ hourglass_empty, sync
```

### Application Icon

**Requirements**:
- Sizes: 16x16, 32x32, 48x48, 64x64, 128x128, 256x256, 512x512
- Format: ICO (Windows), PNG (source)
- Style: Modern, recognizable, professional
- Theme: Related to object detection / AI / vision

**Suggested Design**:
- Simple geometric shape (square or circle)
- Bounding box motif
- Neural network element
- Blue/purple gradient or solid color

---

## Spacing and Layout

### Spacing Scale

Use an 8-point grid system:

```
Spacing Values:
xs:   4px   (Tight spacing, inline elements)
sm:   8px   (Small gaps, related items)
md:   16px  (Default spacing, components)
lg:   24px  (Section spacing)
xl:   32px  (Major section breaks)
xxl:  48px  (Page sections)
```

### Layout Grid

**12-Column Grid System**:
- Container max-width: 1920px
- Gutter: 16px
- Margin: 24px

### Component Spacing

```
Component Padding:
- Buttons:          8px 16px
- Input Fields:     12px 16px
- Cards:            16px
- Panels:           24px
- Dialogs:          24px

Component Margins:
- Between sections: 24px
- Between elements: 16px
- Between items:    8px
```

---

## Component Styling

### Buttons

#### Primary Button
```css
.button-primary {
  background: #2196F3;
  color: #FFFFFF;
  border: none;
  border-radius: 4px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  text-transform: uppercase;
  cursor: pointer;
  transition: background 0.2s ease;
}

.button-primary:hover {
  background: #1976D2;
}

.button-primary:active {
  background: #1565C0;
}

.button-primary:disabled {
  background: #3F3F3F;
  color: #6B6B6B;
  cursor: not-allowed;
}
```

#### Secondary Button
```css
.button-secondary {
  background: transparent;
  color: #2196F3;
  border: 1px solid #2196F3;
  border-radius: 4px;
  padding: 8px 16px;
  /* ... same as primary ... */
}
```

### Input Fields

```css
.input-field {
  background: #1E1E1E;
  color: #FFFFFF;
  border: 1px solid #3F3F3F;
  border-radius: 4px;
  padding: 12px 16px;
  font-size: 16px;
  transition: border-color 0.2s ease;
}

.input-field:focus {
  outline: none;
  border-color: #2196F3;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2);
}

.input-field::placeholder {
  color: #808080;
}
```

### Cards / Panels

```css
.card {
  background: #1E1E1E;
  border: 1px solid #3F3F3F;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
}
```

### Sliders

```css
.slider {
  color: #2196F3;
}

.slider-thumb {
  width: 16px;
  height: 16px;
  background: #2196F3;
  border: 2px solid #FFFFFF;
  border-radius: 50%;
}

.slider-track {
  height: 4px;
  background: #3F3F3F;
}

.slider-rail {
  height: 4px;
  background: #2D2D2D;
}
```

---

## Animations and Transitions

### Transition Timing

```
Duration:
- Fast:     150ms  (Hover, focus)
- Normal:   250ms  (Expand/collapse, fade)
- Slow:     400ms  (Complex animations, page transitions)

Easing:
- Standard: cubic-bezier(0.4, 0.0, 0.2, 1)
- Decelerate: cubic-bezier(0.0, 0.0, 0.2, 1)
- Accelerate: cubic-bezier(0.4, 0.0, 1, 1)
```

### Common Animations

#### Fade In
```css
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.fade-in {
  animation: fadeIn 250ms ease-in;
}
```

#### Slide Down (Panel Expand)
```css
@keyframes slideDown {
  from {
    max-height: 0;
    opacity: 0;
  }
  to {
    max-height: 1000px;
    opacity: 1;
  }
}

.slide-down {
  animation: slideDown 400ms cubic-bezier(0.4, 0.0, 0.2, 1);
}
```

#### Progress Bar Pulse
```css
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.progress-pulse {
  animation: pulse 1.5s ease-in-out infinite;
}
```

### Hover Effects

```css
/* Elevation on Hover */
.hover-lift {
  transition: transform 150ms ease, box-shadow 150ms ease;
}

.hover-lift:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

/* Color Transition */
.hover-color {
  transition: color 150ms ease, background 150ms ease;
}
```

---

## Accessibility

### WCAG 2.1 Level AA Compliance

#### Contrast Ratios
```
Required Ratios:
- Normal text (< 18px):      4.5:1 minimum
- Large text (≥ 18px/14px bold): 3:1 minimum
- UI components:             3:1 minimum
- Active UI components:      3:1 minimum
```

#### Color Contrast Check
```
Dark Theme:
✓ White (#FFFFFF) on Dark Background (#121212): 15.8:1
✓ Light Grey (#B0B0B0) on Dark Background (#121212): 7.9:1
✓ Primary Blue (#2196F3) on Dark Background (#121212): 5.2:1
✓ Success Green (#4CAF50) on Dark Background (#121212): 5.1:1
✓ Error Red (#F44336) on Dark Background (#121212): 4.7:1
```

### Keyboard Navigation

```
Focus Indicators:
- Visible outline: 2px solid #2196F3
- Offset: 2px from element
- Border-radius: Match element
```

```css
*:focus-visible {
  outline: 2px solid #2196F3;
  outline-offset: 2px;
}
```

### Screen Reader Support

```html
<!-- Button with label -->
<button aria-label="Upload images">
  <UploadIcon />
</button>

<!-- Input with label -->
<label for="confidence">Confidence Threshold</label>
<input id="confidence" type="number" aria-describedby="confidence-help" />
<span id="confidence-help">Minimum confidence score for detections</span>

<!-- Progress indicator -->
<div role="progressbar" aria-valuenow="65" aria-valuemin="0" aria-valuemax="100">
  65% Complete
</div>
```

---

## Responsive Design

### Breakpoints

```
Screen Sizes:
- xs: 0-599px      (Small phones)
- sm: 600-959px    (Large phones, small tablets)
- md: 960-1279px   (Tablets, small laptops)
- lg: 1280-1919px  (Laptops, desktops)
- xl: 1920px+      (Large desktops)
```

### Responsive Layout

**Desktop (≥1280px)**:
- Full 3-column layout
- Left panels: 300-350px
- Main content: Flexible
- Bottom panel: 250-300px

**Tablet (960-1279px)**:
- Collapsible left panels
- Main content: Full width
- Bottom panel: Collapsible

**Mobile (< 960px)**:
- Single column layout
- All panels as tabs or drawer navigation
- Full-width components
- Touch-optimized controls (larger tap targets)

---

## Asset Requirements

### Application Icons

**File Format**: ICO for Windows, PNG for development

**Sizes Required**:
- 16x16 (taskbar)
- 32x32 (taskbar, list view)
- 48x48 (large icons)
- 64x64 (extra large icons)
- 128x128 (tiles)
- 256x256 (high DPI)
- 512x512 (source)

### Splash Screen (Optional)

**Dimensions**: 800x600px  
**Format**: PNG with transparency  
**Content**: App logo, name, loading indicator

### Empty State Illustrations

**Style**: Simple, line-based illustrations  
**Size**: 200-300px  
**Format**: SVG (scalable)  
**Content**:
- No images uploaded
- No results yet
- No data available
- Error state

### Sample Images

For demonstration/testing:
- Sample detection image (1920x1080)
- Sample results with bounding boxes
- Sample charts and metrics

---

## Design Tokens (JSON)

For easier integration with code:

```json
{
  "colors": {
    "dark": {
      "background": {
        "primary": "#121212",
        "secondary": "#1E1E1E",
        "elevated": "#2D2D2D"
      },
      "text": {
        "primary": "#FFFFFF",
        "secondary": "#B0B0B0",
        "disabled": "#6B6B6B"
      },
      "accent": {
        "primary": "#2196F3",
        "secondary": "#FF9800",
        "success": "#4CAF50",
        "error": "#F44336",
        "warning": "#FF9800"
      }
    }
  },
  "spacing": {
    "xs": "4px",
    "sm": "8px",
    "md": "16px",
    "lg": "24px",
    "xl": "32px",
    "xxl": "48px"
  },
  "typography": {
    "fontFamily": {
      "primary": "Roboto, sans-serif",
      "mono": "Roboto Mono, monospace"
    },
    "fontSize": {
      "h1": "32px",
      "h2": "24px",
      "h3": "20px",
      "body": "16px",
      "caption": "12px"
    }
  },
  "borderRadius": {
    "small": "4px",
    "medium": "8px",
    "large": "16px"
  },
  "transitions": {
    "fast": "150ms",
    "normal": "250ms",
    "slow": "400ms"
  }
}
```

---

## Summary

This visual design guideline ensures:

✅ Consistent visual language across the application  
✅ Professional, modern appearance  
✅ Accessibility compliance (WCAG 2.1 AA)  
✅ Responsive design for various screen sizes  
✅ Clear component styling specifications  
✅ Smooth animations and transitions  
✅ Complete asset requirements  

Use these guidelines during implementation to maintain design consistency and quality throughout the application.
