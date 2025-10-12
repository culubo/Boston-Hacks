#!/bin/bash

# Screen Privacy Blocker Installation Script

set -e

echo "Installing Screen Privacy Blocker..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    echo "Please install Python 3 from https://python.org"
    exit 1
fi

# Install dependencies
echo "Installing Python dependencies..."
pip3 install --break-system-packages opencv-python Pillow pytesseract

# Install tkinter (if not available)
echo "Checking for tkinter..."
python3 -c "import tkinter" 2>/dev/null || {
    echo "Installing tkinter..."
    brew install python-tk
}

# Install Tesseract OCR (macOS)
if command -v brew &> /dev/null; then
    echo "Installing Tesseract OCR via Homebrew..."
    brew install tesseract
else
    echo "Warning: Homebrew not found. Please install Tesseract OCR manually:"
    echo "https://github.com/tesseract-ocr/tesseract"
fi

echo ""
echo "Installation complete!"
echo ""
echo "To start the application:"
echo "1. Run: ./start_blocker.sh"
echo "2. Grant screen recording permission when prompted"
echo ""
echo "IMPORTANT: Grant screen recording permission in System Preferences!"
