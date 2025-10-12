#!/bin/bash

# Screen Privacy Blocker - Automated Setup Script
# This script will install all dependencies and build the application

set -e

echo ""
echo "╔═══════════════════════════════════════════════════╗"
echo "║                                                   ║"
echo "║       SCREEN PRIVACY BLOCKER - SETUP         ║"
echo "║                                                   ║"
echo "║     Automated Installation & Configuration        ║"
echo "║                                                   ║"
echo "╚═══════════════════════════════════════════════════╝"
echo ""
echo "This will install all dependencies and build the app."
echo "Estimated time: 3-7 minutes"
echo ""

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Progress counter
TOTAL_STEPS=7
CURRENT_STEP=0

# Function to show progress
show_progress() {
    CURRENT_STEP=$((CURRENT_STEP + 1))
    echo -e "${BLUE}[$CURRENT_STEP/$TOTAL_STEPS]${NC} $1"
}

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Step 1: Check Python 3
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
show_progress "Checking Python 3..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Error: Python 3 is required but not installed.${NC}"
    echo "Please install Python 3 from https://python.org"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN} Found: $PYTHON_VERSION${NC}"
echo ""

# Step 2: Check/Install Homebrew
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
show_progress "Checking Homebrew..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if ! command -v brew &> /dev/null; then
    echo -e "${YELLOW}⚠ Homebrew not found. Installing Homebrew...${NC}"
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo -e "${GREEN} Homebrew is installed${NC}"
fi
echo ""

# Step 3: Install Tesseract
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
show_progress "Installing Tesseract OCR..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if ! command -v tesseract &> /dev/null; then
    echo "Installing Tesseract via Homebrew..."
    brew install tesseract
    echo -e "${GREEN} Tesseract installed${NC}"
else
    echo -e "${GREEN} Tesseract already installed${NC}"
fi
echo ""

# Step 4: Check Xcode Command Line Tools
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
show_progress "Checking Xcode Command Line Tools..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if ! command -v xcodebuild &> /dev/null; then
    echo -e "${YELLOW}⚠ Xcode Command Line Tools not found.${NC}"
    echo "Installing Xcode Command Line Tools..."
    echo "Please follow the prompt to install."
    xcode-select --install
    echo -e "${YELLOW}Waiting for installation to complete...${NC}"
    echo "Press ENTER once installation is finished."
    read -r
else
    echo -e "${GREEN} Xcode Command Line Tools installed${NC}"
fi
echo ""

# Step 5: Create virtual environment
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
show_progress "Setting up Python virtual environment..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN} Virtual environment created${NC}"
else
    echo -e "${GREEN} Virtual environment already exists${NC}"
fi
echo ""

# Step 6: Install Python dependencies
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
show_progress "Installing Python dependencies..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
echo "Installing packages (this may take a minute)..."
pip install -r requirements.txt
echo -e "${GREEN} Python dependencies installed${NC}"
echo ""

# Step 7: Build Swift app
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
show_progress "Building Swift ScreenBlocker app..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "This may take a minute..."
./build_swift_app.sh > /dev/null 2>&1
if [ -d "ScreenBlocker.app" ]; then
    echo -e "${GREEN} Swift app built successfully${NC}"
else
    echo -e "${RED}Error: Swift app build failed${NC}"
    echo "You can try building manually with: ./build_swift_app.sh"
fi
echo ""

# Step 8: Setup complete
echo ""
echo "╔═══════════════════════════════════════════════════╗"
echo "║                                                   ║"
echo "║              SETUP COMPLETE!                  ║"
echo "║                                                   ║"
echo "╚═══════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN} All components installed successfully!${NC}"
echo ""

# Summary of what was installed
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " Installed Components:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "   Homebrew"
echo "   Tesseract OCR"
echo "   Xcode Command Line Tools"
echo "   Python Virtual Environment"
echo "   Python Dependencies (OpenCV, WebSockets, etc.)"
echo "   ScreenBlocker.app"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  IMPORTANT: Grant Permissions"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Before running the app, grant Screen Recording permission:"
echo ""
echo "  ${YELLOW}System Settings → Privacy & Security → Screen Recording${NC}"
echo "  ${YELLOW}Enable 'ScreenBlocker' when it appears${NC}"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " To Start the Application:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  ${GREEN}./run.sh${NC}"
echo ""
echo "This will start the detection engine and open the app."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " Documentation:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Quick Start Guide:    QUICKSTART.md"
echo "  Full Documentation:   README.md"
echo "  Installation Guide:   INSTALL.md"
echo ""

