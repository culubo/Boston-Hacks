# Setup Checklist

Use this checklist to ensure proper installation of Screen Privacy Blocker.

---

## Pre-Installation

- [ ] **macOS 10.15 or later** installed
- [ ] **4GB+ RAM** available (8GB recommended)
- [ ] **500MB+ disk space** available
- [ ] **Internet connection** active
- [ ] **Terminal** application ready

---

## Installation Steps

### Step 1: Clone Repository
```bash
git clone https://github.com/culubo/Boston-Hacks.git
cd Boston-Hacks
git checkout screen-blocker-final
```

- [ ] Repository cloned successfully
- [ ] In correct directory (`Boston-Hacks`)
- [ ] On `screen-blocker-final` branch

### Step 2: Run Setup Script
```bash
./setup.sh
```

- [ ] Script runs without errors
- [ ] Homebrew installed (or already present)
- [ ] Tesseract OCR installed
- [ ] Xcode Command Line Tools installed
- [ ] Python virtual environment created
- [ ] Python dependencies installed
- [ ] Swift app built successfully
- [ ] `ScreenBlocker.app` exists in directory

---

## Verify Installation

### Check Components

Run these commands to verify:

```bash
# Check Python
python3 --version
# Should show Python 3.8 or later

# Check Tesseract
tesseract --version
# Should show Tesseract 5.x.x

# Check virtual environment
ls -la venv
# Should show directory with bin/, lib/, etc.

# Check Swift app
ls -la ScreenBlocker.app
# Should show app bundle

# Check Python packages
source venv/bin/activate
python3 -c "import cv2, websockets, pytesseract, numpy; print(' All OK')"
# Should print: All OK
```

- [ ] Python 3.8+ installed
- [ ] Tesseract installed
- [ ] Virtual environment exists
- [ ] ScreenBlocker.app exists
- [ ] All Python packages import successfully

---

## Grant Permissions

### Screen Recording Permission

1. **Start the app:**
 ```bash
 ./run.sh
 ```

2. **When prompted, allow access**

3. **Open System Settings:**
 - Go to **System Settings**
 - Click **Privacy & Security**
 - Click **Screen Recording**

4. **Enable ScreenBlocker:**
 - [ ] Find "ScreenBlocker" in the list
 - [ ] Toggle switch to ON
 - [ ] Lock icon closed (if present)

5. **Restart the app:**
 ```bash
 ./run.sh
 ```

---

## Test the Application

### Basic Functionality Test

1. **Start the app:**
 - [ ] Run `./run.sh`
 - [ ] No error messages appear
 - [ ] Python services start
 - [ ] ScreenBlocker window appears

2. **Test detection:**
 - [ ] Open a text editor
 - [ ] Type: `API_KEY=sk_test_1234567890abcdef`
 - [ ] Black box appears over the text
 - [ ] Detection works in real-time

3. **Test performance:**
 - [ ] Screen capture is smooth (no lag)
 - [ ] CPU usage is reasonable (< 30%)
 - [ ] No excessive heat or fan noise

4. **Test shutdown:**
 - [ ] Press Ctrl+C in terminal
 - [ ] App closes cleanly
 - [ ] No error messages
 - [ ] No lingering processes

---

## Troubleshooting

If anything doesn't work, check these:

### Permission Issues
- [ ] Screen Recording permission granted in System Settings
- [ ] ScreenBlocker appears in the permission list
- [ ] Permission toggle is ON

### Build Issues
- [ ] Xcode Command Line Tools installed: `xcode-select --install`
- [ ] Run build manually: `./build_swift_app.sh`
- [ ] Check build output for errors

### Python Issues
- [ ] Virtual environment activated: `source venv/bin/activate`
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Python 3.8 or later: `python3 --version`

### Connection Issues
- [ ] Ports 7777 and 8765 not in use by other apps
- [ ] Firewall not blocking connections
- [ ] Python services running before starting Swift app

---

## Final Verification

All systems go! 

- [ ] Installation completed without errors
- [ ] All components installed and working
- [ ] Permissions granted correctly
- [ ] Test detection works
- [ ] App starts and stops cleanly
- [ ] Documentation reviewed

---

## You're All Set!

Your Screen Privacy Blocker is ready to use!

### Next Steps:

1. **Read the documentation:**
 - [README.md](README.md) - Full features and configuration
 - [QUICKSTART.md](QUICKSTART.md) - Quick reference guide

2. **Start using the app:**
 ```bash
 ./run.sh
 ```

3. **Report issues:**
 - If you encounter problems, open an issue on GitHub
 - Include your checklist status and error messages

---

## Installation Summary

| Component | Status |
|-----------|--------|
| Python 3.8+ | |
| Homebrew | |
| Tesseract OCR | |
| Xcode Tools | |
| Virtual Environment | |
| Python Packages | |
| Swift App | |
| Permissions | |
| Functionality Test | |

**Installation Date:** _______________

**Installation Time:** ~_____ minutes

**Notes:**
_________________________________
_________________________________
_________________________________

---

**Need help?** Check [INSTALL.md](INSTALL.md) or open an issue on GitHub.

