"""
Color Capture Module - Core logic extracted for testing
"""
import cv2
import numpy as np
import pytesseract
import pyautogui
import time
import subprocess
import tempfile
from pathlib import Path
from PIL import Image


def find_autohotkey_exe():
    """
    Find AutoHotkey.exe in common installation locations.
    
    Returns:
        str: Path to AutoHotkey.exe if found, 'AutoHotkey.exe' if in PATH, None otherwise
    """
    # Common AutoHotkey installation paths (checked first)
    common_paths = [
        Path("C:\\Program Files\\AutoHotkey\\v2\\AutoHotkey.exe"),  # AutoHotkey v2 (found on this system)
        Path("C:\\Program Files\\AutoHotkey\\AutoHotkey.exe"),      # AutoHotkey v1
        Path("C:\\Program Files (x86)\\AutoHotkey\\AutoHotkey.exe"),
        Path(Path.home() / "AppData\\Local\\Programs\\AutoHotkey\\AutoHotkey.exe"),
        Path("C:\\ProgramData\\AutoHotkey\\AutoHotkey.exe"),
    ]
    
    for path in common_paths:
        if path.exists():
            return str(path)
    
    # Try to find in PATH using where command
    try:
        result = subprocess.run(
            ["where", "AutoHotkey.exe"],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            exe_path = result.stdout.strip().split('\n')[0]
            return exe_path
    except Exception:
        pass
    
    # Try to find using python's shutil.which
    import shutil
    ahk_path = shutil.which("AutoHotkey.exe")
    if ahk_path:
        return ahk_path
    
    # If not found but executable might be in PATH, return just the name
    # (subprocess will search PATH automatically)
    try:
        result = subprocess.run(
            ["AutoHotkey.exe", "--version"],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            return "AutoHotkey.exe"
    except Exception:
        pass
    
    return None


class ColorCapture:
    """Main class for color-based rectangle capture with OCR filtering."""
    
    def __init__(self, color_ref_path, captures_dir, ocr_enabled=True, 
                 ocr_search_text="Allow", color_tolerance=30, debug_mode=True, click_delay=0.1,
                 use_ahk=True, ahk_script_path=None):
        self.color_ref_path = Path(color_ref_path)
        self.captures_dir = Path(captures_dir)
        self.ocr_enabled = ocr_enabled
        self.ocr_search_text = ocr_search_text
        self.color_tolerance = color_tolerance
        self.debug_mode = debug_mode
        self.click_delay = click_delay  # Delay between cursor movement and click (seconds)
        self.use_ahk = use_ahk  # Use AutoHotkey for clicks instead of PyAutoGUI
        
        # Set AHK script path (defaults to script directory)
        if ahk_script_path:
            self.ahk_script_path = Path(ahk_script_path)
        else:
            self.ahk_script_path = Path(__file__).parent / "click_helper.ahk"
        
        self.ref_color = None
        
        # Load reference color on init
        self._load_reference_color()
    
    def _load_reference_color(self):
        """Load and cache the reference color."""
        if not self.color_ref_path.exists():
            raise FileNotFoundError(f"Color reference image not found: {self.color_ref_path}")
        
        img = cv2.imread(str(self.color_ref_path))
        if img is None:
            raise ValueError(f"Could not load image: {self.color_ref_path}")
        
        # Convert BGR to RGB and get the average color
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.ref_color = np.mean(img_rgb, axis=(0, 1)).astype(int)
        
        if self.debug_mode:
            print(f"Reference color (RGB): {self.ref_color}")
    
    def extract_text_from_image(self, image_bgr):
        """Extract text from an image using OCR (Tesseract)."""
        try:
            # Convert BGR to RGB for Tesseract
            image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
            
            # Convert to PIL Image
            pil_image = Image.fromarray(image_rgb)
            
            # Extract text using Tesseract
            text = pytesseract.image_to_string(pil_image)
            
            return text
        except Exception as e:
            if self.debug_mode:
                print(f"OCR Error: {e}")
            return ""
    
    def contains_target_text(self, image_bgr):
        """Check if image contains any of the target texts using OCR."""
        if not self.ocr_enabled:
            return True
        
        try:
            extracted_text = self.extract_text_from_image(image_bgr)
            extracted_lower = extracted_text.lower()
            
            # Handle both string and list of search terms
            search_terms = self.ocr_search_text if isinstance(self.ocr_search_text, list) else [self.ocr_search_text]
            has_text = any(term.lower() in extracted_lower for term in search_terms)
            
            if self.debug_mode:
                print(f"    OCR extracted: '{extracted_text.strip()}'")
                search_terms_str = "', '".join(search_terms)
                print(f"    Contains '{search_terms_str}': {has_text}")
            
            return has_text
        except Exception as e:
            if self.debug_mode:
                print(f"OCR check failed: {e}")
            return False
    
    def find_matching_rectangles(self, screen):
        """Find all rectangles with background matching the reference color."""
        if self.ref_color is None:
            raise ValueError("Reference color not loaded. Call _load_reference_color() first.")
        
        # Convert ref_color to BGR if it's in RGB
        ref_color_bgr = (self.ref_color[2], self.ref_color[1], self.ref_color[0])
        
        # Create a mask for pixels matching the reference color (within tolerance)
        lower_bound = np.array([max(0, c - self.color_tolerance) for c in ref_color_bgr])
        upper_bound = np.array([min(255, c + self.color_tolerance) for c in ref_color_bgr])
        
        mask = cv2.inRange(screen, lower_bound, upper_bound)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        rectangles = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            # Filter out very small rectangles (noise)
            if w > 10 and h > 10:
                rectangles.append((x, y, w, h))
        
        return rectangles, mask
    
    def process_rectangles(self, screen, rectangles):
        """
        Process rectangles: filter by size and OCR, collect valid ones in memory.
        Only runs OCR on rectangles within size constraints: 60px < w < 200px and 20px < h < 50px
        Returns only rectangles that pass both size and OCR filters.
        """
        valid_captures = []
        
        for idx, (x, y, w, h) in enumerate(rectangles):
            # Ensure coordinates are within bounds
            x = max(0, x)
            y = max(0, y)
            w = min(w, screen.shape[1] - x)
            h = min(h, screen.shape[0] - y)
            
            # Crop the rectangle (keep in memory)
            cropped = screen[y:y+h, x:x+w]
            
            if cropped.size > 0:
                if self.debug_mode:
                    print(f"  Rectangle [{idx}] at ({x}, {y}) size {w}x{h}:")
                
                # Check size constraints (only run OCR if within size range)
                if 60 < w < 200 and 20 < h < 50:
                    # Check OCR filter
                    if self.contains_target_text(cropped):
                        valid_captures.append({
                            'image': cropped,
                            'coords': (x, y, w, h),
                            'index': idx
                        })
                        if self.debug_mode:
                            print(f"    [PASS] size {w}x{h} within range, OCR passed, will be stored")
                    else:
                        if self.debug_mode:
                            print(f"    [FAIL] size {w}x{h} within range, but OCR failed")
                else:
                    if self.debug_mode:
                        print(f"    [SKIP] size {w}x{h} outside range (60<w<200, 20<h<50)")
        
        return valid_captures
    
    def save_captures_to_disk(self, valid_captures):
        """Save only the valid in-memory captures to disk."""
        self.captures_dir.mkdir(parents=True, exist_ok=True)
        
        saved_count = 0
        for capture in valid_captures:
            filename = self.captures_dir / f"capture_{capture['index']:04d}.png"
            
            # Save the cropped image
            cv2.imwrite(str(filename), capture['image'])
            if self.debug_mode:
                print(f"  → Saved to disk: {filename.name}")
            saved_count += 1
        
        return saved_count
    
    def click_captures(self, valid_captures):
        """
        Click on the center of each captured rectangle, restore cursor to original position, then click once more.
        Uses AutoHotkey for better VM compatibility, falls back to PyAutoGUI if AHK unavailable.
        
        Args:
            valid_captures: List of capture dictionaries with 'coords' key
            
        Returns:
            Number of successful clicks performed (includes final click at original position)
        """
        if not valid_captures:
            return 0
        
        # Save current cursor position
        original_x, original_y = pyautogui.position()
        if self.debug_mode:
            print(f"  Saved cursor position: ({original_x}, {original_y})")
        
        click_count = 0
        try:
            for capture in valid_captures:
                x, y, w, h = capture['coords']
                # Calculate center of the rectangle
                center_x = x + w // 2
                center_y = y + h // 2
                
                if self.debug_mode:
                    print(f"  Moving to ({center_x}, {center_y})...")
                
                # Move to position first, with small delay
                pyautogui.moveTo(center_x, center_y, duration=0.1)
                if self.debug_mode:
                    after_move_x, after_move_y = pyautogui.position()
                    print(f"  [DEBUG] Cursor after pyautogui.moveTo: ({after_move_x}, {after_move_y})")
                
                # Wait a bit for the move to complete
                time.sleep(self.click_delay)
                
                # Click using AutoHotkey or PyAutoGUI
                if self.use_ahk and self.ahk_script_path.exists():
                    # Try to find and use AutoHotkey for more reliable VM clicks
                    if self.debug_mode:
                        print(f"  Clicking at ({center_x}, {center_y}) via AutoHotkey")
                    try:
                        # Find AutoHotkey executable
                        ahk_exe = find_autohotkey_exe()
                        if ahk_exe:
                            # Call AutoHotkey script with coordinates and delay
                            subprocess.run(
                                [str(ahk_exe), str(self.ahk_script_path), str(center_x), str(center_y), str(int(self.click_delay * 1000))],
                                check=True,
                                timeout=5
                            )
                            time.sleep(0.05)  # Allow the AHK script time to write its log and perform clicks
                            # Print current cursor post-click (for verification)
                            curr_x, curr_y = pyautogui.position()
                            if self.debug_mode:
                                print(f"  [DEBUG] Cursor after AHK click: ({curr_x}, {curr_y})")
                            # Attempt to read the AHK log in temp to verify coordinates clicked
                            try:
                                tmp_log = Path(tempfile.gettempdir()) / "allow_clicker_ahk.log"
                                if tmp_log.exists():
                                    # Print last 3 lines of the log.
                                    with tmp_log.open('r', encoding='utf-8') as f:
                                        lines = f.read().strip().splitlines()
                                    if lines:
                                        for log_line in lines[-3:]:
                                            print(f"  [AHK LOG] {log_line}")
                            except Exception as e:
                                if self.debug_mode:
                                    print(f"  [DEBUG] Could not read AHK log: {e}")
                        else:
                            if self.debug_mode:
                                print(f"  [INFO] AutoHotkey.exe not found in PATH. Falling back to PyAutoGUI...")
                            pyautogui.click(center_x, center_y, button='left')
                    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                        if self.debug_mode:
                            print(f"  [WARNING] AutoHotkey execution failed: {e}. Falling back to PyAutoGUI...")
                        # Fallback to PyAutoGUI if AHK fails
                        pyautogui.click(center_x, center_y, button='left')
                else:
                    # Use PyAutoGUI as fallback
                    if self.debug_mode:
                        print(f"  Clicking at ({center_x}, {center_y}) via PyAutoGUI")
                    pyautogui.click(center_x, center_y, button='left')
                
                # Small delay between clicks
                time.sleep(0.05)
                
                click_count += 1
                
                if self.debug_mode:
                    print(f"  Click #{click_count} completed")
                # Verify whether the click succeeded: re-OCR the area; if still present, try fallback
                if self.ocr_enabled:
                    # Small delay to allow UI update
                    time.sleep(0.2)
                    try:
                        # Capture screen and crop to the rectangle
                        full_scr = pyautogui.screenshot()
                        scr_np = np.array(full_scr)
                        scr_bgr = cv2.cvtColor(scr_np, cv2.COLOR_RGB2BGR)
                        x, y, w, h = capture['coords']
                        crop = scr_bgr[y:y+h, x:x+w]
                        still_has = self.contains_target_text(crop)
                        if still_has:
                            if self.debug_mode:
                                print(f"  [DEBUG] After click, target still present at ({x},{y},{w},{h}). Trying fallback click via PyAutoGUI.")
                            # Try PyAutoGUI click as a fallback
                            pyautogui.click(center_x, center_y, button='left')
                            time.sleep(0.2)
                            # Recheck again
                            full_scr = pyautogui.screenshot()
                            scr_np = np.array(full_scr)
                            scr_bgr = cv2.cvtColor(scr_np, cv2.COLOR_RGB2BGR)
                            crop = scr_bgr[y:y+h, x:x+w]
                            still_has = self.contains_target_text(crop)
                            if still_has:
                                if self.debug_mode:
                                    print(f"  [WARNING] Button still present after fallback click.")
                                # Try sending Enter as a final attempt
                                try:
                                    pyautogui.press('enter')
                                    time.sleep(0.15)
                                    full_scr = pyautogui.screenshot()
                                    scr_np = np.array(full_scr)
                                    scr_bgr = cv2.cvtColor(scr_np, cv2.COLOR_RGB2BGR)
                                    crop = scr_bgr[y:y+h, x:x+w]
                                    still_has = self.contains_target_text(crop)
                                    if still_has and self.debug_mode:
                                        print(f"  [WARNING] Button still present after Enter key press.")
                                except Exception as e:
                                    if self.debug_mode:
                                        print(f"  [DEBUG] Enter key fallback failed: {e}")
                                # Save a full-screen debug capture after fallback
                                try:
                                    dbg_path = self.captures_dir / f"after_click_{int(time.time())}.png"
                                    full = pyautogui.screenshot()
                                    full.save(str(dbg_path))
                                    if self.debug_mode:
                                        print(f"  [DEBUG] Saved after-click screenshot to {dbg_path}")
                                except Exception as e:
                                    if self.debug_mode:
                                        print(f"  [DEBUG] Failed saving after-click screenshot: {e}")
                    except Exception as e:
                        if self.debug_mode:
                            print(f"  [DEBUG] Re-check after click failed: {e}")
        
        finally:
            # Always restore cursor to original position
            if self.debug_mode:
                print(f"  Restoring cursor to: ({original_x}, {original_y})")
            pyautogui.moveTo(original_x, original_y, duration=0.1)
            
            # Wait a moment for cursor to settle
            time.sleep(0.2)
            
            # Click at the original cursor position
            if self.debug_mode:
                print(f"  Clicking at original cursor position: ({original_x}, {original_y})")
            pyautogui.click(original_x, original_y, button='left')
            
            if self.debug_mode:
                print(f"  Final click completed")
        
        return click_count
