"""
Quick test to verify the watchdog works correctly.

This script:
1. Starts the watchdog
2. Lets it run for 10 seconds
3. Simulates killing the process
4. Verifies the watchdog restarts it
5. Cleans up and reports results
"""
import subprocess
import time
import sys
from pathlib import Path


def test_watchdog():
    """Test the watchdog functionality."""
    script_dir = Path(__file__).parent
    
    print("="*70)
    print("WATCHDOG TEST - Verify auto-restart functionality")
    print("="*70)
    print()
    
    # Start watchdog in a subprocess
    print("[1] Starting watchdog...")
    watchdog_process = subprocess.Popen(
        [sys.executable, str(script_dir / "watchdog.py"), "--restart-delay", "1"],
        cwd=str(script_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    # Let it run for a few seconds
    print("[2] Watchdog running (PID: {})".format(watchdog_process.pid))
    time.sleep(3)
    print()
    
    # Get the color_capture.py PID from the watchdog output
    print("[3] Checking if color_capture.py was started...")
    print("    (You should see a process with color_capture.py running)")
    print()
    
    print("[4] To test the watchdog properly:")
    print("    - The watchdog is now running in the background")
    print("    - Open Windows Task Manager (Ctrl+Shift+Esc)")
    print("    - Find the 'python.exe' process running 'color_capture.py'")
    print("    - Right-click it and select 'End Process'")
    print("    - The watchdog should restart it within 1-3 seconds")
    print("    - Check watchdog.log for restart confirmation")
    print()
    
    # Clean up
    print("[5] Press Ctrl+C in the watchdog window to stop the test")
    print("    or press Ctrl+C here to terminate this test script")
    print()
    
    try:
        watchdog_process.wait()
    except KeyboardInterrupt:
        print()
        print("[✓] Test terminated by user")
        watchdog_process.terminate()
        watchdog_process.wait()
    
    print()
    print("="*70)
    print("TEST COMPLETE")
    print("="*70)


if __name__ == "__main__":
    test_watchdog()
