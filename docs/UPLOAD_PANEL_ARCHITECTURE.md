# Upload Panel Component Architecture

## Component Hierarchy

```
UploadPanel (Main Component)
├── Paper (Material-UI container)
│   ├── Header Section
│   │   ├── CloudUploadIcon
│   │   └── "Upload Images" Typography
│   │
│   ├── Error Alert (conditional)
│   │   └── Alert with close button
│   │
│   ├── Drop Zone (react-dropzone)
│   │   ├── CloudUploadIcon (large, 48px)
│   │   ├── Main Text (drag or browse message)
│   │   └── Caption (supported formats)
│   │
│   └── File List Section (conditional, shown when files.length > 0)
│       ├── Header Row
│       │   ├── "Uploaded Images (N)" Typography
│       │   └── "Clear All" Button
│       │
│       └── Scrollable List
│           └── FileListItem[] (map over files)
│               ├── ListItemAvatar
│               │   └── Avatar (56×56)
│               │       └── Image Preview or ImageIcon
│               ├── ListItemText
│               │   ├── Primary: File Name
│               │   └── Secondary: File Size
│               └── IconButton (Delete)
│                   └── DeleteIcon
```

## Data Flow

```
User Action (Drop/Click)
    ↓
react-dropzone (onDrop callback)
    ↓
File Validation
    ├── Format Check (MIME type)
    ├── Size Check (< 50MB)
    └── Generate Preview (FileReader API)
    ↓
Validation Results
    ├── Valid Files → dispatch(addFiles(validFiles))
    └── Invalid Files → dispatch(setUploadError(message))
    ↓
Redux Store (uploadSlice)
    ├── files: UploadedFile[]
    └── error: string | null
    ↓
Component Re-render
    ├── Update File List
    └── Show/Hide Error Alert
```

## Redux Integration

```typescript
// State Selectors
const { files, error } = useSelector((state: RootState) => state.upload);

// Actions Dispatched
dispatch(addFiles(validFiles));           // Add files to state
dispatch(removeFile(fileId));             // Remove single file
dispatch(clearFiles());                   // Clear all files
dispatch(setUploadError(message));        // Set error message
dispatch(clearUploadError());             // Clear error message
```

## File Validation Flow

```
File Selected
    ↓
react-dropzone validates:
    ├── MIME Type ∈ {image/jpeg, image/png, image/bmp, image/tiff}
    ├── File Size ≤ 50MB
    └── Multiple files allowed
    ↓
    ├── Accepted Files → onDrop(acceptedFiles)
    └── Rejected Files → fileRejections[]
        ↓
        useEffect → dispatch(setUploadError())
        ↓
        Alert Banner Shown
```

## Preview Generation

```
Accepted File
    ↓
FileReader API
    ├── reader = new FileReader()
    ├── reader.onload = () => { ... }
    └── reader.readAsDataURL(file)
    ↓
Base64 String Generated
    ↓
Store in UploadedFile.preview
    ↓
Display in Avatar Component
```

## Visual States

### 1. Empty State
```
┌─────────────────────────────────┐
│ 📁 Upload Images                │
├─────────────────────────────────┤
│                                 │
│   ┌─────────────────────────┐  │
│   │   ☁️  (48px icon)        │  │
│   │                         │  │
│   │ Drag & drop files here  │  │
│   │    or click to browse   │  │
│   │                         │  │
│   │ Supported: JPG, PNG...  │  │
│   └─────────────────────────┘  │
│                                 │
│   No files uploaded yet         │
│                                 │
└─────────────────────────────────┘
```

### 2. Drag Active State
```
┌─────────────────────────────────┐
│ 📁 Upload Images                │
├─────────────────────────────────┤
│                                 │
│   ┌─────────────────────────┐  │
│   │   ☁️  (blue, 48px)      │  │ ← Blue border
│   │                         │  │   Blue background
│   │   Drop files here...    │  │
│   │                         │  │
│   │                         │  │
│   └─────────────────────────┘  │
│                                 │
└─────────────────────────────────┘
```

### 3. Files Uploaded State
```
┌─────────────────────────────────┐
│ 📁 Upload Images                │
├─────────────────────────────────┤
│                                 │
│   ┌─────────────────────────┐  │
│   │   ☁️                    │  │
│   │ Drag & drop files...    │  │
│   └─────────────────────────┘  │
│                                 │
│   Uploaded Images (3) [Clear]   │
│   ┌───────────────────────┐    │
│   │ 📷 image1.jpg         🗑️│   │
│   │    2.3 MB             │    │
│   ├───────────────────────┤    │
│   │ 📷 image2.png         🗑️│   │
│   │    1.8 MB             │    │
│   ├───────────────────────┤    │
│   │ 📷 image3.jpg         🗑️│   │
│   │    3.1 MB             │    │
│   └───────────────────────┘    │
└─────────────────────────────────┘
```

### 4. Error State
```
┌─────────────────────────────────┐
│ 📁 Upload Images                │
├─────────────────────────────────┤
│ ⚠️ Error: file.txt: Invalid... │ ← Red Alert
├─────────────────────────────────┤
│                                 │
│   ┌─────────────────────────┐  │
│   │   ☁️                    │  │
│   │ Drag & drop files...    │  │
│   └─────────────────────────┘  │
│                                 │
└─────────────────────────────────┘
```

## Styling Details

### Colors (Dark Theme)
- Background: #1E1E1E (Paper)
- Border (inactive): theme.palette.divider
- Border (active/hover): #2196F3 (primary blue)
- Text: theme.palette.text.primary
- Error: #F44336 (red)
- Icon (inactive): theme.palette.text.secondary
- Icon (active): #2196F3 (primary blue)

### Dimensions
- Drop Zone Padding: 24px (p: 3)
- Drop Zone Border: 2px dashed
- Icon Size: 48px (large upload icon)
- Avatar Size: 56×56 pixels
- List Item Gap: 8px (mb: 1)
- Scrollbar Width: 8px

### Transitions
- All: 0.2s ease-in-out
- Hover effects on drop zone
- Border and background color changes

## TypeScript Types

```typescript
interface UploadedFile {
  id: string;              // "${timestamp}-${random}"
  name: string;            // Original filename
  size: number;            // Bytes
  path: string;            // File path or name
  preview?: string;        // Base64 data URL
  uploadedAt: Date;        // Upload timestamp
}

interface FileListItemProps {
  file: UploadedFile;
  onRemove: () => void;
}
```

## Performance Considerations

1. **File Reading**: Async operation with FileReader API
2. **Preview Generation**: Done client-side, no backend needed
3. **Memory**: Base64 previews stored in Redux (cleared on refresh)
4. **Rendering**: Virtualization not needed (typical batch < 100 files)
5. **Validation**: Immediate feedback via react-dropzone

## Browser Compatibility

- FileReader API: All modern browsers
- Drag-and-drop: All modern browsers
- Base64 encoding: All browsers
- Material-UI: React 18+ compatible

---

**Last Updated:** 2026-02-06
**Component Version:** 1.0.0
**Status:** Production Ready ✅
