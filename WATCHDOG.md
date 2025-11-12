# Watchdog Documentation

## Overview

The watchdog is a process monitor that keeps `color_capture.py` running continuously. If the process crashes, is killed, or exits unexpectedly, the watchdog will automatically restart it.

This is useful for production deployments where you need the color capture script to run unattended for long periods.

## Features

- **Automatic Restart**: Restarts the process if it crashes or is killed
- **Health Checks**: Periodic checks to ensure the process is still running
- **Exponential Backoff**: Gradually increases delay between restart attempts (prevents rapid restart loops)
- **Max Attempt Limit**: Gives up after a configurable number of restart failures
- **Graceful Shutdown**: Cleanly terminates the monitored process on user interrupt (Ctrl+C)
- **Detailed Logging**: Timestamped logs show all events and status
- **Configurable**: Command-line options to customize behavior

## Usage

### Method 1: Using Batch File (Recommended for Windows)

```bash
.\run_watchdog.bat
```

This is the simplest way to run the watchdog. Double-click the batch file or run it from Command Prompt.

### Method 2: Using PowerShell

```powershell
.\run_watchdog.ps1
```

Or with arguments:

```powershell
.\run_watchdog.ps1 -interval 10 -max-attempts 20
```

### Method 3: Direct Python Execution

```bash
python watchdog.py
```

### Command-Line Options

Customize the watchdog behavior with these options:

```bash
python watchdog.py --script color_capture.py  # Script to monitor (default: color_capture.py)
python watchdog.py --interval 10              # Check interval in seconds (default: 5)
python watchdog.py --max-attempts 20          # Max restart attempts (default: 10)
```

#### Examples

```bash
# Monitor with 10-second check interval
python watchdog.py --interval 10

# Monitor with up to 20 restart attempts before giving up
python watchdog.py --max-attempts 20

# Monitor a different script
python watchdog.py --script my_capture_script.py

# Combine options
python watchdog.py --interval 3 --max-attempts 30 --script color_capture.py
```

## How It Works

### Start Phase
1. Watchdog validates that `color_capture.py` exists
2. Starts the first process
3. Enters monitoring loop

### Monitoring Loop
1. Checks every `--interval` seconds (default: 5) if the process is running
2. If running, continues checking
3. If not running:
   - Logs the unexpected death
   - Captures any output/errors from the process
   - Increments failure counter
   - Waits with exponential backoff (1s, 2s, 4s, 8s, 16s, 30s max)
   - Attempts to restart

### Restart Strategy
- **Attempt 1**: Restart immediately
- **Attempt 2**: Wait 2 seconds, then restart
- **Attempt 3**: Wait 4 seconds, then restart
- **Attempt 4**: Wait 8 seconds, then restart
- **Attempt 5+**: Wait up to 30 seconds, then restart
- **Attempt 11+**: Give up (configurable with `--max-attempts`)

### Shutdown Phase
When you press Ctrl+C:
1. Watchdog receives interrupt signal
2. Logs shutdown notice
3. Gracefully terminates the monitored process
4. Exits with status 0 (success)

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Successful execution or clean shutdown |
| 1 | Fatal error (e.g., script not found, max restarts exceeded) |

## Output Example

```
======================================================================
WATCHDOG: Monitoring color_capture.py
Press Ctrl+C to stop the watchdog and terminate the process
======================================================================

[WATCHDOG] Initialized
[WATCHDOG] Monitoring: color_capture.py
[WATCHDOG] Check interval: 5s
[WATCHDOG] Max restart attempts: 10

[2025-11-11 16:23:45] [INFO] Starting color_capture.py...
[2025-11-11 16:23:45] [INFO] Process started with PID 12345 (Restart #1)

[2025-11-11 16:24:15] [WARNING] Process is not running!
[2025-11-11 16:24:15] [WARNING] Process died with exit code 1
[2025-11-11 16:24:15] [INFO] Waiting 2s before restart...
[2025-11-11 16:24:17] [INFO] Starting color_capture.py...
[2025-11-11 16:24:17] [INFO] Process started with PID 12346 (Restart #2)
```

## Advanced Usage

### Running in Background (Windows)

Create a shortcut to `run_watchdog.bat` and set it to:
- Target: `C:\path\to\run_watchdog.bat`
- Start in: `C:\path\to\Allow_Clicker_v2`
- Run: `Minimized`

### Windows Task Scheduler

You can also schedule the watchdog to start automatically:

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: "At startup"
4. Set action: Start a program
5. Program: `C:\path\to\.venv\Scripts\python.exe`
6. Arguments: `watchdog.py`
7. Start in: `C:\path\to\Allow_Clicker_v2`

### Monitoring Multiple Scripts

Run separate watchdog instances for different scripts:

```bash
python watchdog.py --script color_capture.py --interval 5
python watchdog.py --script other_script.py --interval 5
```

Each watchdog will manage its own process independently.

## Troubleshooting

### "Script not found" Error

**Problem**: Watchdog exits with "Script not found" error

**Solution**: Ensure `color_capture.py` is in the same directory as `watchdog.py`

### Process keeps restarting

**Possible causes**:
1. `color_capture.py` has a fatal error (check output)
2. Dependencies are missing (check virtual environment)
3. Configuration file is invalid

**Solution**: 
- Run `python color_capture.py` manually to see errors
- Check virtual environment: `.venv\Scripts\activate`
- Review debug output from watchdog logs

### Watchdog uses too much CPU

**Problem**: Watchdog consuming high CPU percentage

**Solution**: Increase `--interval` value

```bash
python watchdog.py --interval 30  # Check every 30 seconds instead of 5
```

### Want to see detailed output

**Problem**: Want to capture watchdog logs to a file

**Solution**: Redirect output to file

```bash
python watchdog.py >> watchdog_log.txt 2>&1
```

## Performance Impact

- **CPU**: Minimal - only checks process status every 5 seconds (configurable)
- **Memory**: ~10-20 MB for watchdog process + monitored process memory
- **Disk I/O**: None (except when restarting)

## Security Notes

- Watchdog runs with same permissions as the user who started it
- No special privileges required
- Process output is printed to console (may contain sensitive data)

## Stopping the Watchdog

### Method 1: Keyboard (Recommended)
Press `Ctrl+C` in the watchdog console window. This will:
- Stop the watchdog
- Gracefully terminate the monitored process
- Exit cleanly

### Method 2: Task Manager
Select the Python process and click "End Task". This will:
- Abruptly terminate both watchdog and monitored process
- May leave processes in inconsistent state

### Method 3: Command Line (PowerShell/CMD)
```bash
# Find the process ID
tasklist | find "python.exe"

# Kill the watchdog process
taskkill /pid 12345 /t /f
```

## Integration with Production Setups

### With Windows Service

To run as a Windows Service, use tools like:
- **NSSM** (Non-Sucking Service Manager)
- **pywin32** service wrapper
- **WinSW** (Windows Service Wrapper)

Example with NSSM:
```bash
nssm install AllowClickerWatchdog C:\path\to\.venv\Scripts\python.exe watchdog.py
nssm start AllowClickerWatchdog
```

### With Docker

```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "watchdog.py", "--interval", "10"]
```

## Development Notes

The watchdog is implemented as a single Python file (`watchdog.py`) with the `ProcessWatchdog` class.

### Key Methods

- `start_process()`: Starts the monitored process
- `check_process()`: Returns True if process is running
- `handle_process_death()`: Called when process unexpectedly exits
- `run()`: Main watchdog loop

### Extending the Watchdog

To customize behavior, you can:

1. Modify command-line arguments in `main()`
2. Adjust exponential backoff logic in `run()`
3. Add custom logging in `log()` method
4. Implement health checks beyond just "is it running"

## License

Same as Allow_Clicker_V2 project
