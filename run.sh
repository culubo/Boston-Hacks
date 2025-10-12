#!/bin/bash

# Screen Privacy Blocker - Launcher
# This script starts all components with one command

set -e

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo ""
echo "╔═══════════════════════════════════════════════════╗"
echo "║   Screen Privacy Blocker                          ║"
echo "╚═══════════════════════════════════════════════════╝"
echo ""

# Check if setup has been run
if [ ! -d "venv" ]; then
    echo -e "${RED}Error: Virtual environment not found.${NC}"
    echo "Please run setup first: ./setup.sh"
    exit 1
fi

if [ ! -d "ScreenBlocker.app" ]; then
    echo -e "${RED}Error: ScreenBlocker.app not found.${NC}"
    echo "Please run setup first: ./setup.sh"
    exit 1
fi

echo "Starting Screen Privacy Blocker..."
echo ""

# Activate virtual environment
source venv/bin/activate

# Start the Python services in the background
echo -e "${GREEN}Starting detection engine...${NC}"
python3 start_high_quality_blocker.py &
PYTHON_PID=$!

# Wait for services to initialize
echo "Waiting for services to start..."
sleep 2

# Check if Python services are running
if ! ps -p $PYTHON_PID > /dev/null; then
    echo -e "${RED}Error: Failed to start Python services${NC}"
    exit 1
fi

echo -e "${GREEN}OK: Detection engine started${NC}"
echo ""

# Start the Swift app
echo -e "${GREEN}Starting ScreenBlocker app...${NC}"
open ScreenBlocker.app

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Application is running!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "If this is your first time running:"
echo "  1. Grant Screen Recording permission when prompted"
echo "  2. Go to: System Settings → Privacy & Security → Screen Recording"
echo "  3. Enable 'ScreenBlocker'"
echo "  4. Restart the app"
echo ""
echo "To stop the application:"
echo "  Press Ctrl+C or close the ScreenBlocker app"
echo ""

# Trap Ctrl+C to clean up
cleanup() {
    echo ""
    echo -e "${YELLOW}Stopping application...${NC}"
    kill $PYTHON_PID 2>/dev/null || true
    killall ScreenBlocker 2>/dev/null || true
    echo -e "${GREEN}Application stopped.${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Keep the script running and monitor the Python process
while true; do
    if ! ps -p $PYTHON_PID > /dev/null; then
        echo -e "${RED}Error: Python services stopped unexpectedly${NC}"
        break
    fi
    sleep 1
done

cleanup

