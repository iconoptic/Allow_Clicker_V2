"""
Color Capture Script - Main entry point
Uses ColorCapture class from color_capture_core for all core functionality
"""
import pyautogui
import time
import shutil
import cv2
import numpy as np
from pathlib import Path

from color_capture_core import ColorCapture, find_autohotkey_exe

# Configuration
SCRIPT_DIR = Path(__file__).resolve().parent
COLOR_REF_PATH = SCRIPT_DIR / "assets" / "color_ref.png"
CAPTURES_DIR = SCRIPT_DIR / "captures"
POLL_INTERVAL = 1  # seconds
COLOR_TOLERANCE = 30  # tolerance for color matching (0-255)
OCR_SEARCH_TEXT = ["Allow", "Try Again", "Continue"]  # Text to search for in images (case-insensitive)
OCR_ENABLED = True  # Set to False to disable OCR filtering
DEBUG_MODE = True  # Enable detailed logging
AUTO_CLICK_ENABLED = True  # Set to False to disable auto-clicking
CLICK_DELAY = 0.5  # Delay between cursor movement and click (seconds) - increased for reliability
USE_AUTOHOTKEY = True  # Use AutoHotkey for clicks (better VM compatibility), falls back to PyAutoGUI


def get_screen_image():
    """Capture the entire screen."""
    screenshot = pyautogui.screenshot()
    screen_np = np.array(screenshot)
    return cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)


def run_background_capture():
    """Main loop for continuous screen capture and processing."""
    print("Initializing color capture script...")
    print(f"Captures will be saved to: {CAPTURES_DIR}")
    print(f"OCR Filtering: {'ENABLED' if OCR_ENABLED else 'DISABLED'}")
    print(f"Debug Mode: {'ON' if DEBUG_MODE else 'OFF'}")
    if OCR_ENABLED:
        search_texts = ", ".join(f"'{text}'" for text in OCR_SEARCH_TEXT)
        print(f"Searching for text: {search_texts}")
    
    # Check AutoHotkey availability
    if USE_AUTOHOTKEY:
        ahk_exe = find_autohotkey_exe()
        if ahk_exe:
            print(f"AutoHotkey: FOUND at {ahk_exe}")
        else:
            print(f"AutoHotkey: NOT FOUND (will use PyAutoGUI fallback)")
    print()
    
    try:
        # Initialize ColorCapture
        cc = ColorCapture(
            COLOR_REF_PATH,
            CAPTURES_DIR,
            ocr_enabled=OCR_ENABLED,
            ocr_search_text=OCR_SEARCH_TEXT,
            color_tolerance=COLOR_TOLERANCE,
            debug_mode=DEBUG_MODE,
            click_delay=CLICK_DELAY,
            use_ahk=USE_AUTOHOTKEY
        )
        
        print("Starting background capture loop (press Ctrl+C to stop)...\n")
        
        iteration = 0
        while True:
            iteration += 1
            
            # Clear previous captures at start of loop (with robust error handling)
            if CAPTURES_DIR.exists():
                try:
                    shutil.rmtree(CAPTURES_DIR)
                except PermissionError:
                    # Files may be locked, try deleting individual files
                    if DEBUG_MODE:
                        print("[INFO] Captures folder locked, clearing files individually...")
                    try:
                        for file in CAPTURES_DIR.glob("*"):
                            if file.is_file():
                                file.unlink()
                    except Exception as e:
                        if DEBUG_MODE:
                            print(f"[WARNING] Could not clear all files: {e}")
            CAPTURES_DIR.mkdir(parents=True, exist_ok=True)
            
            print(f"\n{'='*60}")
            print(f"Iteration {iteration} | Time: {time.strftime('%H:%M:%S')}")
            print(f"{'='*60}")
            
            # Capture screen
            screen = get_screen_image()
            
            # Find matching rectangles
            rectangles, mask = cc.find_matching_rectangles(screen)
            print(f"Found {len(rectangles)} color-matching rectangle(s)\n")
            
            # Process rectangles in memory (filter by OCR)
            if rectangles:
                print("Processing rectangles:")
                valid_captures = cc.process_rectangles(screen, rectangles)
                
                if valid_captures:
                    print(f"\n[OK] {len(valid_captures)} rectangle(s) passed OCR filter, saving to disk...")
                    saved_count = cc.save_captures_to_disk(valid_captures)
                    print(f"[OK] Saved {saved_count} image(s) to {CAPTURES_DIR}\n")
                    
                    # Auto-click on the rectangles
                    if AUTO_CLICK_ENABLED:
                        print(f"[INFO] Auto-clicking on {len(valid_captures)} rectangle(s)...")
                        click_count = cc.click_captures(valid_captures)
                        print(f"[OK] Clicked {click_count} rectangle(s), cursor restored\n")
                else:
                    print(f"\n[INFO] No rectangles contain '{OCR_SEARCH_TEXT}' text - captures folder is empty\n")
            else:
                print(f"[INFO] No color-matching rectangles found - captures folder is empty\n")
            
            # Wait for next poll
            time.sleep(POLL_INTERVAL)
    
    except KeyboardInterrupt:
        print("\n\nCapture script stopped by user.")
    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    run_background_capture()

