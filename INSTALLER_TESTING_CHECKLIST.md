# Windows Installer Testing Checklist

This checklist should be used when testing the Windows installer on clean Windows 10 and Windows 11 systems.

---

## Pre-Testing Setup

### Test Environment
- [ ] Clean Windows 10 64-bit VM or physical machine
- [ ] Clean Windows 11 64-bit VM or physical machine  
- [ ] At least 5 GB free disk space
- [ ] Administrator account access
- [ ] Internet connection (for downloading SWI-Prolog if needed)

### Optional: Install Dependencies
- [ ] SWI-Prolog 8.4.x or later (test with and without)
- [ ] NVIDIA GPU Drivers (test with and without if GPU available)

---

## Installer Build Testing

### Build Process
- [ ] Prerequisites installed (Python, Node.js, Inno Setup)
- [ ] Run `python build_installer.py`
- [ ] Build completes without errors
- [ ] Backend build successful (check `dist/neurosymbolic-backend/`)
- [ ] Frontend build successful (check `frontend/out/`)
- [ ] Installer created (check `installer_output/NeurosymbolicApp_Setup_v1.0.0.exe`)
- [ ] Installer size reasonable (~1.5-3 GB)

### Quick Build Testing
- [ ] Run `python build_installer.py --skip-backend --skip-frontend`
- [ ] Installer builds using existing artifacts
- [ ] Build time significantly reduced (< 5 minutes)

---

## Installation Testing

### Installation Wizard
- [ ] Double-click installer executable
- [ ] Installer launches successfully
- [ ] Modern wizard interface appears
- [ ] License agreement displays correctly
- [ ] License is MIT License
- [ ] User must accept license to proceed

### SWI-Prolog Check
- [ ] **With SWI-Prolog installed:** No warning appears
- [ ] **Without SWI-Prolog:** Warning appears but installation continues
- [ ] Warning message is clear and helpful

### Installation Options
- [ ] Installation directory shown correctly (C:\Program Files\Neurosymbolic Object Detection)
- [ ] Desktop shortcut option available
- [ ] Quick Launch shortcut option available
- [ ] Can customize installation options

### Installation Process
- [ ] Installation progress bar displays
- [ ] Files copy successfully
- [ ] No errors during installation
- [ ] Post-installation options appear:
  - [ ] Launch application option
  - [ ] View README option

### Installation Verification
- [ ] Installation directory created
- [ ] All expected folders present:
  - [ ] `frontend/`
  - [ ] `backend/`
  - [ ] `configs/`
  - [ ] `docs/`
  - [ ] `data/`
  - [ ] `models/`
  - [ ] `logs/`
- [ ] All expected files present:
  - [ ] `start_application.bat`
  - [ ] `start_backend.bat`
  - [ ] `README.txt`
  - [ ] `LICENSE.txt`
  - [ ] `EXECUTABLE_README.txt`

---

## Shortcuts Testing

### Start Menu Shortcuts
- [ ] Start Menu folder created: "Neurosymbolic Object Detection"
- [ ] Four shortcuts visible:
  1. [ ] Neurosymbolic Object Detection
  2. [ ] Neurosymbolic Object Detection Backend Server
  3. [ ] Neurosymbolic Object Detection Documentation
  4. [ ] Uninstall Neurosymbolic Object Detection

### Desktop Shortcut
- [ ] Desktop shortcut created (if option selected)
- [ ] Shortcut has correct name
- [ ] Shortcut icon appears (if icon configured)

### Quick Launch Shortcut
- [ ] Quick Launch shortcut created (if option selected)
- [ ] Accessible from taskbar

### Shortcut Functionality
- [ ] Main application shortcut launches frontend
- [ ] Backend server shortcut launches backend console
- [ ] Documentation shortcut opens user guide
- [ ] All shortcuts work from first click

---

## Application Testing

### Backend Server
- [ ] Run backend from Start Menu shortcut
- [ ] Backend console window opens
- [ ] No immediate errors displayed
- [ ] Server starts on http://localhost:8000
- [ ] Open browser and navigate to http://localhost:8000/docs
- [ ] FastAPI documentation page loads
- [ ] API endpoints visible

### Frontend Application
- [ ] Run frontend from Start Menu or Desktop shortcut
- [ ] Application window opens
- [ ] No errors in console (if dev tools opened)
- [ ] UI loads completely
- [ ] All panels visible:
  - [ ] Upload Panel
  - [ ] Config Panel
  - [ ] Image Canvas
  - [ ] Results Viewer
  - [ ] Monitoring Panel (if applicable)

### Combined Launcher
- [ ] Run `start_application.bat` from installation directory
- [ ] Backend console window opens
- [ ] Wait 5 seconds
- [ ] Frontend window opens automatically
- [ ] No errors in either window

### Basic Functionality
- [ ] Upload test image to frontend
- [ ] Configure inference parameters
- [ ] Run detection
- [ ] Results appear after processing
- [ ] Visualizations display correctly

---

## Data Directories Testing

### Directory Permissions
- [ ] Navigate to installation directory
- [ ] Check `data/` folder exists
- [ ] Create test file in `data/uploads/`
- [ ] Verify write permissions work
- [ ] Check subdirectories:
  - [ ] `data/uploads/`
  - [ ] `data/results/`
  - [ ] `data/visualizations/`
  - [ ] `data/jobs/`
- [ ] Verify `models/` directory exists and is writable
- [ ] Verify `logs/` directory exists and is writable

---

## External Dependencies Testing

### With SWI-Prolog Installed
- [ ] Symbolic reasoning features work
- [ ] No warnings about missing Prolog
- [ ] Prolog rules load successfully

### Without SWI-Prolog
- [ ] Application still runs
- [ ] Clear warning about missing Prolog
- [ ] Symbolic features gracefully disabled
- [ ] Other features work normally

### With NVIDIA GPU
- [ ] GPU detected correctly
- [ ] GPU acceleration available
- [ ] Inference faster than CPU

### Without GPU (CPU only)
- [ ] Application runs on CPU
- [ ] Inference works (slower)
- [ ] No GPU errors displayed

---

## Uninstaller Testing

### Uninstall Process
- [ ] Open "Add or Remove Programs" in Windows
- [ ] Find "Neurosymbolic Object Detection"
- [ ] Click Uninstall
- [ ] Confirmation dialog appears
- [ ] Confirm uninstall
- [ ] User data prompt appears:
  - [ ] Option to keep data
  - [ ] Option to remove data

### Uninstall Verification (Keep Data)
- [ ] Application files removed from Program Files
- [ ] Shortcuts removed from Start Menu
- [ ] Desktop shortcut removed
- [ ] Quick Launch shortcut removed
- [ ] `data/` directory still exists
- [ ] `models/` directory still exists

### Uninstall Verification (Remove Data)
- [ ] Application files removed
- [ ] Shortcuts removed
- [ ] `data/` directory removed
- [ ] User data cleaned up
- [ ] Installation directory removed if empty

### Reinstall Test
- [ ] Reinstall application after uninstall
- [ ] Installation succeeds
- [ ] All functionality works
- [ ] Previous data accessible (if kept)

---

## Performance Testing

### Installation Performance
- [ ] Installation time: _____ minutes
- [ ] Installation size: _____ GB
- [ ] Acceptable for user experience

### Application Performance
- [ ] Backend startup time: _____ seconds
- [ ] Frontend launch time: _____ seconds
- [ ] Combined launch time: _____ seconds
- [ ] Inference speed acceptable
- [ ] UI responsive

---

## Error Handling Testing

### Invalid Scenarios
- [ ] Run installer without admin rights → Should request elevation
- [ ] Install with insufficient disk space → Should warn
- [ ] Launch app without backend → Should show connection error
- [ ] Upload invalid file → Should show validation error
- [ ] Run inference without model → Should show error message

### Recovery
- [ ] Application handles errors gracefully
- [ ] Error messages are clear and helpful
- [ ] Application doesn't crash on errors
- [ ] Can recover from error states

---

## Documentation Testing

### README Files
- [ ] Open `README.txt` from installation directory
- [ ] Content is clear and helpful
- [ ] Instructions are accurate
- [ ] Links work (if any)

### User Guide
- [ ] Open `EXECUTABLE_README.txt`
- [ ] Complete and comprehensive
- [ ] Easy to follow
- [ ] Troubleshooting section helpful

### Documentation Shortcut
- [ ] Documentation shortcut opens correct file
- [ ] File opens in default text viewer/browser

---

## Windows SmartScreen Testing

### Security Warnings
- [ ] Note if SmartScreen warning appears
- [ ] "Unknown publisher" warning (expected if unsigned)
- [ ] Can bypass warning with "More info" → "Run anyway"
- [ ] Application runs normally after bypass

### Antivirus Testing
- [ ] Test with Windows Defender
- [ ] Test with common antivirus (if available)
- [ ] Note any false positives
- [ ] Application runs if allowed

---

## Compatibility Testing

### Windows 10
- [ ] Home Edition: _____ (Pass/Fail/Not Tested)
- [ ] Pro Edition: _____ (Pass/Fail/Not Tested)
- [ ] Version: _____
- [ ] Build: _____

### Windows 11
- [ ] Home Edition: _____ (Pass/Fail/Not Tested)
- [ ] Pro Edition: _____ (Pass/Fail/Not Tested)
- [ ] Version: _____
- [ ] Build: _____

---

## Issues Found

Document any issues found during testing:

### Critical Issues
1. _____________________________________
2. _____________________________________
3. _____________________________________

### Minor Issues
1. _____________________________________
2. _____________________________________
3. _____________________________________

### Suggestions
1. _____________________________________
2. _____________________________________
3. _____________________________________

---

## Test Results Summary

**Date:** _____________________  
**Tester:** _____________________  
**Environment:** _____________________  

**Overall Result:** ⬜ Pass / ⬜ Pass with Minor Issues / ⬜ Fail

**Ready for Production:** ⬜ Yes / ⬜ No / ⬜ With Fixes

**Recommended Actions:**
- [ ] _____________________________________
- [ ] _____________________________________
- [ ] _____________________________________

---

## Sign-off

**Tested by:** _____________________  
**Date:** _____________________  
**Signature:** _____________________  

**Approved by:** _____________________  
**Date:** _____________________  
**Signature:** _____________________
