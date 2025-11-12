# Watchdog Script - Monitors and restarts color_capture.py if killed
# This script runs continuously and ensures the Python process is always running
# Usage: powershell -ExecutionPolicy Bypass -File run_watchdog.ps1

param(
    [string]$ScriptPath = "color_capture.py",
    [int]$CheckInterval = 2,  # Check every 2 seconds if process is alive
    [int]$RestartDelay = 1,   # Wait 1 second before restarting
    [string]$LogFile = "watchdog.log"
)

# Get the script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommandPath
if (-not $ScriptDir) { $ScriptDir = Get-Location }

# Full path to the Python script
$FullScriptPath = Join-Path $ScriptDir $ScriptPath

# Full path to the log file
$FullLogPath = Join-Path $ScriptDir $LogFile

# Validate that the Python script exists
if (-not (Test-Path $FullScriptPath)) {
    Write-Host "ERROR: Python script not found at $FullScriptPath" -ForegroundColor Red
    exit 1
}

# Function to write timestamped log entries
function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] $Message"
    Write-Host $logEntry
    Add-Content -Path $FullLogPath -Value $logEntry
}

# Function to start the Python process
function Start-PythonProcess {
    param([string]$ProcessName = "color_capture")
    
    # Kill any existing process
    $existingProcess = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -like "*$ProcessName*"
    }
    
    if ($existingProcess) {
        Write-Log "Killing existing Python process (PID: $($existingProcess.Id))"
        Stop-Process -Id $existingProcess.Id -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 1
    }
    
    # Start the new process with quoted path to handle spaces in directory names
    Write-Log "Starting Python process: $FullScriptPath"
    $process = Start-Process -FilePath python.exe -ArgumentList "`"$FullScriptPath`"" `
        -WorkingDirectory $ScriptDir `
        -NoNewWindow `
        -PassThru
    
    if ($process) {
        Write-Log "Python process started successfully (PID: $($process.Id))"
        return $process.Id
    } else {
        Write-Log "ERROR: Failed to start Python process"
        return $null
    }
}

# Function to check if a process is running
function Test-ProcessRunning {
    param([int]$ProcessId)
    
    if ($ProcessId -eq 0) { return $false }
    
    try {
        $process = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
        return $null -ne $process
    } catch {
        return $false
    }
}

# Main watchdog loop
Write-Log "=========================================="
Write-Log "Watchdog started for: $FullScriptPath"
Write-Log "Check interval: ${CheckInterval}s, Restart delay: ${RestartDelay}s"
Write-Log "Log file: $FullLogPath"
Write-Log "=========================================="

$currentPid = Start-PythonProcess
$restartCount = 0
$lastStatus = $null

while ($true) {
    Start-Sleep -Seconds $CheckInterval
    
    # Check if process is still running
    $isRunning = Test-ProcessRunning -ProcessId $currentPid
    
    if (-not $isRunning) {
        $restartCount++
        $lastStatus = "DEAD"
        Write-Log "WARNING: Python process (PID: $currentPid) is not running! Restart #$restartCount"
        
        # Wait before restarting
        Start-Sleep -Seconds $RestartDelay
        
        # Restart the process
        $currentPid = Start-PythonProcess
    } else {
        # Only log if status changed
        if ($lastStatus -ne "ALIVE") {
            Write-Log "INFO: Python process (PID: $currentPid) is running"
            $lastStatus = "ALIVE"
        }
    }
}
