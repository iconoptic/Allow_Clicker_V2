@echo off
REM Batch launcher for PowerShell watchdog - Bypasses execution policy
REM This runs the PowerShell script with proper arguments

setlocal enabledelayedexpansion

REM Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0

REM Change to script directory
cd /d "%SCRIPT_DIR%"

REM Run the PowerShell script with execution policy bypass
REM Arguments: ScriptPath, CheckInterval, RestartDelay, LogFile
powershell.exe -ExecutionPolicy Bypass -NoProfile ^
    -File "%SCRIPT_DIR%run_watchdog.ps1" ^
    -ScriptPath "color_capture.py" ^
    -CheckInterval 2 ^
    -RestartDelay 1 ^
    -LogFile "watchdog.log"

REM Exit with the same exit code as PowerShell
exit /b %ERRORLEVEL%
