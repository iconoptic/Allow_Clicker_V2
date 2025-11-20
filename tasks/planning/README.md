# Color Rectangle Capture Script with OCR and Auto-Click

This script runs in the background and captures all rectangles with a background color matching a reference color. It then uses OCR to filter and only save images containing specific text. Automatically clicks on detected rectangles using **AutoHotkey** (for better VM compatibility) and restores the cursor. It polls every 1 second and overwrites previous captures.

## Features

- **Background Color Matching**: Automatically detects the dominant color from `assets/color_ref.png`
- **Rectangle Detection**: Finds and captures all rectangles matching the reference color
- **OCR Text Filtering**: Uses Tesseract OCR to extract text and only save images containing "Allow"
- **Auto-Click (VM-Compatible)**: Uses AutoHotkey for reliable clicking in virtual machines, with PyAutoGUI fallback
- **Continuous Polling**: Runs every 1 second and updates the captures folder
- **Auto-Cleanup**: Overwrites previous captures on each poll
- **Configurable**: Adjust color tolerance, search text, and OCR settings

## Setup

### 1. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 2. Install Tesseract OCR

The script requires Tesseract for OCR functionality.

**Windows:**
- Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
- Install to default location: `C:\Program Files\Tesseract-OCR`
- Or add to PATH environment variable

**Alternative:** If Tesseract is installed elsewhere, update the path in the script:
```python
pytesseract.pytesseract.pytesseract_cmd = r'C:\path\to\tesseract.exe'
```

### 3. Install AutoHotkey (Required for clicking in VMs)

The script uses **AutoHotkey** for mouse clicks, which works better in virtual machine environments than PyAutoGUI.

**Windows:**
- Download AutoHotkey v2.0+: https://www.autohotkey.com/download/
- **Install to default location** (`C:\Program Files\AutoHotkey`) - the script will find it automatically
- Or manually add to PATH after installation
- Verify installation by running: `AutoHotkey.exe --version` in PowerShell

**Why AutoHotkey?**
- Works reliably in virtual machines (VirtualBox, VMware, Hyper-V)
- Uses lower-level Windows API for more reliable input simulation
- Better compatibility with event-driven applications
- Falls back to PyAutoGUI if AutoHotkey is unavailable
- The script automatically searches common installation locations

**If AutoHotkey is Not Installed:**
- The script will automatically fall back to PyAutoGUI
- Clicks will still work, just with slightly less reliability in VMs
- You'll see: `[INFO] AutoHotkey.exe not found in PATH. Falling back to PyAutoGUI...`

### 4. Prepare Color Reference

Place your reference color image at:
```
assets/color_ref.png
```

The script will extract the dominant color from this image.

### 5. Run the Script

```powershell
python color_capture.py
```

The script will:
1. Read the reference color from `assets/color_ref.png`
2. Start polling the screen every 1 second
3. Find all matching rectangles
4. Use OCR to extract text from each rectangle
5. Save only images containing "Allow" to `captures/` folder
6. Automatically click on detected rectangles (using AutoHotkey if available, PyAutoGUI otherwise)
7. Restore cursor to original position
8. Continuously overwrite captures with the latest results

Press `Ctrl+C` to stop the script.

## Running with Watchdog (Recommended for Production)

For unattended, continuous operation, use the **watchdog** to monitor and automatically restart the color_capture script if it crashes:

### Quick Start

```powershell
.\run_watchdog.bat
```

Or in PowerShell:
```powershell
.\run_watchdog.ps1
```

### What the Watchdog Does

- **Monitors** the color_capture.py process continuously
- **Auto-restarts** if the process crashes or is killed
- **Exponential backoff** - gradually increases delay between restart attempts
- **Graceful shutdown** - Press Ctrl+C to cleanly stop both watchdog and process
- **Detailed logging** - Shows timestamps and status of all events

### Command-Line Options

```powershell
python watchdog.py --interval 10          # Check every 10 seconds (default: 5)
python watchdog.py --max-attempts 20      # Restart up to 20 times (default: 10)
python watchdog.py --script custom.py     # Monitor a different script
```

### Example Output

```
============================================================
Iteration 1 | Time: 16:53:04
============================================================
Found 13 color-matching rectangle(s)
[OK] 1 rectangle(s) passed OCR filter, saving to disk...
[OK] Clicked 1 rectangle(s), cursor restored

[Process dies unexpectedly]

[2025-11-11 16:24:15] [WARNING] Process is not running!
[2025-11-11 16:24:15] [INFO] Waiting 2s before restart...
[2025-11-11 16:24:17] [INFO] Process started with PID 12346 (Restart #2)
```

See `WATCHDOG.md` for detailed documentation.

## Output

Captured images are saved in the `captures/` folder with names like:
- `capture_0000.png`
- `capture_0001.png`
- `capture_0002.png`
- etc.

Each capture includes the bounding box coordinates and dimensions in the console output.

## Configuration

Edit these variables in `color_capture.py` to customize behavior:

```python
POLL_INTERVAL = 1  # Time between captures (in seconds)
COLOR_TOLERANCE = 30  # Color matching tolerance (0-255)
OCR_SEARCH_TEXT = "Allow"  # Text to search for in images
OCR_ENABLED = True  # Set to False to disable OCR filtering
AUTO_CLICK_ENABLED = True  # Set to False to disable auto-clicking
CLICK_DELAY = 0.2  # Delay between cursor movement and click (seconds)
```
DEBUG_MODE = True  # Enable detailed logging
```

### Color Tolerance Explanation

- **Lower values (0-15)**: Strict color matching, only exact colors
- **Medium values (20-30)**: Good balance, captures variations
- **Higher values (40+)**: Loose matching, captures color range

### OCR Configuration

- **OCR_SEARCH_TEXT**: Change this to search for different text (case-insensitive)
- **OCR_ENABLED**: Set to `False` to save all rectangles without text filtering

### Auto-Click Configuration

- **AUTO_CLICK_ENABLED**: Set to `True` to automatically click on detected rectangles
  - The script saves the current cursor position before clicking
  - Clicks on the center of each rectangle
  - Automatically restores the cursor to its original position after all clicks
  - Even if an error occurs, cursor position is always restored

## Troubleshooting

- **"Color reference image not found"**: Ensure `assets/color_ref.png` exists
- **No rectangles found**: Check that your reference color is on the screen and the tolerance is appropriate
- **Too many false positives**: Reduce `COLOR_TOLERANCE` value
- **Captures not updating**: Check write permissions in the script directory

## Requirements

- Python 3.7+
- OpenCV (cv2)
- NumPy
- PyAutoGUI
- Pillow (PIL)
- Pytesseract
- Tesseract-OCR executable (separate system installation)

## System Tray / Background Mode

To run this script as a background service without a visible console window, create a batch file and use Windows Task Scheduler.

See `run_background.bat` (if present) for an example.
