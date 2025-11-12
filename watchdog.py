"""
Watchdog Script - Monitors and restarts color_capture.py if it's killed

This script runs in the background and monitors the color_capture.py process.
If the process is killed or crashes, it automatically restarts it.

Features:
- Monitors the color_capture.py process
- Restarts if process dies unexpectedly
- Logs all activity with timestamps
- Graceful shutdown on Ctrl+C
- Can be set up as a Windows Task Scheduler task for true background operation
"""
import subprocess
import time
import sys
import os
from pathlib import Path
from datetime import datetime
import psutil


class ColorCaptureWatchdog:
    """Watchdog that monitors and restarts the color_capture.py process."""
    
    def __init__(self, script_dir=None, restart_delay=2, max_restart_attempts=10, 
                 log_file=None, check_interval=2):
        """
        Initialize the watchdog.
        
        Args:
            script_dir: Directory containing color_capture.py (defaults to script's parent)
            restart_delay: Seconds to wait before restarting after crash (default: 2)
            max_restart_attempts: Max retries before giving up (0=unlimited, default: 10)
            log_file: Path to log file (defaults to watchdog.log in script dir)
            check_interval: Seconds between process checks (default: 2)
        """
        self.script_dir = Path(script_dir) if script_dir else Path(__file__).parent
        self.color_capture_script = self.script_dir / "color_capture.py"
        self.restart_delay = restart_delay
        self.max_restart_attempts = max_restart_attempts
        self.check_interval = check_interval
        self.log_file = Path(log_file) if log_file else self.script_dir / "watchdog.log"
        
        self.process = None
        self.restart_count = 0
        self.running = True
        
        # Verify color_capture.py exists
        if not self.color_capture_script.exists():
            raise FileNotFoundError(f"color_capture.py not found at: {self.color_capture_script}")
        
        self._log(f"Watchdog initialized for: {self.color_capture_script}")
        self._log(f"Restart delay: {restart_delay}s, Check interval: {check_interval}s")
    
    def _log(self, message):
        """Log a message with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        # Also write to log file
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_message + '\n')
        except Exception as e:
            print(f"Warning: Could not write to log file: {e}")
    
    def _start_process(self):
        """Start the color_capture.py process."""
        try:
            self._log(f"Starting color_capture.py (attempt {self.restart_count + 1})")
            
            # Start the process
            self.process = subprocess.Popen(
                [sys.executable, str(self.color_capture_script)],
                cwd=str(self.script_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1  # Line buffered
            )
            
            self._log(f"Process started successfully (PID: {self.process.pid})")
            self.restart_count += 1
            return True
            
        except Exception as e:
            self._log(f"Error starting process: {e}")
            return False
    
    def _is_process_alive(self):
        """Check if the process is still running."""
        if self.process is None:
            return False
        
        # Check if process is still running
        if self.process.poll() is None:
            return True  # Process is still running
        else:
            return False  # Process has terminated
    
    def _get_process_info(self):
        """Get information about the current process."""
        if self.process is None or not self._is_process_alive():
            return None
        
        try:
            p = psutil.Process(self.process.pid)
            return {
                'pid': p.pid,
                'name': p.name(),
                'status': p.status(),
                'cpu_percent': p.cpu_percent(interval=0.1),
                'memory_mb': p.memory_info().rss / 1024 / 1024,
                'create_time': datetime.fromtimestamp(p.create_time()).strftime("%Y-%m-%d %H:%M:%S")
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None
    
    def _handle_process_crash(self, exit_code):
        """Handle process crash and restart."""
        self._log(f"Process died (exit code: {exit_code})")
        self.process = None
        
        # Check if we should continue restarting
        if self.max_restart_attempts > 0 and self.restart_count >= self.max_restart_attempts:
            self._log(f"Max restart attempts ({self.max_restart_attempts}) reached. Stopping watchdog.")
            self.running = False
            return
        
        # Wait before restarting
        self._log(f"Waiting {self.restart_delay}s before restart...")
        time.sleep(self.restart_delay)
        
        # Start the process again
        self._start_process()
    
    def run(self):
        """Main watchdog loop."""
        self._log("="*70)
        self._log("COLOR CAPTURE WATCHDOG STARTED")
        self._log("="*70)
        
        # Start the initial process
        if not self._start_process():
            self._log("Failed to start process on initialization. Exiting.")
            return
        
        try:
            while self.running:
                time.sleep(self.check_interval)
                
                # Check if process is alive
                if not self._is_process_alive():
                    exit_code = self.process.poll() if self.process else None
                    self._handle_process_crash(exit_code)
                else:
                    # Log periodic status if debug is enabled
                    info = self._get_process_info()
                    if info:
                        # Only log status every 30 seconds to reduce log spam
                        if self.restart_count % 15 == 0:  # 15 * 2s check interval = 30s
                            self._log(f"Process alive - PID: {info['pid']}, Memory: {info['memory_mb']:.1f}MB, CPU: {info['cpu_percent']:.1f}%")
                
                # Read and log any output from the process
                if self.process and self.process.stdout:
                    try:
                        # Non-blocking read of stdout
                        line = self.process.stdout.readline()
                        if line:
                            # Print to console but don't log to file (too verbose)
                            print(f"[CAPTURE] {line.rstrip()}")
                    except Exception:
                        pass
        
        except KeyboardInterrupt:
            self._log("Watchdog interrupted by user (Ctrl+C)")
        finally:
            self._shutdown()
    
    def _shutdown(self):
        """Shutdown the watchdog and terminate the process."""
        self._log("="*70)
        self._log("SHUTTING DOWN WATCHDOG")
        self._log("="*70)
        
        if self.process and self._is_process_alive():
            self._log(f"Terminating color_capture.py process (PID: {self.process.pid})")
            try:
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                    self._log("Process terminated gracefully")
                except subprocess.TimeoutExpired:
                    self._log("Process did not terminate within 5 seconds, forcing kill...")
                    self.process.kill()
                    self.process.wait()
                    self._log("Process killed")
            except Exception as e:
                self._log(f"Error terminating process: {e}")
        
        self._log(f"Watchdog stopped. Total restart attempts: {self.restart_count}")
        self._log("="*70)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Watchdog for color_capture.py - automatically restarts if killed"
    )
    parser.add_argument(
        '--script-dir',
        type=str,
        default=None,
        help='Directory containing color_capture.py (default: script directory)'
    )
    parser.add_argument(
        '--restart-delay',
        type=int,
        default=2,
        help='Seconds to wait before restarting (default: 2)'
    )
    parser.add_argument(
        '--check-interval',
        type=int,
        default=2,
        help='Seconds between process checks (default: 2)'
    )
    parser.add_argument(
        '--max-restarts',
        type=int,
        default=0,
        help='Max restart attempts before giving up (0=unlimited, default: 0)'
    )
    parser.add_argument(
        '--log-file',
        type=str,
        default=None,
        help='Path to log file (default: watchdog.log in script directory)'
    )
    
    args = parser.parse_args()
    
    try:
        watchdog = ColorCaptureWatchdog(
            script_dir=args.script_dir,
            restart_delay=args.restart_delay,
            max_restart_attempts=args.max_restarts,
            log_file=args.log_file,
            check_interval=args.check_interval
        )
        watchdog.run()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
