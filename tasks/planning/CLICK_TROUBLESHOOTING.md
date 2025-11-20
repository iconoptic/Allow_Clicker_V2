# Auto-Click Troubleshooting Guide

## Problem: Clicks Not Working

If the script detects "Allow" rectangles and reports clicks but nothing happens, there are several potential causes and solutions.

## Diagnostic Steps

### 1. Verify Clicks Are Being Registered

The improved click functionality now includes:
- **Cursor movement tracking** - Script moves to the exact center of each rectangle
- **Movement delay** - `CLICK_DELAY` (default 0.2s) between move and click
- **Smooth movement** - Uses duration parameter for smooth cursor movement
- **Explicit button specification** - Specifies `button='left'` to avoid confusion
- **Detailed logging** - Shows each step: move, delay, click, restore

Check the debug output for these lines:
```
  Moving to (1938, 984)...
  Clicking at (1938, 984) with button='left'
  Click #1 completed
  Restoring cursor to: (1533, 670)
```

### 2. Check if Application is Responding

The problem might not be with the script but with the application:

1. **Test manually**: Click the exact same location with your mouse
2. **Check for modals**: Is there a dialog or popup blocking interaction?
3. **Check focus**: Make sure the application window is in focus
4. **Test with pyautogui directly**:

```python
import pyautogui
pyautogui.moveTo(1938, 984, duration=0.2)
time.sleep(0.2)
pyautogui.click(button='left')
```

### 3. Increase Click Delay

If the application is slow to respond, increase `CLICK_DELAY`:

```python
# In color_capture.py
CLICK_DELAY = 0.5  # Wait 500ms between move and click
```

Available settings:
- `CLICK_DELAY = 0.1` - Fast response applications
- `CLICK_DELAY = 0.2` - Standard (default)
- `CLICK_DELAY = 0.5` - Slow applications
- `CLICK_DELAY = 1.0` - Very slow applications

### 4. Verify Coordinates Are Correct

Check that the rectangles being detected are in the right location:

1. Enable `DEBUG_MODE = True` (default)
2. Look for lines like: `Rectangle [6] at (1903, 972) size 71x24:`
3. The calculated center should be close to the visible "Allow" button

Manual calculation:
```
Rectangle at (1903, 972) size 71x24:
Center X = 1903 + 71//2 = 1903 + 35 = 1938
Center Y = 972 + 24//2 = 972 + 12 = 984
Expected click: (1938, 984)
```

If the coordinates seem wrong:
- The color_ref.png might not match the actual button color
- Try increasing `COLOR_TOLERANCE` to detect larger areas
- Verify assets/color_ref.png is the correct reference color

### 5. Check for Multi-Monitor Issues

If you have multiple monitors, pyautogui might not click on the right one:

```python
# Add this to verify which monitor pyautogui sees
import pyautogui
size = pyautogui.size()
print(f"Screen size: {size}")
# If incorrect, try adjusting click coordinates
```

### 6. Test Click Without Cursor Restoration

Temporarily disable cursor restoration to test:

```python
# Modify color_capture_core.py click_captures() temporarily
# Comment out the finally block to keep cursor at click location
# This helps verify if the click itself is working
```

### 7. Check for Accessibility Issues

Some applications require specific permissions:

- **Windows**: Check if the application requires admin privileges
- **UAC**: Try running the script as Administrator
- **Accessibility**: Some apps block automated input (security feature)

## Advanced Solutions

### Solution 1: Add Pre-Click Activation

If the application window isn't focused:

```python
# Add to color_capture_core.py click_captures()
import pyautogui
import subprocess

# Bring window to focus first
# subprocess.Popen(['taskkill', '/IM', 'AppName.exe'])
# subprocess.Popen('AppName.exe')
# time.sleep(1)
```

### Solution 2: Use Double-Click Instead

```python
# Modify click_captures() to use doubleClick
pyautogui.doubleClick(center_x, center_y, button='left')
```

### Solution 3: Add Keyboard Alternative

If clicking doesn't work, try keyboard activation:

```python
# Add Tab/Enter approach
pyautogui.press('tab')  # Navigate to button
time.sleep(0.2)
pyautogui.press('enter')  # Activate button
```

### Solution 4: Disable AUTO_CLICK and Test Manually

```python
# In color_capture.py
AUTO_CLICK_ENABLED = False  # Disable auto-click

# Now captures will save images but won't click
# You can manually click and verify OCR detection works
```

## Configuration Options

```python
# In color_capture.py

# Timing adjustments
CLICK_DELAY = 0.2              # Increase if clicks not registering
POLL_INTERVAL = 1              # How often to check for rectangles

# Detection adjustments  
COLOR_TOLERANCE = 30           # Increase to detect more variations
OCR_SEARCH_TEXT = "Allow"      # Change to search for different text

# Disable features to test
AUTO_CLICK_ENABLED = True      # Set to False to disable clicking
OCR_ENABLED = True             # Set to False to save all rectangles
DEBUG_MODE = True              # Set to False for less output
```

## Testing Checklist

- [ ] Script detects rectangles with debug output
- [ ] OCR extracts text correctly ("Allow" is visible in output)
- [ ] Script reports successful saves to captures/
- [ ] Cursor position is saved and restored (check log output)
- [ ] Click coordinates look correct (near visible Allow button)
- [ ] Manual mouse click works at same coordinates
- [ ] Application is responsive and in focus
- [ ] No administrator/permission restrictions

## Example: Complete Test

```powershell
# 1. Run script with full debug output
python color_capture.py

# 2. Watch for "Allow | ~" text in OCR output
# 3. Look for "Clicking at (X, Y)" messages
# 4. Verify cursor moves and returns
# 5. Check if Allow button actually gets clicked

# If click doesn't work:
# 6. Try manually clicking at same (X, Y) coordinates
# 7. If manual click works, increase CLICK_DELAY
# 8. If manual click fails, check application focus/permissions
```

## Performance Considerations

**Click timing breakdown** (with default settings):
- Cursor move: ~100ms (0.1s duration)
- Movement delay: 200ms (CLICK_DELAY)
- Click execution: ~10ms
- Between-click delay: ~50ms
- **Total per rectangle**: ~360ms
- **Total per cycle**: 1000ms (1 second poll) + click time

## Still Not Working?

1. **Enable maximum debugging**:
   ```python
   DEBUG_MODE = True
   CLICK_DELAY = 1.0  # Very long delay
   ```

2. **Check system logs** for any pyautogui errors

3. **Test with different applications** to isolate the issue

4. **Try alternative clicking methods**:
   - `pyautogui.write()` - Send keyboard commands instead
   - `win32api` - Windows-specific API
   - `pynput` - Alternative input library

5. **Contact support** with:
   - Full debug output
   - Screenshots of rectangles detected
   - Application name and version
   - Windows version
   - Any error messages
