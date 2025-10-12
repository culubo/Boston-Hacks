#!/usr/bin/env python3
"""
High-Quality Screen Privacy Blocker
Starts the Python WebSocket receiver and overlay server
"""

import subprocess
import sys
import os
import time
import signal
import threading
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        ('websockets', 'websockets'),
        ('opencv-python', 'cv2'),
        ('Pillow', 'PIL'),
        ('pytesseract', 'pytesseract'),
        ('numpy', 'numpy')
    ]
    
    missing = []
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
        except ImportError:
            missing.append(package_name)
    
    if missing:
        print(f"Missing dependencies: {', '.join(missing)}")
        print("Install with: pip3 install " + " ".join(missing))
        return False
    
    return True

def start_receiver():
    """Start the WebSocket receiver"""
    receiver_path = Path(__file__).parent / "src" / "detector" / "recv_ws.py"
    venv_python = Path(__file__).parent / "venv" / "bin" / "python"
    if venv_python.exists():
        return subprocess.Popen([str(venv_python), str(receiver_path)])
    else:
        return subprocess.Popen([sys.executable, str(receiver_path)])

def start_overlay_server():
    """Start the overlay WebSocket server"""
    overlay_path = Path(__file__).parent / "src" / "detector" / "overlay_server.py"
    venv_python = Path(__file__).parent / "venv" / "bin" / "python"
    if venv_python.exists():
        return subprocess.Popen([str(venv_python), str(overlay_path)])
    else:
        return subprocess.Popen([sys.executable, str(overlay_path)])

def main():
    """Main function"""
    print("High-Quality Screen Privacy Blocker")
    print("=" * 40)
    print()
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    print("Starting Python WebSocket services...")
    
    # Start receiver
    print("Starting WebSocket receiver on :7777...")
    receiver_proc = start_receiver()
    
    # Wait a moment for receiver to start
    time.sleep(1)
    
    # Start overlay server
    print("Starting overlay server on :8765...")
    overlay_proc = start_overlay_server()
    
    print()
    print("Python services started successfully!")
    print("Now you can run the Swift app to start high-quality capture.")
    print()
    print("To stop: Press Ctrl+C")
    print()
    
    def signal_handler(sig, frame):
        print("\nShutting down...")
        receiver_proc.terminate()
        overlay_proc.terminate()
        receiver_proc.wait()
        overlay_proc.wait()
        print("Shutdown complete.")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Keep running until interrupted
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if receiver_proc.poll() is not None:
                print("Receiver process died unexpectedly!")
                break
            if overlay_proc.poll() is not None:
                print("Overlay server process died unexpectedly!")
                break
                
    except KeyboardInterrupt:
        signal_handler(None, None)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
