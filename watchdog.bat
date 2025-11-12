@echo off
REM ==============================================================================
REM Color Capture Watchdog - Windows Batch Script
REM Monitors and restarts color_capture.py if it crashes
REM Pure Windows - no Python, no PowerShell, no Task Scheduler needed
REM ==============================================================================

setlocal enabledelayedexpansion

REM Configuration - edit these values as needed
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=!SCRIPT_DIR:~0,-1!"
set "PYTHON_SCRIPT=%SCRIPT_DIR%\color_capture.py"
set "VENV_DIR=%SCRIPT_DIR%\.venv"
set "LOG_FILE=%SCRIPT_DIR%\watchdog.log"
set "RESTART_DELAY=2"
set "CHECK_INTERVAL=2"
set "MAX_RESTARTS=0"
set "RESTART_COUNT=0"
set "PROCESS_PID="

REM Parse command line arguments
:parse_args
if "%~1"=="" goto args_done
if "%~1"=="--restart-delay" (
    set "RESTART_DELAY=%~2"
    shift & shift
    goto parse_args
)
if "%~1"=="--check-interval" (
    set "CHECK_INTERVAL=%~2"
    shift & shift
    goto parse_args
)
if "%~1"=="--max-restarts" (
    set "MAX_RESTARTS=%~2"
    shift & shift
    goto parse_args
)
if "%~1"=="--help" (
    goto show_help
)
shift
goto parse_args

:args_done

REM ==============================================================================
REM Initialization and Validation
REM ==============================================================================

call :log "================================================================================"
call :log "COLOR CAPTURE WATCHDOG - WINDOWS BATCH VERSION"
call :log "================================================================================"

if not exist "%PYTHON_SCRIPT%" (
    call :log_error "ERROR: color_capture.py not found!"
    call :log_error "Expected location: %PYTHON_SCRIPT%"
    call :log_error ""
    call :log_error "Make sure you run this from the Allow_Clicker_v2 directory:"
    call :log_error "   cd Allow_Clicker_v2"
    call :log_error "   watchdog.bat"
    timeout /t 10 /nobreak
    exit /b 1
)

if not exist "%VENV_DIR%" (
    call :log_error "ERROR: Virtual environment not found at %VENV_DIR%"
    call :log_error "Create it with: python -m venv .venv"
    timeout /t 10 /nobreak
    exit /b 1
)

call :log "Script directory: %SCRIPT_DIR%"
call :log "Python script: %PYTHON_SCRIPT%"
call :log "Virtual environment: %VENV_DIR%"
call :log "Restart delay: %RESTART_DELAY%s"
call :log "Check interval: %CHECK_INTERVAL%s"

if %MAX_RESTARTS% gtr 0 (
    call :log "Max restart attempts: %MAX_RESTARTS%"
) else (
    call :log "Max restart attempts: Unlimited"
)

call :log "Log file: %LOG_FILE%"
call :log ""
call :log "Watchdog is ready. Starting color_capture.py..."
call :log "Press Ctrl+C in this window to stop."
call :log ""

REM Start initial process
call :start_process

REM ==============================================================================
REM Main Watchdog Loop
REM ==============================================================================

:main_loop

REM Check if the color_capture process is still running
REM We look for python.exe processes that have color_capture.py in their arguments
wmic process where "name='python.exe' and commandline like '%%color_capture.py%%'" get processid 2>nul | find /I "processid" >nul
set "PROCESS_RUNNING=!ERRORLEVEL!"

if %PROCESS_RUNNING% equ 0 (
    REM Process is running - continue monitoring
    REM Log status every ~30 seconds (15 iterations x 2 second check)
    set /a "LOG_COUNTER=!RESTART_COUNT! %% 15"
    if !LOG_COUNTER! equ 0 (
        call :log "Process is running and healthy"
    )
) else (
    REM Process died - need to restart
    call :log ""
    call :log "WARNING: color_capture.py is not running!"
    call :log ""
    
    REM Check if we've exceeded max restarts
    if %MAX_RESTARTS% gtr 0 (
        if !RESTART_COUNT! geq %MAX_RESTARTS% (
            call :log "ERROR: Max restart attempts (%MAX_RESTARTS%) exceeded!"
            call :log "Watchdog is stopping."
            call :log ""
            call :log "================================================================================"
            call :log "WATCHDOG STOPPED - Max restarts exceeded"
            call :log "================================================================================"
            timeout /t 10 /nobreak
            exit /b 1
        )
    )
    
    REM Wait before restarting
    call :log "Waiting %RESTART_DELAY% seconds before restart..."
    timeout /t %RESTART_DELAY% /nobreak >nul
    
    REM Increment counter and restart
    set /a RESTART_COUNT=!RESTART_COUNT!+1
    call :start_process
)

REM Wait before next check
timeout /t %CHECK_INTERVAL% /nobreak >nul
goto main_loop

REM ==============================================================================
REM Subroutines
REM ==============================================================================

:start_process
    set /a RESTART_COUNT=!RESTART_COUNT!+1
    call :log "Starting color_capture.py (restart attempt !RESTART_COUNT!)"
    
    REM Start Python in a minimized window
    cd /d "%SCRIPT_DIR%"
    start "Color Capture" /MIN "%VENV_DIR%\Scripts\python.exe" "%PYTHON_SCRIPT%"
    
    REM Give the process time to start
    timeout /t 3 /nobreak >nul
    
    REM Get the PID of the python process running color_capture.py
    for /f "tokens=*" %%A in ('wmic process where "name=^"python.exe^" and commandline like ^"%%color_capture.py%%^"" get processid 2^>nul ^| find /V "processid"') do (
        set "PROCESS_PID=%%A"
    )
    
    REM Trim whitespace from PID
    for /f "tokens=*" %%A in ('echo !PROCESS_PID!') do set "PROCESS_PID=%%A"
    
    if defined PROCESS_PID (
        call :log "Process started successfully (PID: !PROCESS_PID!)"
    ) else (
        call :log_error "Process failed to start - will retry next cycle"
    )
    goto :eof

:log
    setlocal enabledelayedexpansion
    for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set "mydate=%%c-%%a-%%b")
    for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set "mytime=%%a:%%b")
    set "timestamp=!mydate! !mytime!"
    
    echo [!timestamp!] %~1
    echo [!timestamp!] %~1 >> "%LOG_FILE%"
    endlocal
    goto :eof

:log_error
    setlocal enabledelayedexpansion
    for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set "mydate=%%c-%%a-%%b")
    for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set "mytime=%%a:%%b")
    set "timestamp=!mydate! !mytime!"
    
    echo [!timestamp!] ERROR: %~1
    echo [!timestamp!] ERROR: %~1 >> "%LOG_FILE%"
    endlocal
    goto :eof

:show_help
    cls
    echo.
    echo COLOR CAPTURE WATCHDOG - Windows Batch Version
    echo.
    echo Usage: watchdog.bat [options]
    echo.
    echo Options:
    echo   --restart-delay SECONDS     Seconds to wait before restarting (default: 2)
    echo   --check-interval SECONDS    Seconds between status checks (default: 2)
    echo   --max-restarts COUNT        Max restart attempts (default: 0 = unlimited)
    echo   --help                      Show this help message
    echo.
    echo Examples:
    echo   watchdog.bat
    echo   watchdog.bat --restart-delay 5
    echo   watchdog.bat --max-restarts 20
    echo   watchdog.bat --check-interval 3 --restart-delay 2 --max-restarts 10
    echo.
    echo Notes:
    echo   - Pure Windows batch - no Python or PowerShell required
    echo   - Logs to watchdog.log in the script directory
    echo   - Press Ctrl+C in this window to stop the watchdog
    echo   - color_capture.py runs in a separate window
    echo.
    pause
    exit /b 0
