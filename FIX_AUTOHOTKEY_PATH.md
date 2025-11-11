# Fix AutoHotkey PATH Issue

## Problem

AutoHotkey is installed but not in the Windows PATH environment variable. The script detects this and shows:

```
AutoHotkey: NOT FOUND (will use PyAutoGUI fallback)
```

## Solution: Add AutoHotkey to PATH

### Option 1: Permanent Fix (Recommended)

This adds AutoHotkey to your system PATH so it can be found from any terminal.

**Windows 10/11:**

1. Press `Win + X` then select "System"
2. Click "Advanced system settings" (or search for "Environment Variables")
3. Click "Environment Variables" button
4. Under "System variables" click "New"
   - Variable name: `AUTOHOTKEY_PATH`
   - Variable value: `C:\Program Files\AutoHotkey`
5. Click OK, then locate the `Path` variable in System variables
6. Click "Edit" on the `Path` variable
7. Click "New" and add: `C:\Program Files\AutoHotkey`
8. Click OK on all dialogs
9. **Restart your terminal/IDE** for changes to take effect
10. Verify: Open PowerShell and type: `AutoHotkey.exe --version`

### Option 2: Quick Fix (Temporary)

If you don't want to modify system settings, you can manually specify the AutoHotkey path in the script.

Edit `color_capture_core.py` and update the ColorCapture initialization:

```python
# Hard-code the AutoHotkey path if not in PATH
cc = ColorCapture(
    COLOR_REF_PATH,
    CAPTURES_DIR,
    # ... other parameters ...
    ahk_script_path="click_helper.ahk",
)

# Then manually set the exe path before clicking:
cc.ahk_exe_path = r"C:\Program Files\AutoHotkey\AutoHotkey.exe"
```

### Option 3: Find Your AutoHotkey Installation

If installed in a non-standard location, find it:

**PowerShell:**
```powershell
Get-ChildItem -Path "C:\" -Name "AutoHotkey.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
```

Or manually check:
- `C:\Program Files\AutoHotkey\`
- `C:\Program Files (x86)\AutoHotkey\`
- User's AppData: `C:\Users\[YourUsername]\AppData\Local\Programs\AutoHotkey\`

## How to Verify the Fix Works

1. **Test AutoHotkey directly:**
   ```powershell
   AutoHotkey.exe --version
   ```
   Should show version number if PATH is correct

2. **Run the script:**
   ```powershell
   python color_capture.py
   ```
   Should show:
   ```
   AutoHotkey: FOUND at C:\Program Files\AutoHotkey\AutoHotkey.exe
   ```
   Instead of:
   ```
   AutoHotkey: NOT FOUND (will use PyAutoGUI fallback)
   ```

## Alternative: Update color_capture.py

If you want to specify the path directly without modifying PATH, edit `color_capture.py`:

```python
# Option A: Specify full path if not in PATH
if USE_AUTOHOTKEY:
    ahk_exe = find_autohotkey_exe()
    if not ahk_exe:
        # Try your known installation path
        ahk_exe = r"C:\Program Files\AutoHotkey\AutoHotkey.exe"
    print(f"AutoHotkey: {'FOUND at ' + ahk_exe if ahk_exe else 'NOT FOUND'}")
```

## Understanding the Issue

Windows searches for executables in folders listed in the `PATH` environment variable. When AutoHotkey is installed, it may not automatically add itself to PATH. You need to do this manually.

**Why it matters:**
- With PATH: Script can find `AutoHotkey.exe` automatically
- Without PATH: Script can't find `AutoHotkey.exe` and falls back to PyAutoGUI
- PyAutoGUI works but is slower in VMs

## After Fixing PATH

Once AutoHotkey is in PATH and script detects it, you'll see:
- ✅ AutoHotkey detection message at startup
- ✅ Faster clicks in VMs (5-10x faster than PyAutoGUI)
- ✅ More reliable clicking on buttons
- ✅ Better compatibility with event-driven applications

## Troubleshooting

**Still not found after adding to PATH?**
1. Did you restart your terminal/IDE? (Required for changes to take effect)
2. Is AutoHotkey actually installed? Check manually:
   - Open File Explorer
   - Go to `C:\Program Files\AutoHotkey\`
   - Look for `AutoHotkey.exe`

**Script runs but shows "NOT FOUND"?**
1. Add full path to `color_capture.py` temporarily to debug
2. Open PowerShell and test: `AutoHotkey.exe --version`
3. If that fails, AutoHotkey isn't in your PATH

**Want to use PyAutoGUI instead?**
```python
# In color_capture.py
USE_AUTOHOTKEY = False  # Disable AutoHotkey, use PyAutoGUI
```

## Need More Help?

- AutoHotkey Official: https://www.autohotkey.com/
- PATH Environment Variable Guide: https://www.windows-commandline.com/set-path-environment-variable/
- PowerShell PATH: https://learn.microsoft.com/powershell/
