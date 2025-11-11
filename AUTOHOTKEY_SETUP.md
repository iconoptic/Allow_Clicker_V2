# AutoHotkey Setup & Configuration

## Why AutoHotkey?

The script now uses **AutoHotkey** for mouse clicks instead of PyAutoGUI. This provides better compatibility with virtual machines (VirtualBox, VMware, Hyper-V, etc.).

### Benefits of AutoHotkey over PyAutoGUI:
- ✅ **VM-Compatible**: Works reliably in virtual machine environments
- ✅ **Lower-Level API**: Uses Windows API directly for more reliable input simulation
- ✅ **Event Handling**: Better compatibility with event-driven applications
- ✅ **Fallback Support**: Automatically falls back to PyAutoGUI if AutoHotkey is unavailable

## Installation

### Step 1: Download AutoHotkey

1. Go to: https://www.autohotkey.com/download/
2. Download **AutoHotkey v2.0** or later (NOT v1.1)
3. Run the installer
4. Choose "Install for current user" or "Install for all users"
5. Install to default location (recommended): `C:\Program Files\AutoHotkey`

### Step 2: Add AutoHotkey to PATH (Optional but Recommended)

If AutoHotkey is not automatically in PATH:

**Windows 10/11:**
1. Press `Win + R` → type `sysdm.cpl` → press Enter
2. Click "Environment Variables"
3. Under "User variables" click "New"
4. Variable name: `PATH`
5. Variable value: `C:\Program Files\AutoHotkey`
6. Click OK and restart terminal

**Or in PowerShell:**
```powershell
$env:PATH += ";C:\Program Files\AutoHotkey"
```

### Step 3: Verify Installation

```powershell
AutoHotkey.exe --version
```

You should see output like:
```
AutoHotkey 2.0-xxxx
```

## Configuration

### Enable/Disable AutoHotkey in Script

Edit `color_capture.py`:

```python
USE_AUTOHOTKEY = True   # Set to False to disable (uses PyAutoGUI instead)
```

### Click Delay Adjustment

If clicks don't register, increase the delay in `color_capture.py`:

```python
CLICK_DELAY = 0.2   # Default: 200ms
# Try these values if clicks don't work:
CLICK_DELAY = 0.5   # 500ms - for slower VMs
CLICK_DELAY = 1.0   # 1000ms - for very slow VMs
```

## How AutoHotkey Clicking Works

### click_helper.ahk

The script uses a helper AutoHotkey script (`click_helper.ahk`) that:

1. Receives click coordinates as command-line arguments
2. Moves mouse to position
3. Waits for specified delay
4. Performs the click
5. Returns control to Python

### Python Integration

When `USE_AUTOHOTKEY = True`:

```
Python → subprocess.run(['AutoHotkey.exe', 'click_helper.ahk', x, y, delay]) → Click executed
                                                                                    ↓
                                                                        Fallback to PyAutoGUI if fails
```

## Troubleshooting

### AutoHotkey.exe not found

**Error:**
```
FileNotFoundError: [WinError 2] The system cannot find the file specified
```

**Solution:**
1. Verify AutoHotkey is installed: `AutoHotkey.exe --version`
2. If not found, add to PATH (see Step 2 above)
3. Or set `USE_AUTOHOTKEY = False` in `color_capture.py`

### Clicks still not working in VM

1. **Increase CLICK_DELAY** (see Configuration section)
2. **Check VM settings**:
   - Ensure mouse integration is enabled
   - Try disabling 3D acceleration
   - Update VM tools/drivers
3. **Test with manual click**: Click same coordinates with mouse
4. **Check window focus**: Ensure application window is in focus
5. **Set DEBUG_MODE = True** to see detailed logging

### Mixed results (some clicks work, some don't)

This usually indicates timing issues:

```python
# Increase delays
CLICK_DELAY = 0.5   # Increase from default 0.2
```

Or disable AutoHotkey and test with PyAutoGUI:
```python
USE_AUTOHOTKEY = False
```

## Performance Notes

### Typical Click Timing

With `CLICK_DELAY = 0.2` (200ms):
- Move to position: 100ms (smooth movement)
- Wait: 200ms
- Click: ~50ms
- **Total per click**: ~350ms

For multiple rectangles (N clicks):
```
Total time ≈ 350ms × N
```

### VM Performance

AutoHotkey is typically:
- **5-10x faster** than PyAutoGUI in VMs
- **More reliable** with event-driven applications
- **Minimal overhead** compared to Python subprocess call

## Advanced Configuration

### Custom AHK Script Path

If you need to use a different AutoHotkey script:

```python
from color_capture_core import ColorCapture

cc = ColorCapture(
    color_ref_path,
    captures_dir,
    use_ahk=True,
    ahk_script_path="/path/to/custom/script.ahk"
)
```

### Custom Click Behavior

Edit `click_helper.ahk` to customize click behavior:

```autohotkey
; Example: Add double-click support
Click, x, y, 2  ; Double-click instead of single-click
```

## Testing AutoHotkey Integration

### Manual Test

```powershell
# Click at position 500, 500 with 200ms delay
AutoHotkey.exe .\click_helper.ahk 500 500 200
```

### With Python

```python
from color_capture_core import ColorCapture
from pathlib import Path

cc = ColorCapture(
    Path("assets/color_ref.png"),
    Path("captures"),
    use_ahk=True,
    debug_mode=True
)

# Mock capture at position 500, 500
valid_captures = [{'coords': (450, 475, 100, 50), 'image': None, 'index': 0}]
cc.click_captures(valid_captures)
```

## Fallback Behavior

If AutoHotkey fails for any reason:

1. **Script missing**: Falls back to PyAutoGUI
2. **AutoHotkey.exe not found**: Falls back to PyAutoGUI
3. **AutoHotkey timeout**: Falls back to PyAutoGUI
4. **AutoHotkey execution error**: Falls back to PyAutoGUI

**Logging:**
```
[WARNING] AutoHotkey failed: [error details]. Falling back to PyAutoGUI...
```

This ensures the script always works, even if AutoHotkey is unavailable.

## FAQs

**Q: Do I need to install AutoHotkey for each user?**
A: If installed "for all users", no. If "for current user", yes - install for each user.

**Q: Can I use AutoHotkey v1.1?**
A: Not recommended. The script expects v2.0+. For v1.1, you'd need to modify `click_helper.ahk`.

**Q: Does AutoHotkey work on Windows 7/8?**
A: Yes, but you must use AutoHotkey v1.1. The script defaults to v2.0.

**Q: What if I'm in a VM with no AutoHotkey support?**
A: Use PyAutoGUI: `USE_AUTOHOTKEY = False`

**Q: How much does AutoHotkey impact performance?**
A: Minimal - subprocess overhead is ~50-100ms, which is acceptable for 1-second polling intervals.

## Support

For AutoHotkey issues:
- AutoHotkey Documentation: https://www.autohotkey.com/docs/
- GitHub Issues: https://github.com/AutoHotkey/AutoHotkey/issues

For script-specific issues:
- Enable DEBUG_MODE for detailed logging
- Check CLICK_TROUBLESHOOTING.md for diagnostic steps
