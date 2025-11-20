@echo off
REM Run color_capture.py in the background without a visible console window

setlocal enabledelayedexpansion

REM Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0

REM Change to script directory
cd /d "%SCRIPT_DIR%"

REM Run the Python script with no visible window
if exist "color_capture.py" (
    start "" /b pythonw.exe color_capture.py
    echo Color capture script started in background
) else (
    echo Error: color_capture.py not found in %SCRIPT_DIR%
    pause
)
