# Installation Guide

Complete step-by-step installation guide for Screen Privacy Blocker.

---

## Prerequisites Check

Before installing, make sure you have:

- [ ] **macOS 10.15+** (Catalina or later)
- [ ] **4GB+ RAM** (8GB recommended)
- [ ] **Internet connection** (for downloading dependencies)
- [ ] **~500MB free disk space**

> Don't worry if you're missing some dependencies - the setup script will install them!

---

## Installation Methods

### Method 1: Automated Setup (Recommended) 

This is the easiest way to get started. One command does everything.

```bash
# 1. Clone the repository
git clone https://github.com/culubo/Boston-Hacks.git
cd Boston-Hacks
git checkout screen-blocker-final

# 2. Run the automated setup
./setup.sh
```

**What gets installed:**
- Homebrew (macOS package manager)
- Tesseract OCR (text recognition)
- Xcode Command Line Tools
- Python virtual environment
- All Python dependencies (opencv, websockets, etc.)
- Swift ScreenBlocker app (compiled and ready)

**Time required:** 3-7 minutes

---

### Method 2: Manual Setup

If you prefer to install components manually or already have some dependencies:

#### Step 1: Install Homebrew
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### Step 2: Install System Dependencies
```bash
brew install tesseract
xcode-select --install # If not already installed
```

#### Step 3: Setup Python Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Step 4: Build Swift App
```bash
./build_swift_app.sh
```

---

## Post-Installation Setup

### Grant Required Permissions

macOS requires explicit permission for screen recording:

1. **Start the app** for the first time:
 ```bash
 ./run.sh
 ```

2. **macOS will prompt** for Screen Recording permission

3. **Grant the permission:**
 - Open **System Settings**
 - Navigate to **Privacy & Security**
 - Click **Screen Recording**
 - Find **ScreenBlocker** in the list
 - Toggle it **ON** 

4. **Restart the app:**
 ```bash
 ./run.sh
 ```

### Visual Guide for Permissions

```
System Settings
 └── Privacy & Security
 └── Screen Recording
 └── [ ] ScreenBlocker <-- Enable this!
```

---

## Verification

After installation, verify everything works:

### 1. Check Python Dependencies
```bash
source venv/bin/activate
python3 -c "import cv2, websockets, pytesseract; print(' All dependencies OK')"
```

Expected output: ` All dependencies OK`

### 2. Check Tesseract
```bash
tesseract --version
```

Expected output: `tesseract 5.x.x`

### 3. Check Swift App
```bash
ls -la ScreenBlocker.app
```

Expected: Directory exists with app contents

### 4. Test Run
```bash
./run.sh
```

Expected: App starts, Python services run in background

---

## Troubleshooting Installation

### Problem: "Homebrew not found"

**Solution:**
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Problem: "xcodebuild: command not found"

**Solution:**
```bash
xcode-select --install
```
Follow the prompts to install Xcode Command Line Tools.

### Problem: "Permission denied" when running scripts

**Solution:**
```bash
chmod +x setup.sh run.sh build_swift_app.sh
```

### Problem: "Build failed" for Swift app

**Solution:**
```bash
# Clean and rebuild
rm -rf ScreenBlocker.app
rm -rf macos_app/build
./build_swift_app.sh
```

### Problem: Python package installation fails

**Solution:**
```bash
# Upgrade pip first
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Problem: "Tesseract not found" error

**Solution:**
```bash
# Install via Homebrew
brew install tesseract

# Verify installation
which tesseract
tesseract --version
```

---

## Installation Paths

After successful installation, here's where everything is:

```
/Users/culubo/Desktop/blocker/
├── venv/ # Python virtual environment
├── ScreenBlocker.app # Compiled Swift app
├── setup.sh # Setup script (can be deleted)
├── run.sh # Launcher script
└── [other project files]
```

---

## Updating

To update to the latest version:

```bash
# Pull latest changes
git pull origin screen-blocker-final

# Reinstall dependencies (if changed)
source venv/bin/activate
pip install -r requirements.txt

# Rebuild Swift app
./build_swift_app.sh
```

---

## Uninstalling

To completely remove the application:

```bash
# Remove the app and virtual environment
rm -rf ScreenBlocker.app venv

# Optional: Remove Homebrew packages
brew uninstall tesseract

# Optional: Remove Python packages
pip3 uninstall opencv-python pillow pytesseract numpy websockets pandas scikit-learn
```

To revoke screen recording permission:
1. System Settings →Privacy & Security →Screen Recording
2. Toggle off **ScreenBlocker**

---

## Next Steps

After successful installation:

1. **Read the [QUICKSTART.md](QUICKSTART.md)** - Get running in 3 minutes
2. **Read the [README.md](README.md)** - Learn about features and configuration
3. **Run the app** with `./run.sh`
4. **Test it out** by typing sensitive data and watching it get blocked

---

## Getting Help

If you're stuck:

1. **Check the [Troubleshooting](#troubleshooting-installation) section** above
2. **Check terminal output** for specific error messages
3. **Open an issue** on GitHub with:
 - Your macOS version (`sw_vers`)
 - Python version (`python3 --version`)
 - Full error message
 - What you tried

---

## System Requirements Summary

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| macOS | 10.15 (Catalina) | 12.0+ (Monterey) |
| RAM | 4 GB | 8 GB |
| CPU | Intel i5 / M1 | Intel i7 / M1 Pro+ |
| Disk Space | 500 MB | 1 GB |
| Python | 3.8 | 3.10+ |

---

**Installation complete? Time to protect your screen!** 

Run `./run.sh` to start the application.

