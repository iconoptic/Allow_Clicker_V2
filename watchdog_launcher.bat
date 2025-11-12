@echo off
REM Watchdog Launcher for Color Capture Script
REM This batch file starts the watchdog in a separate window
REM The watchdog will monitor and automatically restart color_capture.py if it crashes

setlocal enabledelayedexpansion

REM Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0
set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%

REM Check if .venv exists
if not exist "%SCRIPT_DIR%\.venv" (
    echo Error: Virtual environment not found at %SCRIPT_DIR%\.venv
    echo Please run: python -m venv .venv
    pause
    exit /b 1
)

REM Check if watchdog.py exists
if not exist "%SCRIPT_DIR%\watchdog.py" (
    echo Error: watchdog.py not found at %SCRIPT_DIR%\watchdog.py
    pause
    exit /b 1
)

echo Starting Color Capture Watchdog...
echo Script directory: %SCRIPT_DIR%
echo.

REM Activate virtual environment and run watchdog
cd /d "%SCRIPT_DIR%"
call .venv\Scripts\activate.bat
python watchdog.py --restart-delay 2 --check-interval 2 --max-restarts 0

pause
