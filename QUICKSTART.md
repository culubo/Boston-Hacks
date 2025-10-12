# Quick Start Guide

Get up and running in 3 minutes!

---

## Step 1: Clone & Navigate
```bash
git clone https://github.com/culubo/Boston-Hacks.git
cd Boston-Hacks
git checkout screen-blocker-final
```

---

## Step 2: Run Setup
```bash
./setup.sh
```

**What this does:**
- Checks for Python 3
- Installs Homebrew (if needed)
- Installs Tesseract OCR
- Installs Xcode Command Line Tools
- Creates Python virtual environment
- Installs all Python packages
- Builds the Swift ScreenBlocker app

**Time:** ~2-5 minutes (depending on what's already installed)

---

## Step 3: Grant Permissions

When you first run the app, macOS will ask for permissions.

### How to Grant Screen Recording Permission:

1. **System Settings** →**Privacy & Security**
2. Scroll down to **Screen Recording**
3. Find **ScreenBlocker** in the list
4. Toggle it **ON** 

![Permission Location](https://support.apple.com/library/content/dam/edam/applecare/images/en_US/macos/Big-Sur/macos-big-sur-system-preferences-security-privacy-screen-recording.jpg)

---

## Step 4: Start the App
```bash
./run.sh
```

**What this does:**
- Starts the Python detection engine (WebSocket services)
- Opens the ScreenBlocker app
- Begins monitoring your screen

---

## You're Protected!

The app is now running and will automatically detect and block sensitive information.

### Test it:
1. Open a text editor
2. Type: `API_KEY=sk_test_1234567890`
3. Watch it get blocked! 

---

## To Stop the App

Press `Ctrl+C` in the terminal, or close the ScreenBlocker app window.

---

## Having Issues?

### "Permission Denied"
→Make sure you granted Screen Recording permission (see Step 3)

### "Command not found"
→Run `./setup.sh` again

### "Build failed"
→Make sure Xcode Command Line Tools are installed:
```bash
xcode-select --install
```

### Still stuck?
→Check the full [README.md](README.md) or open a GitHub issue

---

## Learn More

- **Full Documentation**: [README.md](README.md)
- **Advanced Config**: See "Advanced Configuration" in README
- **Architecture Details**: See "Architecture" section in README

---

**That's it! You're all set up.** 

Share your screen with confidence knowing your sensitive data is protected.

