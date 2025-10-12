#!/bin/bash

# Clean script - Remove temporary and cache files

echo "Cleaning Screen Privacy Blocker project..."
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Remove Python cache
echo "Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

# Remove macOS files
echo "Removing macOS temporary files..."
find . -name ".DS_Store" -delete 2>/dev/null || true

# Remove editor temporary files
echo "Removing editor temporary files..."
find . -type f \( -name "*.swp" -o -name "*.swo" -o -name "*~" \) -delete 2>/dev/null || true

# Remove build artifacts (optional - uncomment if needed)
# echo "Removing build artifacts..."
# rm -rf ScreenBlocker.app 2>/dev/null || true
# rm -rf macos_app/build 2>/dev/null || true

# Remove logs (optional - uncomment if needed)
# echo "Removing log files..."
# find . -type f -name "*.log" -delete 2>/dev/null || true

echo ""
echo "OK: Cleanup complete!"
echo ""
echo "To rebuild the app after cleaning, run: ./setup.sh"

