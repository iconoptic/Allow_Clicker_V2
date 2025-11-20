"""
Color Capture Module - Core logic extracted for testing
"""
import cv2
import numpy as np
import pytesseract
import pyautogui
import time
from pathlib import Path
from PIL import Image


class ColorCapture:
    """Main class for color-based rectangle capture with OCR filtering."""
    
    def __init__(self, color_ref_path, captures_dir, ocr_enabled=True, 
                 ocr_search_text="Allow", color_tolerance=30, debug_mode=True, click_delay=0.1,
                 use_ahk=True):
        self.color_ref_path = Path(color_ref_path)
        self.captures_dir = Path(captures_dir)
        self.ocr_enabled = ocr_enabled
        self.ocr_search_text = ocr_search_text
        self.color_tolerance = color_tolerance
        self.debug_mode = debug_mode
        self.click_delay = click_delay  # Delay between cursor movement and click (seconds)
        self.use_ahk = use_ahk  # Use PyAutoGUI for clicks
        
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
        Double-click on each captured rectangle to select the window, then restore cursor to original position.
        Uses PyAutoGUI for clicking.
        
        Args:
            valid_captures: List of capture dictionaries with 'coords' key
            
        Returns:
            Number of successful double-clicks performed
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
                    print(f"  Double-clicking at ({center_x}, {center_y})...")
                
                # Move to target
                pyautogui.moveTo(center_x, center_y, duration=0.05)
                time.sleep(0.01)
                
                # Double-click to select window and activate button
                pyautogui.click(center_x, center_y, button='left')
                time.sleep(0.05)  # Delay between clicks in double-click
                pyautogui.click(center_x, center_y, button='left')
                time.sleep(0.01)  # Minimal delay between targets
                
                click_count += 1
                
                if self.debug_mode:
                    print(f"  Double-click #{click_count} completed")
        
        finally:
            # Always restore cursor to original position
            if self.debug_mode:
                print(f"  Restoring cursor to: ({original_x}, {original_y})")
            pyautogui.moveTo(original_x, original_y, duration=0.05)
            
            # Wait a moment for cursor to settle
            time.sleep(0.05)
            
            # Click at the original cursor position
            if self.debug_mode:
                print(f"  Clicking at original cursor position: ({original_x}, {original_y})")
            pyautogui.click(original_x, original_y, button='left')
            
            if self.debug_mode:
                print(f"  Final click completed")
        
        return click_count
