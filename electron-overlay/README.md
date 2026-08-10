# Electron Overlay for Screen Blocker

This Electron app replaces the Swift components and provides:
- **Transparent full-screen overlay** - draws detection boxes directly on your screen
- **Screen capture** - sends frames to Python detection server
- **WebSocket integration** - connects to existing Python backend

## Architecture

```
┌─────────────────┐
│ Electron Capture│ ──JPEG frames──> ws://127.0.0.1:7777 (recv_ws.py)
└─────────────────┘                           │
                                              │ OCR + Pattern Detection
                                              ▼
┌─────────────────┐                   ┌──────────────┐
│ Electron Overlay│ <──detections──── │overlay_server│
│  (transparent)  │                   │   :8765      │
└─────────────────┘                   └──────────────┘
```

## Setup

```bash
cd electron-overlay
npm install
```

## Run

### Option 1: Use the main startup script (recommended)
```bash
cd ..
chmod +x start_system.sh
./start_system.sh
```

This starts:
1. Python overlay server (ws://127.0.0.1:8765)
2. Python frame receiver (ws://127.0.0.1:7777)
3. Electron overlay

### Option 2: Manual start
```bash
# Terminal 1: Python servers
python3 ../src/detector/overlay_server.py &
python3 ../src/detector/recv_ws.py &

# Terminal 2: Electron
npm start
```

## Permissions Required

**IMPORTANT:** macOS will ask for Screen Recording permission for Electron.
- Go to: **System Settings → Privacy & Security → Screen Recording**
- Enable **Electron** (or the app name)
- Restart the app

## Hotkeys

- **Cmd+Shift+P**: Toggle panic mode (full screen black overlay)

## How It Works

1. **capture.html**: Captures your screen using Electron's desktopCapturer, sends JPEG frames to Python
2. **overlay.html**: Transparent window that receives detection coordinates from Python and draws black boxes
3. **Python backend**: Receives frames, runs OCR + pattern detection, broadcasts results

## Development

```bash
npm run dev  # Start with inspector for debugging
```

## Troubleshooting

**"No detections appearing"**
- Check Python servers are running: `ps aux | grep python`
- Check WebSocket connections in browser console (Cmd+Option+I in overlay window)
- Verify ports 7777 and 8765 are not in use

**"Can't see overlay"**
- Check overlay window is always-on-top
- Try toggling panic mode (Cmd+Shift+P) to verify overlay is working

**"Permission denied"**
- Grant Screen Recording permission to Electron
- Restart app after granting permission

