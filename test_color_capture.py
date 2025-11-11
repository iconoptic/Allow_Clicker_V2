"""
Comprehensive test suite for OCR filtering functionality
"""
import pytest
import cv2
import numpy as np
from pathlib import Path
import shutil
from PIL import Image, ImageDraw, ImageFont
from unittest.mock import patch, MagicMock, call

from color_capture_core import ColorCapture


@pytest.fixture(autouse=True)
def disable_ahk_in_tests():
    """Disable AutoHotkey in all tests to avoid subprocess calls."""
    # Tests will use PyAutoGUI fallback instead
    pass


@pytest.fixture
def test_dir():
    """Create a temporary test directory."""
    test_path = Path(__file__).resolve().parent / "test_temp"
    test_path.mkdir(exist_ok=True)
    yield test_path
    # Cleanup
    if test_path.exists():
        shutil.rmtree(test_path)


@pytest.fixture
def color_ref_image(test_dir):
    """Create a reference color image (light gray)."""
    img = Image.new('RGB', (100, 100), color=(200, 200, 200))
    path = test_dir / "color_ref.png"
    img.save(path)
    return path


@pytest.fixture
def captures_dir(test_dir):
    """Create captures directory path."""
    path = test_dir / "captures"
    return path


def create_test_image_with_text(text, color=(255, 255, 255)):
    """Create a test image with specified text and background color."""
    img = Image.new('RGB', (200, 100), color=color)
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    draw.text((10, 35), text, fill='black', font=font)
    
    # Convert to numpy array and BGR for OpenCV
    img_np = np.array(img)
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    return img_bgr


class TestOCRTextExtraction:
    """Test OCR text extraction functionality."""
    
    def test_extract_text_from_image_with_allow(self, color_ref_image, captures_dir):
        """Test that text extraction works and finds 'Allow' text."""
        cc = ColorCapture(color_ref_image, captures_dir, debug_mode=False, use_ahk=False)
        
        # Create test image with "Allow" text
        img_with_allow = create_test_image_with_text("Allow")
        
        extracted = cc.extract_text_from_image(img_with_allow)
        
        # Should extract something (might have variations due to OCR)
        assert extracted is not None
        assert "Allow" in extracted or "allow" in extracted.lower()
    
    def test_extract_text_from_image_with_other_text(self, color_ref_image, captures_dir):
        """Test extraction with different text."""
        cc = ColorCapture(color_ref_image, captures_dir, debug_mode=False, use_ahk=False)
        
        img_with_text = create_test_image_with_text("Click Here")
        extracted = cc.extract_text_from_image(img_with_text)
        
        assert extracted is not None
        # Should NOT contain "Allow"
        assert "Allow" not in extracted


class TestOCRFiltering:
    """Test OCR filtering logic."""
    
    def test_contains_target_text_true(self, color_ref_image, captures_dir):
        """Test detection of target text when present."""
        cc = ColorCapture(color_ref_image, captures_dir, ocr_search_text="Allow", debug_mode=False, use_ahk=False)
        
        img_with_allow = create_test_image_with_text("Allow")
        result = cc.contains_target_text(img_with_allow)
        
        assert result is True
    
    def test_contains_target_text_false(self, color_ref_image, captures_dir):
        """Test detection when target text is absent."""
        cc = ColorCapture(color_ref_image, captures_dir, ocr_search_text="Allow", debug_mode=False, use_ahk=False)
        
        img_without_allow = create_test_image_with_text("Click Here")
        result = cc.contains_target_text(img_without_allow)
        
        assert result is False
    
    def test_contains_target_text_case_insensitive(self, color_ref_image, captures_dir):
        """Test that search is case-insensitive."""
        cc = ColorCapture(color_ref_image, captures_dir, ocr_search_text="Allow", debug_mode=False, use_ahk=False)
        
        img_with_lowercase = create_test_image_with_text("allow")
        result = cc.contains_target_text(img_with_lowercase)
        
        # Should find it even in lowercase
        assert result is True
    
    def test_ocr_disabled_always_returns_true(self, color_ref_image, captures_dir):
        """Test that when OCR is disabled, all images pass."""
        cc = ColorCapture(color_ref_image, captures_dir, ocr_enabled=False, debug_mode=False, use_ahk=False)
        
        img_without_allow = create_test_image_with_text("Click Here")
        result = cc.contains_target_text(img_without_allow)
        
        # Should pass because OCR is disabled
        assert result is True


class TestRectangleProcessing:
    """Test rectangle processing and filtering."""
    
    def test_process_rectangles_filters_by_ocr(self, color_ref_image, captures_dir):
        """Test that process_rectangles only keeps images with target text."""
        cc = ColorCapture(color_ref_image, captures_dir, ocr_search_text="Allow", debug_mode=False, use_ahk=False)
        
        # Create a mock screen with test rectangles
        # Light gray background to match ref color
        screen = np.full((300, 400, 3), (200, 200, 200), dtype=np.uint8)
        
        # Add test images at different positions
        img_with_allow = create_test_image_with_text("Allow")
        img_without_allow = create_test_image_with_text("Click Here")
        
        # Paste images onto screen
        screen[50:150, 50:250] = img_with_allow
        screen[160:260, 50:250] = img_without_allow
        
        # Mock rectangles list (x, y, w, h)
        rectangles = [
            (50, 50, 200, 100),      # Contains "Allow"
            (50, 160, 200, 100),     # Contains "Click Here"
        ]
        
        valid_captures = cc.process_rectangles(screen, rectangles)
        
        # Should only keep the one with "Allow"
        assert len(valid_captures) == 1
        assert valid_captures[0]['index'] == 0
        assert valid_captures[0]['coords'] == (50, 50, 200, 100)
    
    def test_process_rectangles_empty_when_no_match(self, color_ref_image, captures_dir):
        """Test that no rectangles are kept if none contain target text."""
        cc = ColorCapture(color_ref_image, captures_dir, ocr_search_text="Allow", debug_mode=False, use_ahk=False)
        
        # Create a mock screen
        screen = np.full((300, 400, 3), (200, 200, 200), dtype=np.uint8)
        
        img_without_allow = create_test_image_with_text("Click Here")
        screen[50:150, 50:250] = img_without_allow
        
        rectangles = [(50, 50, 200, 100)]
        
        valid_captures = cc.process_rectangles(screen, rectangles)
        
        # Should be empty
        assert len(valid_captures) == 0
    
    def test_process_rectangles_keeps_all_when_ocr_disabled(self, color_ref_image, captures_dir):
        """Test that all rectangles are kept when OCR is disabled."""
        cc = ColorCapture(color_ref_image, captures_dir, ocr_enabled=False, debug_mode=False, use_ahk=False)
        
        screen = np.full((300, 400, 3), (200, 200, 200), dtype=np.uint8)
        
        img1 = create_test_image_with_text("Any Text")
        img2 = create_test_image_with_text("More Text")
        
        screen[50:150, 50:250] = img1
        screen[160:260, 50:250] = img2
        
        rectangles = [
            (50, 50, 200, 100),
            (50, 160, 200, 100),
        ]
        
        valid_captures = cc.process_rectangles(screen, rectangles)
        
        # Should keep all rectangles
        assert len(valid_captures) == 2


class TestDiskSaving:
    """Test disk saving functionality."""
    
    def test_save_captures_to_disk(self, color_ref_image, captures_dir):
        """Test that valid captures are saved correctly."""
        cc = ColorCapture(color_ref_image, captures_dir, debug_mode=False, use_ahk=False)
        
        test_image = create_test_image_with_text("Allow")
        
        valid_captures = [
            {
                'image': test_image,
                'coords': (10, 20, 200, 100),
                'index': 0
            }
        ]
        
        saved_count = cc.save_captures_to_disk(valid_captures)
        
        assert saved_count == 1
        assert (captures_dir / "capture_0000.png").exists()
    
    def test_save_captures_empty_list(self, color_ref_image, captures_dir):
        """Test saving with empty list."""
        cc = ColorCapture(color_ref_image, captures_dir, debug_mode=False, use_ahk=False)
        
        valid_captures = []
        
        saved_count = cc.save_captures_to_disk(valid_captures)
        
        assert saved_count == 0
        # Directory should exist but be empty
        assert captures_dir.exists()


class TestIntegration:
    """Integration tests for the full pipeline."""
    
    def test_full_pipeline_only_saves_allow_images(self, color_ref_image, captures_dir):
        """Test the full pipeline: find rectangles, filter by OCR, save only valid ones."""
        cc = ColorCapture(color_ref_image, captures_dir, ocr_search_text="Allow", debug_mode=False, use_ahk=False)
        
        # Create a mock screen matching the reference color (larger to fit all images)
        screen = np.full((300, 500, 3), (200, 200, 200), dtype=np.uint8)
        
        # Create test images
        img_allow = create_test_image_with_text("Allow")
        img_click = create_test_image_with_text("Click Here")
        img_allow2 = create_test_image_with_text("Allow Button")
        
        # Place them on the screen
        screen[20:120, 20:220] = img_allow      # Index 0
        screen[140:240, 20:220] = img_click     # Index 1
        screen[20:120, 260:460] = img_allow2    # Index 2
        
        # Mock rectangles that match these positions
        rectangles = [
            (20, 20, 200, 100),      # Will contain "Allow"
            (20, 140, 200, 100),     # Will contain "Click Here"
            (260, 20, 200, 100),     # Will contain "Allow Button"
        ]
        
        # Process the rectangles
        valid_captures = cc.process_rectangles(screen, rectangles)
        
        # Should have 2 valid captures (indices 0 and 2)
        assert len(valid_captures) == 2
        
        # Save to disk
        saved_count = cc.save_captures_to_disk(valid_captures)
        assert saved_count == 2
        
        # Verify files exist
        saved_files = list(captures_dir.glob("capture_*.png"))
        assert len(saved_files) == 2
        
        # Verify the rejected image was NOT saved
        assert not (captures_dir / "capture_0001.png").exists()


class TestClickFunctionality:
    """Test auto-click functionality."""
    
    @patch('color_capture_core.pyautogui.position')
    @patch('color_capture_core.pyautogui.click')
    @patch('color_capture_core.pyautogui.moveTo')
    def test_click_captures_single(self, mock_moveTo, mock_click, mock_position, color_ref_image, captures_dir):
        """Test clicking on a single rectangle."""
        cc = ColorCapture(color_ref_image, captures_dir, debug_mode=False, click_delay=0.01, use_ahk=False)
        
        # Mock cursor position
        mock_position.return_value = (100, 100)
        
        test_image = create_test_image_with_text("Allow")
        valid_captures = [
            {
                'image': test_image,
                'coords': (200, 300, 100, 50),  # x, y, w, h
                'index': 0
            }
        ]
        
        click_count = cc.click_captures(valid_captures)
        
        # Should have saved position once, clicked once, and restored position
        assert mock_position.call_count == 1
        assert mock_click.call_count == 1
        assert mock_moveTo.call_count == 2  # Move to center, then restore
        
        # Verify click was at center of rectangle
        # Center = (200 + 100//2, 300 + 50//2) = (250, 325)
        mock_click.assert_called_with(250, 325, button='left')
        
        # Verify cursor was restored
        mock_moveTo.assert_called_with(100, 100, duration=0.1)
        
        assert click_count == 1
    
    @patch('color_capture_core.pyautogui.position')
    @patch('color_capture_core.pyautogui.click')
    @patch('color_capture_core.pyautogui.moveTo')
    def test_click_captures_multiple(self, mock_moveTo, mock_click, mock_position, color_ref_image, captures_dir):
        """Test clicking on multiple rectangles."""
        cc = ColorCapture(color_ref_image, captures_dir, debug_mode=False, click_delay=0.01, use_ahk=False)
        
        mock_position.return_value = (50, 50)
        
        test_image = create_test_image_with_text("Allow")
        valid_captures = [
            {
                'image': test_image,
                'coords': (100, 100, 80, 40),
                'index': 0
            },
            {
                'image': test_image,
                'coords': (300, 200, 60, 50),
                'index': 1
            },
            {
                'image': test_image,
                'coords': (400, 400, 100, 100),
                'index': 2
            }
        ]
        
        click_count = cc.click_captures(valid_captures)
        
        assert click_count == 3
        assert mock_click.call_count == 3
        
        # Verify all clicks happened at center positions
        expected_calls = [
            call(140, 120, button='left'),  # (100 + 80//2, 100 + 40//2)
            call(330, 225, button='left'),  # (300 + 60//2, 200 + 50//2)
            call(450, 450, button='left'),  # (400 + 100//2, 400 + 100//2)
        ]
        mock_click.assert_has_calls(expected_calls)
        
        # Should restore cursor once at the end
        assert mock_moveTo.call_count == 4  # 3 moves to centers + 1 restore
        mock_moveTo.assert_called_with(50, 50, duration=0.1)
    
    @patch('color_capture_core.pyautogui.position')
    @patch('color_capture_core.pyautogui.click')
    @patch('color_capture_core.pyautogui.moveTo')
    def test_click_captures_empty(self, mock_moveTo, mock_click, mock_position, color_ref_image, captures_dir):
        """Test clicking with empty list."""
        cc = ColorCapture(color_ref_image, captures_dir, debug_mode=False, click_delay=0.01, use_ahk=False)
        
        click_count = cc.click_captures([])
        
        # Should not click anything or save position
        assert click_count == 0
        mock_position.assert_not_called()
        mock_click.assert_not_called()
        mock_moveTo.assert_not_called()
    
    @patch('color_capture_core.pyautogui.position')
    @patch('color_capture_core.pyautogui.click')
    @patch('color_capture_core.pyautogui.moveTo')
    def test_click_captures_restores_on_exception(self, mock_moveTo, mock_click, mock_position, color_ref_image, captures_dir):
        """Test that cursor is restored even when click fails."""
        cc = ColorCapture(color_ref_image, captures_dir, debug_mode=False, click_delay=0.01, use_ahk=False)
        
        mock_position.return_value = (100, 100)
        mock_click.side_effect = Exception("Simulated click failure")
        
        test_image = create_test_image_with_text("Allow")
        valid_captures = [
            {
                'image': test_image,
                'coords': (200, 300, 100, 50),
                'index': 0
            }
        ]
        
        # Should raise the exception but still restore cursor
        with pytest.raises(Exception):
            cc.click_captures(valid_captures)
        
        # Cursor should still be restored (one moveTo to center, one to restore)
        assert mock_moveTo.call_count == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
