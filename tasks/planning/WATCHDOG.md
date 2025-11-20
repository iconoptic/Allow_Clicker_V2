# Watchdog - Process Monitor and Auto-Restart

## Overview

The watchdog is a PowerShell-based monitoring system that continuously watches the `color_capture.py` Python process. If the process dies or is killed, the watchdog automatically restarts it, ensuring the script runs 24/7 without manual intervention.

## Features

- **Continuous Monitoring**: Checks every 2 seconds (configurable) if the Python process is running
- **Auto-Restart**: Automatically restarts the Python script if it dies
- **Detailed Logging**: Timestamped logs of all events (start, restart, errors)
- **Execution Policy Bypass**: Uses batch launcher to avoid PowerShell execution policy restrictions
- **Process Management**: Kills any existing instances before starting fresh
- **Error Handling**: Graceful handling of process start/stop failures

## Installation

### 1. No Additional Software Required

The watchdog requires only what you already have:

- Windows PowerShell (built-in to Windows)
- Python 3 with the color_capture.py script

### 2. Verify Python is in PATH

Before using the watchdog, ensure `python.exe` is accessible from the command line:

```powershell
python --version
```

If this fails, add Python to your system PATH environment variable.

## Usage

### Quick Start (Recommended)

Run the batch launcher from a Command Prompt or PowerShell:

```cmd
run_watchdog.bat
```

This bypasses PowerShell execution policy and starts the watchdog.

### Alternative: Direct PowerShell

If you have PowerShell execution policy set to allow scripts:

```powershell
powershell -ExecutionPolicy Bypass -File run_watchdog.ps1
```

Or with custom parameters:

```powershell
powershell -ExecutionPolicy Bypass -File run_watchdog.ps1 `
    -ScriptPath "color_capture.py" `
    -CheckInterval 2 `
    -RestartDelay 1 `
    -LogFile "watchdog.log"
```

## Configuration

### Parameters

Edit `run_watchdog.bat` or pass parameters to the PowerShell script:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `ScriptPath` | `color_capture.py` | Path to the Python script to monitor |
| `CheckInterval` | `2` | Seconds between process checks |
| `RestartDelay` | `1` | Seconds to wait before restarting after crash |
| `LogFile` | `watchdog.log` | Path to the log file |

### Example: Faster Restart

Edit `run_watchdog.bat`:

```batch
powershell.exe -ExecutionPolicy Bypass -NoProfile ^
    -File "run_watchdog.ps1" ^
    -ScriptPath "color_capture.py" ^
    -CheckInterval 1 ^
    -RestartDelay 0 ^
    -LogFile "watchdog.log"
```

This checks every 1 second and restarts immediately.

## Log File

The watchdog creates a `watchdog.log` file with timestamped entries:

```text
[2025-11-11 14:30:45] ==========================================
[2025-11-11 14:30:45] Watchdog started for: C:\...\color_capture.py
[2025-11-11 14:30:45] Check interval: 2s, Restart delay: 1s
[2025-11-11 14:30:45] Log file: C:\...\watchdog.log
[2025-11-11 14:30:45] ==========================================
[2025-11-11 14:30:45] Starting Python process: C:\...\color_capture.py
[2025-11-11 14:30:46] Python process started successfully (PID: 12345)
[2025-11-11 14:30:46] INFO: Python process (PID: 12345) is running
[2025-11-11 14:30:52] WARNING: Python process (PID: 12345) is not running! Restart #1
[2025-11-11 14:30:53] Killing existing Python process (PID: 12345)
[2025-11-11 14:30:54] Starting Python process: C:\...\color_capture.py
[2025-11-11 14:30:54] Python process started successfully (PID: 12346)
```

To monitor the log in real-time:

```powershell
Get-Content watchdog.log -Wait
```

Or on Windows 10/11 with `tail` equivalent:

```powershell
powershell -Command "Get-Content watchdog.log -Tail 10 -Wait"
```

## Running as a Service (Advanced)

### Windows Task Scheduler

To run the watchdog at system startup:

1. **Open Task Scheduler**: Press `Win+R`, type `taskschd.msc`, press Enter
2. **Create New Task**: Right-click "Task Scheduler Library" → "Create Task"
3. **General Tab**:
   - Name: `Allow Clicker Watchdog`
   - Check: "Run with highest privileges"
   - Check: "Run whether user is logged in or not"
4. **Triggers Tab**: Click "New..."
   - Begin task: "At startup"
   - Click "OK"
5. **Actions Tab**: Click "New..."
   - Action: "Start a program"
   - Program: `C:\Windows\System32\cmd.exe`
   - Arguments: `/c "C:\path\to\run_watchdog.bat"`
   - Start in: `C:\path\to\Allow_Clicker_v2`
   - Click "OK"
6. **Conditions Tab**:
   - Uncheck "Start the task only if the computer is on AC power"
7. **Settings Tab**:
   - Check: "Allow task to be queued"
   - Check: "If the task is already running, then the following rule applies: Stop the existing instance"

### Alternative: Create a Shortcut

Create a shortcut to `run_watchdog.bat`:

1. Right-click desktop → "New" → "Shortcut"
2. Location: `C:\Windows\System32\cmd.exe /c "C:\path\to\run_watchdog.bat"`
3. Name: `Allow Clicker Watchdog`
4. Right-click shortcut → "Properties" → "Advanced" → Check "Run as administrator"
5. Double-click to start

## Stopping the Watchdog

### From PowerShell

Press `Ctrl+C` in the watchdog window.

### Kill the Process

```powershell
# Find the watchdog process
Get-Process powershell | Where-Object { $_.CommandLine -like "*run_watchdog*" }

# Kill it
Stop-Process -Name powershell -Force
```

### From Task Scheduler

Right-click the task → "Disable"

## Troubleshooting

### "Python script not found" Error

**Problem**: Watchdog can't locate `color_capture.py`

**Solution**: Ensure the script is in the same directory as `run_watchdog.bat`, or update the path in the batch file.

### "Failed to start Python process" Error

**Problem**: Python script starts but exits immediately

**Check**:

1. Run the script manually: `python color_capture.py`
2. Check for errors in the output
3. Verify all dependencies are installed: `pip install -r requirements.txt`
4. Check the `watchdog.log` for specific error messages

### Watchdog uses too much CPU

**Problem**: Constant restarts in a loop

**Check the log file** to see why Python exits immediately. Common causes:

- Missing dependencies (Tesseract, OpenCV, etc.)
- Invalid configuration in `color_capture.py`
- Permission issues with output directories

### Python.exe not found

**Problem**: "python.exe not found" or similar error

**Solution**:
1. Verify Python is installed: `python --version` in Command Prompt
2. If not found, reinstall Python and check "Add Python to PATH"
3. Or modify the batch file to use full path: `C:\Python311\python.exe` (adjust version number)

## Architecture

### How It Works

```
run_watchdog.bat
    ↓ (Bypasses execution policy)
run_watchdog.ps1 (PowerShell script)
    ↓ (Monitors process)
color_capture.py (Python application)
```

### Process Flow

1. Batch file launches PowerShell with execution policy bypass
2. PowerShell script starts the Python process
3. Watchdog enters infinite loop:
   - Sleep for `CheckInterval` seconds
   - Check if Python process is running
   - If not running: wait `RestartDelay` seconds, then restart
   - Log all events to `watchdog.log`

## Best Practices

1. **Run as Administrator**: Ensures process killing/starting works reliably
2. **Monitor the Log**: Regularly check `watchdog.log` for crash patterns
3. **Test Manually First**: Run `color_capture.py` directly to ensure it works
4. **Use Task Scheduler**: For production deployments, run at system startup
5. **Archive Logs**: Keep backups of `watchdog.log` for troubleshooting

## Files

| File | Purpose |
|------|---------|
| `run_watchdog.bat` | Batch launcher (use this to start) |
| `run_watchdog.ps1` | PowerShell watchdog script (called by batch) |
| `WATCHDOG.md` | This documentation |
| `watchdog.log` | Runtime log file (auto-created) |

## Support

### Common Questions

**Q: Can I run multiple instances of the watchdog?**  
A: Not recommended. Each watchdog will try to manage the same Python process, causing conflicts.

**Q: Does the watchdog consume a lot of resources?**  
A: No. It sleeps 99% of the time, only waking to check if the process is running.

**Q: What if the Python script is supposed to exit?**  
A: The watchdog will immediately restart it. If you want the script to stay off, stop the watchdog itself.

**Q: Can I use this with other Python scripts?**  
A: Yes. Modify `run_watchdog.bat` and change the `ScriptPath` parameter to point to a different script.

## License & Attribution

This watchdog script is provided as part of the Allow Clicker V2 project and uses standard Windows PowerShell.
