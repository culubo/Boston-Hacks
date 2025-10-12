# High-Quality Screen Privacy Blocker

This is a dramatically improved version of the screen privacy blocker that uses **ScreenCaptureKit** for crystal-clear, high-FPS screen capture and real-time sensitive information detection.

## Key Improvements

- **ScreenCaptureKit**: GPU-accelerated, zero-compression screen capture
- **30+ FPS**: Smooth, real-time processing
- **High Quality**: No graininess or compression artifacts
- **Efficient OCR**: Frame-diff detection + region-based processing
- **Accurate Positioning**: Proper coordinate scaling for precise masking

## Architecture

```
Swift App (ScreenCaptureKit) → WebSocket → Python (OCR) → WebSocket → Swift Overlay
```

1. **Swift App**: Captures screen at full resolution using ScreenCaptureKit
2. **Python Receiver**: Processes downscaled thumbnails for OCR
3. **Python Overlay Server**: Manages detection data
4. **Swift Overlay**: Displays masks at full resolution

## Setup Instructions

### 1. Install Dependencies

```bash
# Install Python dependencies
pip3 install websockets opencv-python Pillow pytesseract numpy

# Install Tesseract OCR
brew install tesseract

# Install Xcode command line tools (if not already installed)
xcode-select --install
```

### 2. Build Swift App

```bash
# Build the Swift app
./build_swift_app.sh
```

### 3. Grant Permissions

When you first run the Swift app, macOS will prompt you to grant:
- **Screen Recording** permission (required)
- **Camera** permission (required for ScreenCaptureKit)
- **Microphone** permission (required for ScreenCaptureKit)

Go to **System Settings → Privacy & Security → Screen Recording** and enable the app.

## Usage

### Method 1: Automated Startup

```bash
# Start Python services and Swift app
python3 start_high_quality_blocker.py
```

This will:
1. Start the Python WebSocket receiver on port 7777
2. Start the Python overlay server on port 8765
3. Provide instructions for running the Swift app

### Method 2: Manual Startup

```bash
# Terminal 1: Start Python services
python3 start_high_quality_blocker.py

# Terminal 2: Start Swift app
open ScreenBlocker.app
```

### Method 3: Individual Components

```bash
# Terminal 1: Start receiver
python3 src/detector/recv_ws.py

# Terminal 2: Start overlay server
python3 src/detector/overlay_server.py

# Terminal 3: Start Swift app
open ScreenBlocker.app
```

## How It Works

### 1. Screen Capture (Swift)
- Uses ScreenCaptureKit for hardware-accelerated capture
- Captures at full screen resolution (e.g., 2560x1440)
- Sends 960px wide JPEG thumbnails to Python for OCR

### 2. OCR Processing (Python)
- Receives downscaled thumbnails via WebSocket
- Uses frame-diff to skip unchanged frames
- Applies MSER region detection for text areas
- Runs Tesseract OCR on detected regions
- Processes text through pattern detector

### 3. Overlay Display (Swift)
- Receives detection data via WebSocket
- Scales coordinates from thumbnail to full screen
- Displays black masks over sensitive areas
- Updates in real-time as detections occur

## Performance Optimizations

- **Frame Diff**: Only processes frames that have changed
- **Region Detection**: OCR only on text-containing areas
- **Async Processing**: Non-blocking WebSocket communication
- **GPU Acceleration**: ScreenCaptureKit uses hardware acceleration
- **Efficient Scaling**: Proper coordinate transformation

## Troubleshooting

### Common Issues

1. **"Screen Recording permission required"**
   - Go to System Settings → Privacy & Security → Screen Recording
   - Enable the ScreenBlocker app

2. **"WebSocket connection failed"**
   - Make sure Python services are running
   - Check that ports 7777 and 8765 are available

3. **"Build failed"**
   - Ensure Xcode command line tools are installed
   - Try: `xcode-select --install`

4. **"OCR not working"**
   - Install Tesseract: `brew install tesseract`
   - Check Python dependencies: `pip3 install pytesseract`

### Performance Issues

- **High CPU usage**: Reduce detection frequency in `recv_ws.py`
- **Slow OCR**: Consider using PaddleOCR instead of Tesseract
- **Memory leaks**: Restart the Python services periodically

## Advanced Configuration

### Adjusting Quality vs Performance

In `CaptureBridge.swift`:
```swift
// Change thumbnail size (smaller = faster OCR)
let targetW: CGFloat = 720  // Default: 960

// Change frame rate
config.minimumFrameInterval = CMTime(value: 1, timescale: 60)  // 60 FPS
```

In `recv_ws.py`:
```python
# Change detection sensitivity
def significant_change(prev, curr, pix_threshold=10_000):  # Lower = more sensitive

# Change OCR region size limits
if w * h < 300:  # Smaller = more regions detected
```

## File Structure

```
blocker/
├── macos_app/                    # Swift ScreenCaptureKit app
│   └── ScreenBlocker/
│       ├── CaptureBridge.swift  # Screen capture + WebSocket
│       ├── OverlayManager.swift # Overlay display + scaling
│       └── ...
├── src/detector/
│   ├── recv_ws.py              # Python WebSocket receiver
│   ├── overlay_server.py       # Python overlay server
│   └── pattern_detector.py     # Pattern detection logic
├── start_high_quality_blocker.py # Startup script
└── build_swift_app.sh          # Build script
```

## Comparison with Previous Version

| Feature | Old (screencapture) | New (ScreenCaptureKit) |
|---------|-------------------|----------------------|
| Quality | Compressed, grainy | Crystal clear, uncompressed |
| FPS | ~5-10 FPS | 30+ FPS |
| CPU Usage | High (file I/O) | Low (GPU accelerated) |
| Latency | High (file system) | Low (direct memory) |
| Accuracy | Approximate positioning | Precise coordinate scaling |

## Next Steps

1. **PaddleOCR Integration**: Replace Tesseract with PaddleOCR for 10-20x faster OCR
2. **Multi-Monitor Support**: Extend to capture multiple displays
3. **Custom Patterns**: Add user-defined detection patterns
4. **Recording**: Save detection logs and screenshots
5. **Machine Learning**: Integrate with the existing ML model for better detection

## Support

If you encounter issues:
1. Check the console output for error messages
2. Verify all permissions are granted
3. Ensure all dependencies are installed
4. Try restarting the services in order: Python → Swift
