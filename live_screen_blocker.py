#!/usr/bin/env python3
"""
Screen Privacy Blocker - Live Screen Capture with Real-time Detection
Captures live screen, detects sensitive information, and shows output in recorded tab
"""

import sys
import os
import re
import time
import threading
import subprocess
import json
from typing import List, Dict, Tuple
from datetime import datetime

# Add src to path to use existing pattern detector
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from detector.pattern_detector import PatternDetector

try:
    import tkinter as tk
    from tkinter import ttk, scrolledtext
    import cv2
    import numpy as np
    from PIL import Image, ImageTk
    import pytesseract
    TKINTER_AVAILABLE = True
    OPENCV_AVAILABLE = True
    TESSERACT_AVAILABLE = True
except ImportError as e:
    print(f"Missing dependencies: {e}")
    print("Install with: pip3 install opencv-python Pillow pytesseract")
    TKINTER_AVAILABLE = False
    OPENCV_AVAILABLE = False
    TESSERACT_AVAILABLE = False

class LiveScreenCapture:
    """Live screen capture using macOS screencapture"""
    
    def __init__(self):
        self.is_capturing = False
        self.capture_thread = None
        self.current_frame = None
        self.frame_lock = threading.Lock()
        
    def start_capture(self):
        """Start live screen capture"""
        if not self.check_permissions():
            return False
            
        self.is_capturing = True
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        return True
    
    def check_permissions(self):
        """Check screen recording permissions"""
        try:
            result = subprocess.run([
                'screencapture', '-x', '-R', '0,0,100,100', '/tmp/test_capture.png'
            ], capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def _capture_loop(self):
        """Continuous screen capture loop"""
        while self.is_capturing:
            try:
                # Capture screen
                result = subprocess.run([
                    'screencapture', '-x', '-t', 'png', '/tmp/live_capture.png'
                ], capture_output=True, text=True)
                
                if result.returncode == 0 and os.path.exists('/tmp/live_capture.png'):
                    # Load captured image
                    frame = cv2.imread('/tmp/live_capture.png')
                    if frame is not None:
                        with self.frame_lock:
                            self.current_frame = frame
                
                time.sleep(0.033)  # 30 FPS for smoother video-like experience
            except Exception as e:
                print(f"Capture error: {e}")
                time.sleep(1)
    
    def get_current_frame(self):
        """Get the current captured frame"""
        with self.frame_lock:
            return self.current_frame.copy() if self.current_frame is not None else None
    
    def stop_capture(self):
        """Stop screen capture"""
        self.is_capturing = False
        if self.capture_thread:
            self.capture_thread.join()

class SecurityDetector:
    """Detects sensitive information in screen content using existing pattern detector API"""
    
    def __init__(self):
        # Use the existing pattern detector from the git repo
        self.pattern_detector = PatternDetector()
        
        # Map pattern types to severity levels
        self.severity_map = {
            'aws_access_key': 'HIGH',
            'github_token': 'HIGH', 
            'google_api_key': 'HIGH',
            'stripe_key': 'HIGH',
            'jwt_token': 'MEDIUM',
            'credit_card': 'HIGH',
            'phone_number': 'MEDIUM',
            'email': 'LOW',
            'ssn': 'HIGH',
            'password': 'HIGH',
            'bitcoin_address': 'HIGH',
            'ethereum_address': 'HIGH',
            'api_key_generic': 'HIGH',
            'high_entropy': 'MEDIUM'
        }
    
    def detect_in_image(self, image):
        """Detect sensitive information in image using OCR and existing pattern detector API"""
        if not TESSERACT_AVAILABLE:
            return []
        
        try:
            # Convert to PIL Image
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # Extract text using OCR
            text = pytesseract.image_to_string(pil_image)
            
            # Use existing pattern detector API
            pattern_detections = self.pattern_detector.detect_patterns(text)
            
            # Convert to our format with severity mapping
            detections = []
            for detection in pattern_detections:
                pattern_name = detection.get('pattern_name', 'unknown')
                severity = self.severity_map.get(pattern_name, 'LOW')
                
                detections.append({
                    'text': detection['text'],
                    'type': detection['type'],
                    'confidence': detection['confidence'],
                    'severity': severity,
                    'start': detection['start'],
                    'end': detection['end'],
                    'pattern_name': pattern_name,
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                })
            
            return detections
            
        except Exception as e:
            print(f"OCR error: {e}")
            return []

class LiveScreenBlocker:
    """Main application with live screen capture and detection"""
    
    def __init__(self):
        self.root = None
        self.screen_capture = LiveScreenCapture()
        self.detector = SecurityDetector()
        self.is_running = False
        self.detection_count = 0
        self.detections_log = []
        
        # GUI components
        self.canvas = None
        self.log_text = None
        self.status_label = None
        self.count_label = None
        
    def start(self):
        """Start the live screen blocker application"""
        if not TKINTER_AVAILABLE:
            print("Error: tkinter not available. Install with: brew install python-tk")
            return False
        
        if not OPENCV_AVAILABLE:
            print("Error: OpenCV not available. Install with: pip3 install opencv-python")
            return False
        
        if not TESSERACT_AVAILABLE:
            print("Error: Tesseract not available. Install with: pip3 install pytesseract")
            return False
        
        self.create_gui()
        self.root.mainloop()
        return True
    
    def create_gui(self):
        """Create the main GUI"""
        self.root = tk.Tk()
        self.root.title("Screen Privacy Blocker - Live Detection")
        self.root.geometry("1600x1000")  # Bigger window
        self.root.configure(bg='#1a1a1a')
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='#1a1a1a')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="Screen Privacy Blocker - Live Detection",
            fg='white',
            bg='#1a1a1a',
            font=('Arial', 16, 'bold')
        )
        title_label.pack(pady=(0, 10))
        
        # Control frame
        control_frame = tk.Frame(main_frame, bg='#1a1a1a')
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Start/Stop button
        self.start_button = tk.Button(
            control_frame,
            text="Start Protection",
            command=self.toggle_protection,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=20,
            pady=5
        )
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Status label
        self.status_label = tk.Label(
            control_frame,
            text="Status: Stopped",
            fg='red',
            bg='#1a1a1a',
            font=('Arial', 12)
        )
        self.status_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # Detection count
        self.count_label = tk.Label(
            control_frame,
            text="Detections: 0",
            fg='yellow',
            bg='#1a1a1a',
            font=('Arial', 12)
        )
        self.count_label.pack(side=tk.LEFT)
        
        # Main content frame
        content_frame = tk.Frame(main_frame, bg='#1a1a1a')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Live screen
        left_panel = tk.Frame(content_frame, bg='#2a2a2a', relief=tk.RAISED, bd=2)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        tk.Label(
            left_panel,
            text="Live Screen Capture",
            fg='white',
            bg='#2a2a2a',
            font=('Arial', 14, 'bold')
        ).pack(pady=10)
        
        # Canvas for live screen - bigger size
        self.canvas = tk.Canvas(
            left_panel,
            width=800,  # Increased from 640
            height=600,  # Increased from 480
            bg='black',
            highlightthickness=0
        )
        self.canvas.pack(pady=10, padx=10)
        
        # Right panel - Detection log
        right_panel = tk.Frame(content_frame, bg='#2a2a2a', relief=tk.RAISED, bd=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        tk.Label(
            right_panel,
            text="Security Detection Log",
            fg='white',
            bg='#2a2a2a',
            font=('Arial', 14, 'bold')
        ).pack(pady=10)
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(
            right_panel,
            width=50,
            height=25,
            bg='#1a1a1a',
            fg='white',
            font=('Courier', 10),
            wrap=tk.WORD
        )
        self.log_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # Clear log button
        clear_button = tk.Button(
            right_panel,
            text="Clear Log",
            command=self.clear_log,
            bg='#f44336',
            fg='white',
            font=('Arial', 10)
        )
        clear_button.pack(pady=(0, 10))
    
    def toggle_protection(self):
        """Toggle protection on/off"""
        if not self.is_running:
            self.start_protection()
        else:
            self.stop_protection()
    
    def start_protection(self):
        """Start live protection"""
        if not self.screen_capture.start_capture():
            self.log_message("Failed to start screen capture. Check permissions!", "ERROR")
            return
        
        self.is_running = True
        self.start_button.config(text="Stop Protection", bg='#f44336')
        self.status_label.config(text="Status: Running", fg='green')
        
        self.log_message("Screen Privacy Blocker started", "INFO")
        self.log_message("Live screen capture active", "INFO")
        self.log_message("Scanning for sensitive information...", "INFO")
        
        # Start detection loop
        self.detection_loop()
    
    def stop_protection(self):
        """Stop live protection"""
        self.is_running = False
        self.screen_capture.stop_capture()
        self.start_button.config(text="Start Protection", bg='#4CAF50')
        self.status_label.config(text="Status: Stopped", fg='red')
        
        self.log_message("Screen Privacy Blocker stopped", "INFO")
        self.log_message(f"Total detections: {self.detection_count}", "INFO")
    
    def detection_loop(self):
        """Main detection loop"""
        if not self.is_running:
            return
        
        try:
            # Get current frame
            frame = self.screen_capture.get_current_frame()
            
            if frame is not None:
                # Update live screen display
                self.update_screen_display(frame)
                
                # Detect sensitive information
                detections = self.detector.detect_in_image(frame)
                
                if detections:
                    for detection in detections:
                        self.handle_detection(detection)
            
            # Schedule next detection - 30 FPS for smoother video-like experience
            self.root.after(33, self.detection_loop)  # 30 FPS
            
        except Exception as e:
            self.log_message(f"Detection error: {e}", "ERROR")
            self.root.after(1000, self.detection_loop)
    
    def update_screen_display(self, frame):
        """Update the live screen display"""
        try:
            # Resize frame to fit canvas - bigger canvas
            height, width = frame.shape[:2]
            canvas_width = 800  # Increased from 640
            canvas_height = 600  # Increased from 480
            
            # Calculate scaling
            scale = min(canvas_width/width, canvas_height/height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            
            # Resize frame
            resized = cv2.resize(frame, (new_width, new_height))
            
            # Convert to PhotoImage
            rgb_image = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_image)
            photo = ImageTk.PhotoImage(pil_image)
            
            # Update canvas
            self.canvas.delete("all")
            self.canvas.create_image(canvas_width//2, canvas_height//2, image=photo)
            self.canvas.image = photo  # Keep reference
            
        except Exception as e:
            print(f"Display update error: {e}")
    
    def handle_detection(self, detection):
        """Handle a detected security trigger"""
        self.detection_count += 1
        self.detections_log.append(detection)
        
        # Update count label
        self.count_label.config(text=f"Detections: {self.detection_count}")
        
        # Log the detection
        severity_color = {
            'HIGH': 'red',
            'MEDIUM': 'orange', 
            'LOW': 'yellow'
        }.get(detection['severity'], 'white')
        
        log_entry = f"[{detection['timestamp']}] {detection['severity']} - {detection['type']}\n"
        log_entry += f"  Text: {detection['text'][:50]}{'...' if len(detection['text']) > 50 else ''}\n"
        log_entry += f"  Confidence: {detection['confidence']:.2f}\n"
        log_entry += f"  Pattern: {detection['pattern_name']}\n"
        log_entry += "-" * 50 + "\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
        # Color code the severity
        start_line = self.log_text.index(tk.END + "-5l")
        end_line = self.log_text.index(tk.END + "-1l")
        self.log_text.tag_add(detection['severity'], start_line, end_line)
        self.log_text.tag_config(detection['severity'], foreground=severity_color)
    
    def log_message(self, message, level="INFO"):
        """Add a message to the log"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {level} - {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
        # Color code the level
        start_line = self.log_text.index(tk.END + "-1l")
        end_line = self.log_text.index(tk.END)
        self.log_text.tag_add(level, start_line, end_line)
        
        if level == "ERROR":
            self.log_text.tag_config(level, foreground='red')
        elif level == "INFO":
            self.log_text.tag_config(level, foreground='lightblue')
    
    def clear_log(self):
        """Clear the detection log"""
        self.log_text.delete(1.0, tk.END)
        self.detections_log = []
        self.log_message("Log cleared", "INFO")

def main():
    """Main function"""
    print("Screen Privacy Blocker - Live Screen Capture")
    print("=" * 50)
    print()
    
    if not TKINTER_AVAILABLE or not OPENCV_AVAILABLE or not TESSERACT_AVAILABLE:
        print("Missing dependencies. Install with:")
        print("  brew install python-tk")
        print("  pip3 install opencv-python Pillow pytesseract")
        return
    
    blocker = LiveScreenBlocker()
    
    try:
        blocker.start()
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
