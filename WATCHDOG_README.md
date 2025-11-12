# Color Capture Watchdog - Process Monitor and Auto-Restart

A robust watchdog script that monitors the `color_capture.py` process and automatically restarts it if it's killed or crashes. Ideal for keeping the color capture automation running 24/7 even if something terminates the main process.

## Features

- **Automatic Restart**: Detects when `color_capture.py` crashes or is killed
- **Configurable Delay**: Wait time before restarting (default: 2 seconds)
- **Health Monitoring**: Periodic status logging with CPU/memory usage
- **Full Logging**: Timestamped activity log to `watchdog.log`
- **Graceful Shutdown**: Cleanly terminates process on Ctrl+C
- **Max Restart Limit**: Optional safety limit on restart attempts
- **Cross-Platform**: Works on Windows, Linux, and macOS

## Installation

### 1. Install Required Dependencies

```powershell
pip install psutil
```

Or update your requirements.txt:

```powershell
pip install -r requirements.txt
```

The watchdog uses `psutil` for detailed process monitoring.

### 2. Verify Setup

Ensure these files exist in your Allow_Clicker_v2 directory:
- ✓ `color_capture.py` (main script)
- ✓ `color_capture_core.py` (core module)
- ✓ `watchdog.py` (watchdog script)
- ✓ `watchdog_launcher.bat` (Windows launcher)
- ✓ `.venv/` (virtual environment)

## Quick Start

### Option 1: Simple Batch Launcher (Recommended for Windows)

```powershell
.\watchdog_launcher.bat
```

This opens the watchdog in a new window. Press `Ctrl+C` to stop.

### Option 2: Direct PowerShell/Command Prompt

```powershell
python watchdog.py
```

### Option 3: With Custom Arguments

```powershell
python watchdog.py --restart-delay 3 --check-interval 2 --max-restarts 20
```

## Configuration Options

### Command-Line Arguments

```
--script-dir DIR              Directory with color_capture.py (default: script directory)
--restart-delay SECONDS       Wait time before restart (default: 2)
--check-interval SECONDS      Time between process checks (default: 2)
--max-restarts COUNT          Max restart attempts, 0=unlimited (default: 0)
--log-file PATH              Log file path (default: watchdog.log in script dir)
```

### Examples

```powershell
# Run watchdog with 5-second restart delay, unlimited restarts
python watchdog.py --restart-delay 5

# Run watchdog with max 20 restarts before giving up
python watchdog.py --max-restarts 20

# Run watchdog with custom log file
python watchdog.py --log-file C:\logs\color_capture.log

# Run watchdog checking every 3 seconds
python watchdog.py --check-interval 3
```

## Log Output

The watchdog creates a `watchdog.log` file in the script directory with timestamped entries:

```
[2025-11-11 10:30:45] Watchdog initialized for: C:\...\color_capture.py
[2025-11-11 10:30:45] Restart delay: 2s, Check interval: 2s
[2025-11-11 10:30:45] ======================================================================
[2025-11-11 10:30:45] COLOR CAPTURE WATCHDOG STARTED
[2025-11-11 10:30:45] ======================================================================
[2025-11-11 10:30:45] Starting color_capture.py (attempt 1)
[2025-11-11 10:30:45] Process started successfully (PID: 12345)
[2025-11-11 10:31:15] Process alive - PID: 12345, Memory: 45.2MB, CPU: 2.3%
[2025-11-11 10:31:20] Process died (exit code: 1)
[2025-11-11 10:31:20] Waiting 2s before restart...
[2025-11-11 10:31:22] Starting color_capture.py (attempt 2)
[2025-11-11 10:31:22] Process started successfully (PID: 12356)
```

## Console Output

The watchdog prints to console while running:

```
[2025-11-11 10:30:45] COLOR CAPTURE WATCHDOG STARTED
[2025-11-11 10:30:45] Starting color_capture.py (attempt 1)
[2025-11-11 10:30:45] Process started successfully (PID: 12345)
[CAPTURE] Reference color (RGB): [  0 120 212]
[CAPTURE] Starting background capture loop (press Ctrl+C to stop)...
[CAPTURE] ============================================================
[CAPTURE] Iteration 1 | Time: 10:30:46
```

- Lines prefixed `[CAPTURE]` are from the color_capture.py output
- Lines prefixed `[timestamp]` are from the watchdog

## Windows Task Scheduler Integration

To run the watchdog as a true background service that persists across reboots:

### 1. Open Task Scheduler

```powershell
taskschd.msc
```

### 2. Create a New Task

- **Name**: `Color Capture Watchdog`
- **Description**: Monitors and restarts color_capture.py
- **Run with highest privileges**: ☑ (recommended for reliable monitoring)

### 3. Set Trigger

- **Begin the task**: `At system startup`
- **Delay task for**: `1 minute` (gives system time to settle)

### 4. Set Action

- **Action**: `Start a program`
- **Program/script**: `powershell.exe`
- **Arguments**: 
  ```
  -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File "C:\path\to\watchdog_launcher.bat"
  ```

### 5. Set Conditions

- ☑ Run whether user is logged in or not
- ☑ Run with highest privileges
- ☐ Stop if it runs longer than (or uncheck)

### 6. Click OK and Provide Credentials

Enter your Windows username and password.

## Troubleshooting

### "psutil module not found"

**Solution**: Install psutil
```powershell
pip install psutil
```

### "color_capture.py not found"

**Solution**: Ensure you're running watchdog.py from the correct directory
```powershell
cd C:\path\to\Allow_Clicker_v2
python watchdog.py
```

### Watchdog exits immediately

**Possible causes**:
1. color_capture.py crashes on startup
2. Virtual environment not properly activated
3. Missing dependencies in color_capture.py

**Solution**: Check the watchdog.log for error messages
```powershell
Get-Content watchdog.log -Tail 20
```

### Process keeps restarting

**Likely cause**: color_capture.py is crashing repeatedly

**Solution**:
1. Check watchdog.log for error patterns
2. Test color_capture.py manually: `python color_capture.py`
3. Verify all dependencies are installed
4. Set max restarts to prevent infinite loop:
   ```powershell
   python watchdog.py --max-restarts 5
   ```

### High CPU/Memory Usage

**Solution**: Increase check interval
```powershell
python watchdog.py --check-interval 5
```

## Architecture

### Process Flow

```
Watchdog (watchdog.py)
    ↓
Monitors color_capture.py
    ↓
On process death → Wait (restart_delay) → Restart color_capture.py
```

### Monitoring Interval

- Default: Checks every 2 seconds
- Configurable via `--check-interval`
- Status logged every 30 seconds (to reduce log spam)

## How It Works

1. **Startup**: Watchdog starts color_capture.py and logs the PID
2. **Monitoring Loop**: Every `--check-interval` seconds:
   - Checks if process is still alive
   - Logs memory and CPU usage every 30 seconds
   - Reads and displays any output from color_capture.py
3. **On Crash**: If process dies:
   - Logs exit code
   - Waits `--restart-delay` seconds
   - Restarts the process (unless max-restarts exceeded)
4. **Graceful Shutdown**: On Ctrl+C:
   - Terminates child process cleanly
   - Logs final statistics
   - Exits watchdog

## Advanced Usage

### Running Multiple Instances

You can run multiple watchdog instances monitoring different capture scripts:

```powershell
# Terminal 1: Monitor color_capture.py
python watchdog.py --log-file watchdog_main.log

# Terminal 2: Monitor another process
python some_other_script.py --log-file watchdog_other.log
```

### Programmatic Usage

```python
from watchdog import ColorCaptureWatchdog

# Create watchdog instance
watchdog = ColorCaptureWatchdog(
    script_dir="C:/path/to/script",
    restart_delay=2,
    max_restart_attempts=10,
    check_interval=2
)

# Run watchdog
watchdog.run()
```

## Performance Impact

- **CPU**: Negligible (~0.1-0.5% when idle)
- **Memory**: ~30-40MB (subprocess overhead)
- **Disk I/O**: Minimal (only logging)

## Limitations

- Monitors only the direct subprocess (color_capture.py)
- Does not monitor child processes spawned by color_capture.py
- Not a replacement for proper error handling in the main script
- Requires psutil for detailed process information

## Security Notes

- Watchdog runs with same privileges as the user launching it
- For Task Scheduler, running with "highest privileges" is recommended
- Log files contain timestamps but not sensitive data
- Process monitoring uses standard Windows APIs

## Support & Debugging

### Enable Verbose Logging

The watchdog automatically logs all events to `watchdog.log`. For detailed debugging:

```powershell
# View last 50 lines of log
Get-Content watchdog.log -Tail 50

# Follow log in real-time
Get-Content watchdog.log -Wait
```

### Manual Testing

```powershell
# Start watchdog
python watchdog.py

# In another terminal, kill the process
taskkill /PID <pid_from_log> /F

# Watch watchdog automatically restart it
# Check watchdog.log for confirmation
```

## License

Same as Allow_Clicker_v2

## Summary

The watchdog provides:
- ✓ Automatic restart on crash
- ✓ Detailed logging and monitoring
- ✓ Configurable restart behavior
- ✓ Task Scheduler integration for background operation
- ✓ Zero impact on color_capture.py functionality
- ✓ Production-ready reliability

Keep your color capture automation running continuously with confidence!
