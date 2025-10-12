#!/bin/bash

# Screen Privacy Blocker - Uninstall Script

# Color codes
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

echo ""
echo "╔═══════════════════════════════════════════════════╗"
echo "║   Screen Privacy Blocker - Uninstall              ║"
echo "╚═══════════════════════════════════════════════════╝"
echo ""

echo -e "${YELLOW}This will remove the Screen Privacy Blocker from your system.${NC}"
echo ""
echo "The following will be removed:"
echo "  - ScreenBlocker.app"
echo "  - Python virtual environment (venv)"
echo "  - Build artifacts"
echo ""
echo -e "${YELLOW}The following will NOT be removed:${NC}"
echo "  - Source code"
echo "  - System dependencies (Homebrew, Tesseract, Xcode)"
echo "  - System permissions"
echo ""

read -p "Continue with uninstall? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Uninstall cancelled."
    exit 0
fi

echo ""
echo "Uninstalling..."

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Stop any running processes
echo "Stopping any running processes..."
killall ScreenBlocker 2>/dev/null || true
pkill -f "recv_ws.py" 2>/dev/null || true
pkill -f "overlay_server.py" 2>/dev/null || true
pkill -f "start_high_quality_blocker.py" 2>/dev/null || true

# Remove ScreenBlocker app
if [ -d "ScreenBlocker.app" ]; then
    echo "Removing ScreenBlocker.app..."
    rm -rf ScreenBlocker.app
    echo -e "${GREEN}OK: ScreenBlocker.app removed${NC}"
fi

# Remove virtual environment
if [ -d "venv" ]; then
    echo "Removing Python virtual environment..."
    rm -rf venv
    echo -e "${GREEN}OK: Virtual environment removed${NC}"
fi

# Remove build artifacts
if [ -d "macos_app/build" ]; then
    echo "Removing build artifacts..."
    rm -rf macos_app/build
    echo -e "${GREEN}OK: Build artifacts removed${NC}"
fi

# Remove Python cache files
echo "Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
echo -e "${GREEN}OK: Cache files removed${NC}"

echo ""
echo "╔═══════════════════════════════════════════════════╗"
echo "║   Uninstall Complete                              ║"
echo "╚═══════════════════════════════════════════════════╝"
echo ""
echo "The application has been removed from your system."
echo ""
echo "To remove system permissions:"
echo "  1. Go to System Settings → Privacy & Security → Screen Recording"
echo "  2. Remove ScreenBlocker from the list"
echo ""
echo "To remove system dependencies (optional):"
echo "  brew uninstall tesseract"
echo ""
echo "To remove the source code:"
echo "  cd .. && rm -rf $(basename $SCRIPT_DIR)"
echo ""

