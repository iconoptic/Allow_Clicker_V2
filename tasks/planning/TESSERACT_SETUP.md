# Tesseract OCR Installation Guide

The script requires Tesseract-OCR to be installed on your system. Follow these steps for Windows:

## Windows Installation

### Option 1: Download Installer (Recommended)

1. Go to: https://github.com/UB-Mannheim/tesseract/wiki
2. Download the latest `.exe` installer (e.g., `tesseract-ocr-w64-setup-v5.x.x.exe`)
3. Run the installer
4. **Important**: Note the installation path (default is `C:\Program Files\Tesseract-OCR`)
5. Complete the installation

### Option 2: Verify Tesseract is Available

The script will automatically find Tesseract if it's in the default location (`C:\Program Files\Tesseract-OCR`) or in your system PATH.

### Option 3: Manual Path Configuration

If Tesseract is installed elsewhere, edit `color_capture.py` and add this line after the imports:

```python
import pytesseract
pytesseract.pytesseract.pytesseract_cmd = r'C:\path\to\your\tesseract.exe'
```

## Verify Installation

After installation, you can verify Tesseract works by running:

```powershell
tesseract --version
```

If this command fails, add Tesseract to your system PATH or use Option 3 above.

## Troubleshooting

### "pytesseract.TesseractNotFoundError"

This means the script can't find the Tesseract executable. Try:

1. Reinstall Tesseract using the installer (Option 1)
2. Or manually set the path in `color_capture.py` (Option 3)
3. Or add Tesseract to your PATH environment variable

### Poor OCR Accuracy

If the OCR is not recognizing text properly:

1. The target rectangles may have low contrast
2. Try adjusting `COLOR_TOLERANCE` to get cleaner rectangle detection
3. Set `OCR_ENABLED = False` in `color_capture.py` to see all rectangles first

### Script Runs but No "Allow" Text Found

1. Check the captured images in the `captures/` folder manually
2. Verify the text actually says "Allow" and not a similar word
3. Consider disabling OCR to see all detected rectangles
