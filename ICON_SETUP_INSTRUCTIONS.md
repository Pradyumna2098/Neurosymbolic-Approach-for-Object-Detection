# Icon Setup Instructions

## Overview

The Inno Setup installer script (`installer.iss`) references an icon file that needs to be created for a professional-looking installer.

## Required Icon

**Location:** `frontend/src/assets/icon.ico`

**Purpose:**
- Installer executable icon
- Application icon in Windows
- Start Menu shortcut icon
- Desktop shortcut icon

## Creating the Icon

### Option 1: Use Existing Logo/Image

If you have a logo or image for the application:

1. **Create the assets directory:**
   ```bash
   mkdir -p frontend/src/assets
   ```

2. **Convert your image to .ico format:**
   - Use an online converter: https://convertio.co/png-ico/
   - Or use ImageMagick: `convert logo.png -define icon:auto-resize=256,128,64,48,32,16 frontend/src/assets/icon.ico`

3. **Icon Requirements:**
   - Format: ICO file
   - Recommended sizes: 16x16, 32x32, 48x48, 64x64, 128x128, 256x256
   - Transparent background recommended
   - Should represent the application clearly

### Option 2: Use a Default Icon

If you don't have a custom icon yet:

1. **Create assets directory:**
   ```bash
   mkdir -p frontend/src/assets
   ```

2. **Download a placeholder:**
   - Search for "object detection icon" on icon sites
   - Or use a generic application icon

3. **Place in correct location:**
   ```bash
   cp your-icon.ico frontend/src/assets/icon.ico
   ```

### Option 3: Skip Icon for Now

If you want to build without an icon:

1. **Comment out the icon line in `installer.iss`:**
   ```pascal
   ; SetupIconFile=frontend\src\assets\icon.ico
   ```

2. **The installer will use the default Windows application icon**

## Verifying Icon Setup

After adding the icon:

1. **Check file exists:**
   ```bash
   ls -la frontend/src/assets/icon.ico
   ```

2. **Rebuild installer:**
   ```bash
   python build_installer.py
   ```

3. **Verify icon appears:**
   - In Windows Explorer on the installer file
   - During installation wizard
   - On installed shortcuts

## Recommended Icon Design

For best results, your icon should:

✓ Be simple and recognizable at small sizes  
✓ Use high contrast colors  
✓ Avoid fine details that disappear when scaled down  
✓ Match your application's branding  
✓ Be professional and polished  

## Example Icon Sources

Free icon resources:
- **Icons8:** https://icons8.com/
- **Flaticon:** https://www.flaticon.com/
- **Iconfinder:** https://www.iconfinder.com/
- **The Noun Project:** https://thenounproject.com/

Search terms:
- "object detection"
- "AI detection"
- "computer vision"
- "neural network"
- "bounding box"

## Notes

- The icon file is optional but highly recommended for professional appearance
- If missing, the installer will use default Windows icons
- The same icon should be used for Electron app configuration
- Consider creating multiple sizes for different use cases
- Icon should be added to version control once created

## Current Status

⚠️ **Icon file not yet created** - See options above to add an icon before building the installer.
