const { app, BrowserWindow, screen, globalShortcut } = require('electron');
const path = require('path');

let overlayWindow = null;
let captureWindow = null;

function createOverlay() {
  const { width, height } = screen.getPrimaryDisplay().bounds;
  
  overlayWindow = new BrowserWindow({
    width,
    height,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    fullscreen: true,
    resizable: false,
    focusable: false,
    skipTaskbar: true,
    backgroundColor: '#00000000',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  overlayWindow.setIgnoreMouseEvents(true, { forward: true });
  overlayWindow.loadFile('overlay.html');
  
  // Keep overlay on top of everything
  overlayWindow.setAlwaysOnTop(true, 'screen-saver', 1);
  overlayWindow.setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: true });
}

function createCaptureWindow() {
  captureWindow = new BrowserWindow({
    width: 400,
    height: 300,
    show: false, // Hidden window for capture
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  captureWindow.loadFile('capture.html');
}

app.whenReady().then(() => {
  console.log('Starting Screen Blocker Overlay...');
  createOverlay();
  createCaptureWindow();

  // Register panic key (Cmd+Shift+P)
  globalShortcut.register('CommandOrControl+Shift+P', () => {
    console.log('Panic key pressed!');
    if (overlayWindow) {
      overlayWindow.webContents.send('panic-toggle');
    }
  });

  console.log('Overlay ready! Press Cmd+Shift+P to toggle panic mode');
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('will-quit', () => {
  globalShortcut.unregisterAll();
});

