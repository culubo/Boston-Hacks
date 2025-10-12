#!/bin/bash
cd "$(dirname "$0")"
echo "Starting macOS High-Quality Screen Privacy Blocker..."
echo "This will capture your live screen with zero-copy, high-fidelity capture and detect sensitive information in real-time."
echo "A GUI window will open showing the high-quality live screen and detection log."
python3 macos_high_quality_capture.py