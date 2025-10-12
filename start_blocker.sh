#!/bin/bash
cd "$(dirname "$0")"
echo "Starting Screen Privacy Blocker - Live Detection..."
echo "This will capture your live screen and detect sensitive information in real-time."
echo "A GUI window will open showing the live screen and detection log."
python3 live_screen_blocker.py