# Allow Clicker V2

A Python automation script that detects "Allow" buttons on screen, captures them via OCR, and automatically clicks them. Optimized for virtual machines with AutoHotkey integration.

## Features

✨ **Core Features**
- 🎯 **Color-Based Detection**: Detects rectangles matching a reference color (configurable)
- 🔍 **OCR Text Filtering**: Uses Tesseract OCR to identify rectangles containing "Allow" text
- 🖱️ **Auto-Click**: Automatically clicks detected allow buttons
- 🔄 **Continuous Polling**: Scans screen every 1 second, updates results in real-time
- 💾 **Auto-Cleanup**: Overwrites previous captures with latest results

🚀 **VM-Optimized**
- **AutoHotkey Integration**: Uses AutoHotkey v2 for reliable clicking in VMs (VirtualBox, VMware, Hyper-V)
- **Fallback Support**: Automatically falls back to PyAutoGUI if AutoHotkey unavailable
- **Cursor Restoration**: Automatically restores mouse cursor position after clicks
- **Input Validation**: Multiple click methods (mouse movement, double-click, keyboard fallback)

🔧 **Robust & Configurable**
- Adjustable color tolerance for flexible detection
- Configurable OCR search text
- Debug logging for troubleshooting
- Command-line friendly, background-capable

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/iconoptic/Allow_Clicker_V2.git
cd Allow_Clicker_V2
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Tesseract OCR

**Windows (recommended):**
```bash
# Download and run installer from:
# https://github.com/UB-Mannheim/tesseract/wiki
# Install to default: C:\Program Files\Tesseract-OCR
```

Or if installed elsewhere:
```python
# Edit color_capture_core.py:
pytesseract.pytesseract.pytesseract_cmd = r'C:\your\path\to\tesseract.exe'
```

### 4. Install AutoHotkey v2 (Required for VM Clicking)

**Windows:**
```bash
# Download from: https://www.autohotkey.com/download/
# Install to default: C:\Program Files\AutoHotkey\v2\AutoHotkey.exe
# Verify: AutoHotkey.exe --version
```

**Why AutoHotkey?** PyAutoGUI clicks don't work reliably in VMs. AutoHotkey uses lower-level Windows APIs.

### 5. Prepare Color Reference

Place your reference color image at:
```
assets/color_ref.png
```

The script extracts the dominant color from this image.

### 6. Run

```bash
python color_capture.py
```

Press `Ctrl+C` to stop.

## Configuration

Edit `color_capture.py` to customize:

```python
# Polling and detection
POLL_INTERVAL = 1              # Seconds between scans
COLOR_TOLERANCE = 30           # Color match tolerance (0-255)

# OCR settings
OCR_SEARCH_TEXT = "Allow"      # Text to search for (case-insensitive)
OCR_ENABLED = True             # Set to False to capture all rectangles

# Clicking
AUTO_CLICK_ENABLED = True      # Set to False to disable auto-clicking
CLICK_DELAY = 0.5              # Delay before click (seconds)

# Debug
DEBUG_MODE = True              # Enable detailed console output
USE_AUTOHOTKEY = True          # Use AutoHotkey (fallback to PyAutoGUI if unavailable)
```

## How It Works

1. **Color Detection**: Analyzes screen pixels, finds rectangles matching reference color
2. **OCR Extraction**: Crops each rectangle, extracts text using Tesseract
3. **Filtering**: Only keeps rectangles containing search text ("Allow")
4. **Saving**: Saves matching captures to `captures/` folder
5. **Clicking**: Automatically clicks center of each matching rectangle
6. **Cleanup**: Overwrites previous results on next poll

## Output

Captured images saved to `captures/` as:
- `capture_0000.png`
- `capture_0001.png`
- etc.

Console shows:
```
Found 11 color-matching rectangle(s)

Processing rectangles:
  Rectangle [6] at (1903, 972) size 71x24:
    OCR extracted: 'Allow | ~'
    Contains 'Allow': True
    [PASS] will be stored

[OK] 1 rectangle(s) passed OCR filter, saving to disk...
→ Saved to disk: capture_0006.png
[OK] Saved 1 image(s) to ./captures

[INFO] Auto-clicking on 1 rectangle(s)...
  Saved cursor position: (3214, 884)
  Moving to (1938, 984)...
  Clicking at (1938, 984) via AutoHotkey
  Click #1 completed
  Restoring cursor to: (3214, 884)
[OK] Clicked 1 rectangle(s), cursor restored
```

## Architecture

```
Allow_Clicker_V2/
├── color_capture.py           # Main entry point, configuration, polling loop
├── color_capture_core.py       # Core ColorCapture class, OCR logic, clicking
├── click_helper.ahk            # AutoHotkey v2 script for VM-compatible clicking
├── requirements.txt            # Python dependencies
├── assets/
│   └── color_ref.png          # Reference color image (user-provided)
├── captures/                   # Output folder (auto-created)
└── tests/
    ├── test_color_capture.py   # Unit tests
    └── test_integration_manual.py # Integration tests
```

## Key Components

### color_capture.py
- Entry point
- Configuration variables
- Main polling loop
- Screen capture and processing orchestration

### color_capture_core.py
- `ColorCapture` class: main logic
- `find_autohotkey_exe()`: locates AutoHotkey installation
- Methods:
  - `find_matching_rectangles()`: color-based detection
  - `process_rectangles()`: OCR filtering
  - `save_captures_to_disk()`: image storage
  - `click_captures()`: auto-clicking with fallbacks

### click_helper.ahk
- AutoHotkey v2 script
- Receives coordinates via command-line arguments
- Activates target window
- Performs double-click for reliability
- Logs click coordinates to temp file for debugging

## Troubleshooting

### "AutoHotkey: NOT FOUND"
- Install AutoHotkey v2 to default location, or add to PATH
- Script will fall back to PyAutoGUI (less reliable in VMs)

### No rectangles detected
- Verify reference color is on screen
- Increase `COLOR_TOLERANCE` (try 40-50)
- Check `assets/color_ref.png` exists

### Clicks not working
- Verify target window is focused (AutoHotkey tries to activate)
- Check if clicks register in normal apps first (might be app-specific)
- Enable `DEBUG_MODE = True` and check coordinate logs
- Try reducing `CLICK_DELAY` or increasing it (0.3-0.7)

### OCR not extracting text
- Verify Tesseract installed and in PATH
- Check rectangle crop size (too small rectangles fail OCR)
- Try `pytesseract.pytesseract.pytesseract_cmd` configuration

### Performance issues
- Reduce `POLL_INTERVAL` decreases polling frequency
- Disable `DEBUG_MODE` reduces console I/O
- Crop screenshot to region of interest in code

## Testing

Run tests:
```bash
# Unit tests
pytest test_color_capture.py -v

# All tests
pytest -v
```

## System Requirements

- **Python**: 3.7+
- **OS**: Windows (uses AutoHotkey v2)
- **Dependencies**:
  - opencv-python (image processing)
  - numpy (array operations)
  - pyautogui (screen capture, fallback clicking)
  - Pillow (image handling)
  - pytesseract (OCR wrapper)
  - **Tesseract-OCR** (system binary, not pip)
  - **AutoHotkey v2** (system binary, optional but recommended)

## Performance Notes

- **Screen Capture**: ~50-100ms per frame
- **OCR Processing**: ~100-500ms per rectangle (depends on size/complexity)
- **Total Cycle**: ~1-2 seconds per poll (typical)
- **Memory**: ~100-200MB (Python + OpenCV)

## VM Compatibility

Tested on:
- ✅ VirtualBox (6.1+)
- ✅ VMware (Player & Workstation)
- ✅ Hyper-V
- ✅ Local Windows

AutoHotkey is more reliable than PyAutoGUI in VMs due to lower-level Windows API usage.

## License

[Add your license here]

## Contributing

Issues and pull requests welcome!

## Author

iconoptic

---

**Need Help?** Check the [troubleshooting guide](#troubleshooting) or open an issue on GitHub.
