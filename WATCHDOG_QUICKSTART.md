# Watchdog Quick Start Guide

## What is the Watchdog?

The watchdog is a process monitor that automatically restarts `color_capture.py` if it crashes or is killed. Perfect for keeping your automation running 24/7 with zero downtime.

## Files Created

- **`watchdog.py`** - Main watchdog script (monitors and restarts color_capture.py)
- **`watchdog_launcher.bat`** - Windows batch launcher (easy startup)
- **`WATCHDOG_README.md`** - Complete documentation
- **`test_watchdog.py`** - Test script to verify functionality
- **`requirements.txt`** - Updated with psutil dependency

## Installation (1 minute)

```powershell
# 1. Install the psutil dependency
pip install psutil

# 2. You're done! That's it.
```

## Start the Watchdog (2 ways)

### Easy Way: Click the Batch File
```powershell
.\watchdog_launcher.bat
```
A window opens and the watchdog starts monitoring.

### Command Line Way
```powershell
python watchdog.py
```

## What Happens?

1. **Watchdog starts** and launches `color_capture.py`
2. **Every 2 seconds** it checks if color_capture.py is still running
3. **If it crashes** → Waits 2 seconds → Restarts it automatically
4. **You get logs** in `watchdog.log` with timestamps and status

## Example Output

```
[2025-11-11 10:30:45] COLOR CAPTURE WATCHDOG STARTED
[2025-11-11 10:30:45] Starting color_capture.py (attempt 1)
[2025-11-11 10:30:45] Process started successfully (PID: 12345)
[CAPTURE] Reference color (RGB): [  0 120 212]
[CAPTURE] Starting background capture loop...
[2025-11-11 10:31:15] Process alive - PID: 12345, Memory: 45.2MB, CPU: 2.3%
```

## Stop the Watchdog

Press **Ctrl+C** in the watchdog window.

## Configuration

### Faster Restart (1 second instead of 2)
```powershell
python watchdog.py --restart-delay 1
```

### Max 20 Restarts Before Giving Up
```powershell
python watchdog.py --max-restarts 20
```

### Check Status Every 3 Seconds
```powershell
python watchdog.py --check-interval 3
```

## Run as Background Service (Windows Task Scheduler)

Want the watchdog to start automatically when Windows boots, even if you're not logged in?

1. **Open Task Scheduler**: `taskschd.msc`
2. **Create Basic Task**: 
   - Name: `Color Capture Watchdog`
   - Trigger: `At system startup`, delay 1 minute
   - Action: `Start a program` → `powershell.exe`
   - Arguments: `-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -Command "cd '$(pwd)'; python watchdog.py"`
3. **Enable**: Run whether user is logged in or not

Now it runs automatically on every startup!

## Verify It Works

```powershell
# Start the watchdog
python watchdog.py

# In another PowerShell window, find and kill color_capture.py
Get-Process | Where-Object {$_.ProcessName -like "*python*"} | Select-Object Id, ProcessName
taskkill /PID <the_pid> /F

# Watch the watchdog restart it within 3 seconds!
```

Check `watchdog.log` to confirm:
```powershell
Get-Content watchdog.log -Tail 10
```

## Common Issues

**"psutil not found"**
```powershell
pip install psutil
```

**"color_capture.py crashes on startup"**
1. Test it manually: `python color_capture.py`
2. Check the error in watchdog.log
3. Fix the issue in color_capture.py
4. Restart watchdog

**Process keeps restarting (infinite loop)**
```powershell
# Set max restart limit
python watchdog.py --max-restarts 5
```

## Full Configuration Options

```powershell
python watchdog.py --help
```

Shows all available options with defaults.

## Key Features

✅ Automatic restart on crash  
✅ Detailed logging with timestamps  
✅ Health monitoring (CPU/Memory)  
✅ Configurable restart behavior  
✅ Graceful shutdown (Ctrl+C)  
✅ Task Scheduler integration  
✅ Zero impact on color_capture.py  

## Next Steps

- **Run it now**: `.\watchdog_launcher.bat`
- **Read full docs**: See `WATCHDOG_README.md`
- **Set up Task Scheduler**: Follow WATCHDOG_README.md advanced section
- **Monitor logs**: `Get-Content watchdog.log -Wait`

---

Your color capture automation is now protected from unexpected crashes! 🛡️
