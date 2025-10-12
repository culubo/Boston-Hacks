# Screen Privacy Blocker

A macOS application that captures your real screen and masks sensitive information during screen sharing to prevent accidental exposure of API keys, personal data, and confidential information.

## Security & Privacy

**ALL DATA PROCESSING IS LOCAL ONLY** - No data leaves your computer. The application:
- Processes all screen content locally on your machine
- Does not store sensitive information permanently
- Automatically clears detection logs after 24 hours
- Requires explicit user permission for screen recording access
- Implements secure memory management with automatic cleanup

## Features

- Real-time screen capture and analysis
- Detection of API keys, phone numbers, personal information
- Multi-language support for text recognition
- Native macOS overlay system for masking
- Configurable detection patterns
- Panic mode for instant full-screen masking
- Local-only processing (no cloud dependencies)

## Quick Start

1. **Install**: Run `./scripts/install.sh`
2. **Start**: Run `./start_blocker.sh`
3. **Grant Permissions**: Allow screen recording when prompted
4. **Protect**: Your screen is now protected during sharing!

## Installation

```bash
git clone https://github.com/culubo/Boston-Hacks.git
cd Boston-Hacks
git checkout screen-blocker-final
./scripts/install.sh
```

## Usage

### Basic Usage
1. Run the detection engine: `./start_blocker.sh`
2. Grant screen recording permission when prompted
3. Begin screen sharing - sensitive content will be automatically masked

### Panic Mode
- Press Ctrl+C to stop protection instantly
- Restart with `./start_blocker.sh` when ready

## Detection Patterns

The system detects:
- AWS Access Keys (AKIA...)
- GitHub Tokens (ghp_, gho_, ghs_...)
- Google API Keys (AIza...)
- Stripe Keys (sk_test_, sk_live_...)
- JWT Tokens
- Credit Card Numbers
- Phone Numbers
- Email Addresses
- Social Security Numbers
- Bitcoin Addresses
- Ethereum Addresses
- High-entropy strings (potential secrets)

## Permissions Required

- **SCREEN RECORDING**: Required to capture screen content for analysis
- **ACCESSIBILITY**: Required to create overlay windows for masking

## Team Member Integration

### Frontend Developer
Place your UI components in `frontend/` directory. The main app interface should integrate with the detection engine via the provided API endpoints.

### Overlay Developer  
Place your masking/overlay system in `overlay/` directory. The system expects a WebSocket connection to receive masking coordinates and labels.

## Development

See individual component READMEs for detailed development instructions:
- `src/detector/README.md` - Detection engine
- `macos_app/README.md` - Native macOS application
- `overlay/README.md` - Masking overlay system
- `frontend/README.md` - Frontend components

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
