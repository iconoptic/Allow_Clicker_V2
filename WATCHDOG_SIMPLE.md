# Watchdog - Simple Windows Batch Version

A **pure Windows batch script** that monitors `color_capture.py` and automatically restarts it if it crashes or is killed.

**No Python, No PowerShell, No Task Scheduler configuration needed.**

## Quick Start (30 seconds)

```powershell
# Just run it
.\watchdog.bat
```

That's it. The watchdog starts and monitors color_capture.py in a separate window.

## What It Does

- **Monitors** `color_capture.py` every 2 seconds
- **Detects** if the process crashes or is killed
- **Restarts** automatically with a 2-second delay
- **Logs** everything to `watchdog.log`
- **Continues** indefinitely until you press Ctrl+C

## Usage

### Basic (Default Settings)
```powershell
.\watchdog.bat
```

### Custom Restart Delay
```powershell
.\watchdog.bat --restart-delay 5
```
Wait 5 seconds before restarting instead of 2.

### Max Restart Limit
```powershell
.\watchdog.bat --max-restarts 20
```
Stop the watchdog after 20 failed restarts (safety for catastrophic failures).

### Custom Check Interval
```powershell
.\watchdog.bat --check-interval 3
```
Check if process is running every 3 seconds instead of 2.

### Combined Options
```powershell
.\watchdog.bat --restart-delay 3 --check-interval 2 --max-restarts 15
```

### Get Help
```powershell
.\watchdog.bat --help
```

## How It Works

```
┌─ Watchdog.bat (runs in a window)
│
├─ Starts color_capture.py (in its own window)
│
├─ Loop every 2 seconds:
│  ├─ Is color_capture.py running?
│  ├─ YES → Continue monitoring
│  └─ NO → Wait 2 seconds → Restart it
│
└─ Logs to watchdog.log
```

## Example Output

```
[2025-11-11 10:30:45] ========================================================================
[2025-11-11 10:30:45] COLOR CAPTURE WATCHDOG - WINDOWS BATCH VERSION
[2025-11-11 10:30:45] ========================================================================
[2025-11-11 10:30:45] Script directory: C:\...\Allow_Clicker_v2
[2025-11-11 10:30:45] Python script: C:\...\Allow_Clicker_v2\color_capture.py
[2025-11-11 10:30:45] Virtual environment: C:\...\Allow_Clicker_v2\.venv
[2025-11-11 10:30:45] Restart delay: 2s
[2025-11-11 10:30:45] Check interval: 2s
[2025-11-11 10:30:45] Max restart attempts: Unlimited
[2025-11-11 10:30:45] Log file: C:\...\Allow_Clicker_v2\watchdog.log
[2025-11-11 10:30:45] 
[2025-11-11 10:30:45] Watchdog is ready. Starting color_capture.py...
[2025-11-11 10:30:45] Press Ctrl+C in this window to stop.
[2025-11-11 10:30:45] 
[2025-11-11 10:30:45] Starting color_capture.py (restart attempt 1)
[2025-11-11 10:30:46] Process started successfully
[2025-11-11 10:31:15] Process is running and healthy
[2025-11-11 10:31:45] Process is running and healthy

[User kills color_capture.py window]

[2025-11-11 10:32:20] 
[2025-11-11 10:32:20] WARNING: color_capture.py is not running!
[2025-11-11 10:32:20] 
[2025-11-11 10:32:20] Waiting 2 seconds before restart...
[2025-11-11 10:32:22] Starting color_capture.py (restart attempt 2)
[2025-11-11 10:32:23] Process started successfully
```

## Monitoring the Watchdog

### View Logs in Real-Time
```powershell
Get-Content watchdog.log -Wait
```

### View Last 20 Log Lines
```powershell
Get-Content watchdog.log -Tail 20
```

### Find Restart Events
```powershell
Select-String "restart attempt" watchdog.log
```

### Count How Many Times It Restarted
```powershell
(Select-String "Starting color_capture.py" watchdog.log).Count
```

## Requirements

- Windows (XP or newer)
- Python installed and accessible from command line
- Virtual environment at `.venv/` in the script directory
- That's it!

## Troubleshooting

### "color_capture.py not found"
Make sure you run watchdog.bat from the `Allow_Clicker_v2` directory:
```powershell
cd Allow_Clicker_v2
.\watchdog.bat
```

### "Virtual environment not found"
Create it with:
```powershell
python -m venv .venv
```

### Process keeps restarting immediately
Your `color_capture.py` is crashing. Check:
1. Is the virtual environment activated?
2. Are all dependencies installed? (`pip install -r requirements.txt`)
3. Run `color_capture.py` manually to see the error:
   ```powershell
   .venv\Scripts\activate.bat
   python color_capture.py
   ```

### Want to stop the watchdog
Press **Ctrl+C** in the watchdog window. It will cleanly shut down.

## Features

✅ **Pure Windows** - No dependencies, no setup  
✅ **Automatic Restart** - Detects crashes, restarts in 2-3 seconds  
✅ **Detailed Logging** - Everything logged with timestamps  
✅ **Configurable** - Adjust restart delay, check interval, max attempts  
✅ **Independent** - color_capture.py runs in its own window  
✅ **Simple** - Just run `.\watchdog.bat` and you're done  

## What If All Python Processes Get Killed?

The watchdog itself is a batch script, so it continues running. When the system allows Python to run again, the watchdog will immediately restart color_capture.py.

If you want the watchdog itself to auto-restart if Windows kills it, consider running it as a Windows Task Scheduler task (see README.md for details).

## Advanced: Batch Watchdog with Task Scheduler

To make the watchdog itself restart if killed:

1. Open Task Scheduler: `taskschd.msc`
2. Create Basic Task:
   - **Name**: Color Capture Watchdog
   - **Trigger**: At system startup, delay 1 minute
   - **Action**: Start program
     - Program: `cmd.exe`
     - Arguments: `/c "cd C:\path\to\Allow_Clicker_v2 && watchdog.bat"`
   - **Conditions**: Run whether user is logged in or not

Now the watchdog itself is protected and will restart on boot!

## Examples

### Development (Testing)
```powershell
.\watchdog.bat --restart-delay 1 --check-interval 1
```
Fast iteration, restart after 1 second.

### Production (Reliability)
```powershell
.\watchdog.bat --max-restarts 50
```
Run indefinitely but stop if it restarts more than 50 times (sign of deeper problem).

### Conservative (Safety)
```powershell
.\watchdog.bat --restart-delay 5 --max-restarts 10
```
Wait 5 seconds before restart, give up after 10 attempts.

## Summary

The batch watchdog is the **simplest, most reliable watchdog** you can run on Windows:

- ✅ No dependencies
- ✅ No configuration needed
- ✅ Just run `.\watchdog.bat`
- ✅ color_capture.py restarts automatically if it crashes
- ✅ Logs everything for debugging
- ✅ Works forever until you press Ctrl+C

That's it. Your color capture automation is now protected! 🛡️
