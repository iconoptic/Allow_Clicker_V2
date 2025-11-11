#!/usr/bin/env python
"""Quick test of AutoHotkey discovery."""

from color_capture_core import find_autohotkey_exe

exe = find_autohotkey_exe()
if exe:
    print(f"✓ AutoHotkey found at: {exe}")
else:
    print("✓ AutoHotkey not found (script will use PyAutoGUI fallback)")
