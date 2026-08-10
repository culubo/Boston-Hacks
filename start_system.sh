#!/bin/bash
# Start the complete screen blocker system

cd "$(dirname "$0")"

echo "=================================="
echo "Screen Privacy Blocker System"
echo "=================================="
echo ""

# Kill any existing processes
echo "Cleaning up existing processes..."
killall python3 2>/dev/null || true
pkill -f "electron" 2>/dev/null || true
sleep 1

# Start Python servers
echo ""
echo "Starting Python detection servers..."

# Start overlay server (broadcasts detections on :8765)
echo "  - overlay_server.py (ws://127.0.0.1:8765)"
python3 src/detector/overlay_server.py &
OVERLAY_PID=$!
sleep 1

# Start frame receiver (receives frames on :7777, does detection)
echo "  - recv_ws.py (ws://127.0.0.1:7777)"
python3 src/detector/recv_ws.py &
RECV_PID=$!
sleep 2

# Start Electron overlay
echo ""
echo "Starting Electron overlay..."
cd electron-overlay

if [ ! -d "node_modules" ]; then
    echo "Installing Electron dependencies..."
    npm install
fi

npm start &
ELECTRON_PID=$!

cd ..

echo ""
echo "=================================="
echo "System Started!"
echo "=================================="
echo ""
echo "Components running:"
echo "  - Overlay Server PID: $OVERLAY_PID"
echo "  - Frame Receiver PID: $RECV_PID"
echo "  - Electron Overlay PID: $ELECTRON_PID"
echo ""
echo "Controls:"
echo "  - Cmd+Shift+P: Toggle panic mode"
echo "  - Ctrl+C: Stop all services"
echo ""
echo "IMPORTANT: Grant Screen Recording permission to Electron"
echo "  System Settings → Privacy & Security → Screen Recording"
echo ""
echo "Press Ctrl+C to stop all services..."

# Wait for Ctrl+C
trap "echo ''; echo 'Stopping all services...'; kill $OVERLAY_PID $RECV_PID $ELECTRON_PID 2>/dev/null; exit 0" INT
wait

