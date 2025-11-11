"""
AutoHotkey Discovery Utility
Finds AutoHotkey installation on Windows systems
"""
import subprocess
from pathlib import Path
import shutil
import os


def find_autohotkey_exe():
    """
    Try to find AutoHotkey.exe in multiple locations.
    
    Returns:
        str: Full path to AutoHotkey.exe if found, None otherwise
    """
    
    # Try common installation paths
    common_paths = [
        r"C:\Program Files\AutoHotkey\AutoHotkey.exe",
        r"C:\Program Files (x86)\AutoHotkey\AutoHotkey.exe",
        r"C:\Users\{user}\AppData\Local\AutoHotkey\AutoHotkey.exe",
        r"C:\ProgramData\AutoHotkey\AutoHotkey.exe",
    ]
    
    # Expand {user} placeholder
    username = os.getenv("USERNAME")
    common_paths = [p.format(user=username) for p in common_paths]
    
    # Check each path
    for path in common_paths:
        if Path(path).exists():
            print(f"[✓] Found AutoHotkey at: {path}")
            return path
    
    # Try finding via PATH environment variable
    ahk_exe = shutil.which("AutoHotkey.exe")
    if ahk_exe:
        print(f"[✓] Found AutoHotkey in PATH: {ahk_exe}")
        return ahk_exe
    
    # Try alternative names
    ahk_v2 = shutil.which("AutoHotkey2.exe")
    if ahk_v2:
        print(f"[✓] Found AutoHotkey v2 in PATH: {ahk_v2}")
        return ahk_v2
    
    # Try running AutoHotkey directly to check if it's in PATH
    try:
        result = subprocess.run(
            ["AutoHotkey.exe", "--version"],
            capture_output=True,
            timeout=2
        )
        if result.returncode == 0:
            print(f"[✓] AutoHotkey found in PATH")
            return "AutoHotkey.exe"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    return None


def test_autohotkey():
    """Test if AutoHotkey is functional."""
    ahk_exe = find_autohotkey_exe()
    
    if not ahk_exe:
        print("[✗] AutoHotkey not found!")
        print("\nInstallation help:")
        print("  1. Download from: https://www.autohotkey.com/download/")
        print("  2. Run the installer")
        print("  3. Use default installation location")
        print("  4. Restart your terminal")
        return False
    
    try:
        result = subprocess.run(
            [ahk_exe, "--version"],
            capture_output=True,
            timeout=2
        )
        print(f"[✓] AutoHotkey version: {result.stdout.decode().strip()}")
        return True
    except Exception as e:
        print(f"[✗] AutoHotkey test failed: {e}")
        return False


if __name__ == "__main__":
    print("AutoHotkey Discovery Utility")
    print("=" * 50)
    
    ahk_path = find_autohotkey_exe()
    
    if ahk_path:
        print(f"\n[SUCCESS] AutoHotkey found at: {ahk_path}")
        test_autohotkey()
    else:
        print("\n[ERROR] AutoHotkey not found!")
        print("\nPlease install AutoHotkey:")
        print("  1. Visit: https://www.autohotkey.com/download/")
        print("  2. Download AutoHotkey v2.0 or later")
        print("  3. Run the installer (use default location)")
        print("  4. Add to PATH (if not done automatically)")
        print("  5. Restart your terminal")
