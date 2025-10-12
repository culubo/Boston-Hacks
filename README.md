# ML-Only Screen Privacy Blocker

A macOS application that uses machine learning to detect and mask sensitive information during screen sharing. Uses ONLY the ML model from GitHub for detection, preventing accidental exposure of API keys, personal data, and confidential information.

## Security & Privacy

**ALL DATA PROCESSING IS LOCAL ONLY** - No data leaves your computer. The application:
- Processes all screen content locally on your machine
- Does not store sensitive information permanently
- Automatically clears detection logs after 24 hours
- Requires explicit user permission for screen recording access
- Implements secure memory management with automatic cleanup

## Features

- **ML-Only Detection**: Uses machine learning model from GitHub repository
- **Real-time screen capture**: High-quality 30 FPS capture with OCR text extraction
- **Accurate masking**: Blockers positioned over actual detected text using OCR coordinates
- **High-quality video**: Smooth, clear display without graininess
- **Local-only processing**: No cloud dependencies, all processing on your machine
- **Clean logging**: Each detection logged only once to avoid spam
- **OCR-based positioning**: Uses Tesseract for precise text location and masking

## Quick Start

1. **Install Dependencies**: `pip3 install --break-system-packages opencv-python Pillow pytesseract pandas scikit-learn`
2. **Start**: Run `./start_blocker.sh`
3. **Grant Permissions**: Allow screen recording when prompted
4. **Protect**: Your screen is now protected with ML detection!

## Installation

```bash
git clone https://github.com/culubo/Boston-Hacks.git
cd Boston-Hacks
git checkout screen-blocker-final
pip3 install --break-system-packages opencv-python Pillow pytesseract pandas scikit-learn
```

## Usage

### Basic Usage
1. Run the detection engine: `./start_blocker.sh`
2. Grant screen recording permission when prompted
3. Begin screen sharing - sensitive content will be automatically masked

### Panic Mode
- Press Ctrl+C to stop protection instantly
- Restart with `./start_blocker.sh` when ready

## ML Detection

The system uses a machine learning model to detect sensitive content including:
- API keys and tokens
- Personal information
- Financial data
- Credentials and passwords
- Confidential business information
- Any text classified as sensitive by the ML model

**Note**: This version uses ONLY the ML model from the GitHub repository for detection, providing more accurate and comprehensive sensitive content identification.

## Permissions Required

- **SCREEN RECORDING**: Required to capture screen content for analysis
- **ACCESSIBILITY**: Required to create overlay windows for masking

## Technical Details

### ML Model Integration
- Uses `predict_one.py` from the GitHub repository
- Requires `final_model.pkl`, `thresholds.json`, and `policy.json`
- Processes text extracted via OCR (Tesseract)
- Returns confidence scores and detection classifications

### Architecture
- **Screen Capture**: High-quality screencapture with 30 FPS
- **OCR Processing**: Tesseract for text extraction with bounding boxes
- **ML Detection**: GitHub ML model for sensitive content classification
- **Masking**: Black rectangles positioned over detected text coordinates
- **Display**: Tkinter GUI with live screen mirror and detection log

### Dependencies
- `opencv-python` - Image processing and video capture
- `Pillow` - Image manipulation
- `pytesseract` - OCR text extraction
- `pandas` - Data processing for ML model
- `scikit-learn` - Machine learning model support

## Troubleshooting

### Common Issues
1. **Permission Denied**: Grant screen recording permission in System Preferences > Security & Privacy
2. **No Detections**: Ensure the detection engine is running and has permissions
3. **High CPU Usage**: Reduce detection frequency in settings

### Logs
- Detection engine logs: Check terminal output
- macOS app logs: Console.app > ScreenBlocker

## Contributing

1. Create a feature branch: `git checkout -b feature-name`
2. Make your changes
3. Test thoroughly
4. Commit with lowercase messages: `git commit -m "add new feature"`
5. Push and create pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
