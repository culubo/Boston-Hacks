# Screen Privacy Blocker

**Protect your sensitive information during screen sharing with ML-powered real-time detection.**

A macOS application that uses machine learning and OCR to automatically detect and block sensitive information (API keys, passwords, personal data, etc.) when sharing your screen.

---

## Quick Start (3 Steps)

### 1. Clone the Repository
```bash
git clone https://github.com/culubo/Boston-Hacks.git
cd Boston-Hacks
git checkout screen-blocker-final
```

### 2. Run Setup (One Command)
```bash
chmod +x setup.sh
./setup.sh
```

This automatically installs:
- Homebrew (if needed)
- Tesseract OCR
- Python dependencies
- Xcode Command Line Tools
- Builds the Swift app

### 3. Start the Application
```bash
chmod +x run.sh
./run.sh
```

**First time only:** Grant Screen Recording permission when prompted:
1. Go to **System Settings →Privacy & Security →Screen Recording**
2. Enable **ScreenBlocker**
3. Restart the app with `./run.sh`

---

## What It Does

- **Real-time Detection**: Continuously scans your screen at 30 FPS
- **ML-Powered**: Uses machine learning to identify sensitive content
- **Instant Blocking**: Automatically covers detected sensitive information with black boxes
- **100% Local**: All processing happens on your machine - no data leaves your computer
- **Zero Configuration**: Works out of the box after setup

### What Gets Blocked

- API keys and tokens
- Passwords and credentials
- Credit card numbers
- Email addresses
- Phone numbers
- Social security numbers
- Any text classified as sensitive by the ML model

---

## Requirements

- **macOS 10.15+** (Catalina or later)
- **Python 3.8+**
- **Xcode Command Line Tools**
- **4GB RAM minimum** (8GB recommended)

> The setup script will check and install all requirements automatically.

---

## Usage

### Start the Blocker
```bash
./run.sh
```

### Stop the Blocker
- Press `Ctrl+C` in the terminal, or
- Close the ScreenBlocker app window

### Testing It Out
1. Start the blocker with `./run.sh`
2. Open a text editor or browser
3. Type something like: `API_KEY=sk_test_1234567890abcdef`
4. Watch it get automatically blocked with a black box overlay

---

## Architecture

The application uses a dual-component architecture:

```
┌─────────────────────┐ ┌──────────────────────┐
│ Swift App │ │ Python Engine │
│ (ScreenCaptureKit) │◄──────►│ (OCR + ML Model) │
│ │ WebSocket│ │
│ - Screen Capture │ │ - Text Detection │
│ - Overlay Display │ │ - ML Classification │
└─────────────────────┘ └──────────────────────┘
```

1. **Swift App** captures screen at high quality (30+ FPS)
2. **Python Engine** processes frames with OCR and ML model
3. **Swift App** receives detection coordinates and displays overlays

---

## Advanced Configuration

### Adjust Detection Sensitivity

Edit `src/detector/recv_ws.py`:
```python
# Make detection more sensitive (detects smaller changes)
def significant_change(prev, curr, pix_threshold=5_000): # Default: 10_000
```

### Change Capture Quality

Edit `macos_app/ScreenBlocker/CaptureBridge.swift`:
```swift
// Increase resolution for better OCR (may use more CPU)
let targetW: CGFloat = 1280 // Default: 960
```

### Adjust Frame Rate

Edit `macos_app/ScreenBlocker/CaptureBridge.swift`:
```swift
// Higher FPS for smoother capture
config.minimumFrameInterval = CMTime(value: 1, timescale: 60) // 60 FPS
```

---

## Troubleshooting

### "Permission Denied" or Black Screen
**Solution:** Grant Screen Recording permission
1. Go to **System Settings →Privacy & Security →Screen Recording**
2. Enable **ScreenBlocker**
3. Restart the app

### "Command not found: xcodebuild"
**Solution:** Install Xcode Command Line Tools
```bash
xcode-select --install
```

### "WebSocket connection failed"
**Solution:** Ensure Python services are running
```bash
# Restart the app
./run.sh
```

### High CPU Usage
**Solution:** Reduce capture frequency or resolution (see Advanced Configuration)

### App Won't Build
**Solution:** Clean build and retry
```bash
rm -rf ScreenBlocker.app
./setup.sh
```

---

## Project Structure

```
blocker/
├── setup.sh # One-command setup script
├── run.sh # Launch application
├── requirements.txt # Python dependencies
│
├── macos_app/ # Swift ScreenCaptureKit app
│ └── ScreenBlocker/
│ ├── CaptureBridge.swift # Screen capture
│ ├── OverlayManager.swift # Overlay display
│ ├── DetectionManager.swift # WebSocket client
│ └── ...
│
├── src/detector/ # Python detection engine
│ ├── recv_ws.py # WebSocket receiver + OCR
│ ├── overlay_server.py # Detection data server
│ └── pattern_detector.py # Pattern matching
│
└── Backend/ML Model/ # Machine learning model
 ├── final_model.pkl # Trained ML model
 ├── predict_one.py # Prediction interface
 ├── features.py # Feature extraction
 ├── thresholds.json # Detection thresholds
 └── policy.json # Detection policies
```

---

## Privacy & Security

**Your privacy is our priority:**

- **100% Local Processing** - No data sent to external servers
- **No Data Storage** - Sensitive content is never saved to disk
- **Temporary Memory Only** - Detection data cleared immediately after use
- **Open Source** - Fully transparent, auditable code
- **No Analytics** - We don't track or log your usage

---

## Contributing

We welcome contributions! Here's how:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test thoroughly
5. Commit: `git commit -m "add new feature"`
6. Push: `git push origin feature-name`
7. Open a Pull Request

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## Support

Having trouble? Here are your options:

1. **Check the [Troubleshooting](#troubleshooting) section** above
2. **Open an issue** on GitHub with:
 - Your macOS version
 - Error messages or logs
 - Steps to reproduce the problem
3. **Review the logs** in the terminal where you ran `./run.sh`

---

## Features Roadmap

- [ ] Multi-monitor support
- [ ] Custom detection patterns
- [ ] Configurable blocking styles (blur, pixelate, etc.)
- [ ] Detection history and logs
- [ ] Whitelist/blacklist for specific applications
- [ ] Browser extension integration

---

## Performance

- **Frame Rate**: 30+ FPS
- **Detection Latency**: < 100ms
- **CPU Usage**: 15-25% (depends on screen content)
- **RAM Usage**: ~200-300 MB
- **GPU Accelerated**: Yes (via ScreenCaptureKit)

---

**Made for privacy-conscious developers**

*Protect your secrets. Share with confidence.*
