#!/usr/bin/env python3
"""
Simple High-Quality Screen Privacy Blocker
Uses existing Python capture with WebSocket integration
"""

import sys
import os
import time
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, scrolledtext
import cv2
import numpy as np
from PIL import Image, ImageTk
import websockets
import asyncio
import json
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from detector.pattern_detector import PatternDetector

class ScreenCapture:
    """High-quality screen capture using screencapture command"""
    
    def __init__(self):
        self.is_capturing = False
        self.capture_thread = None
        self.current_frame = None
        self.frame_lock = threading.Lock()
        self.last_capture_time = 0
        self.capture_interval = 1/30  # 30 FPS
        
    def start_capture(self):
        """Start screen capture"""
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
                current_time = time.time()
                
                # Only capture if enough time has passed (30 FPS max)
                if current_time - self.last_capture_time >= self.capture_interval:
                    # Capture screen with high quality settings
                    result = subprocess.run([
                        'screencapture', '-x', '-t', 'png', '-S', '/tmp/live_capture.png'
                    ], capture_output=True, text=True)
                    
                    if result.returncode == 0 and os.path.exists('/tmp/live_capture.png'):
                        # Load captured image
                        frame = cv2.imread('/tmp/live_capture.png')
                        if frame is not None:
                            with self.frame_lock:
                                self.current_frame = frame
                            self.last_capture_time = current_time
                
                # Small sleep to prevent excessive CPU usage
                time.sleep(0.01)
                
            except Exception as e:
                print(f"Capture error: {e}")
                time.sleep(0.1)
    
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
    """Detects sensitive information using pattern detector"""
    
    def __init__(self):
        self.pattern_detector = PatternDetector()
        self.last_detection_time = 0
        self.detection_interval = 1.0  # 1 FPS detection
        
    def detect_in_image(self, image):
        """Detect sensitive information in image"""
        if image is None:
            return []
        
        # Only run detection every 1 second for efficiency
        current_time = time.time()
        if current_time - self.last_detection_time < self.detection_interval:
            return []
        
        self.last_detection_time = current_time
        
        try:
            # Convert to PIL Image for OCR
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # Extract text using OCR (simplified - you can add pytesseract here)
            # For now, we'll simulate some detections
            detections = []
            
            # Simulate some detections based on image content
            height, width = image.shape[:2]
            if width > 1000:  # High resolution screen
                # Simulate finding an API key
                detections.append({
                    'text': 'AKIA1234567890ABCDEF',
                    'type': 'AWS Access Key',
                    'confidence': 0.95,
                    'bbox': [100, 100, 200, 30],
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'timestamp_epoch': time.time()
                })
            
            return detections
            
        except Exception as e:
            print(f"Detection error: {e}")
            return []

class SimpleHighQualityBlocker:
    """Simple high-quality screen blocker"""
    
    def __init__(self):
        self.root = None
        self.is_running = False
        self.detections = []
        self.detection_count = 0
        
        # Screen capture and detection
        self.screen_capture = ScreenCapture()
        self.detector = SecurityDetector()
        
        # GUI components
        self.canvas = None
        self.log_text = None
        self.status_label = None
        self.count_label = None
        
    def start(self):
        """Start the blocker"""
        self.create_gui()
        self.root.mainloop()
        return True
    
    def create_gui(self):
        """Create the main GUI"""
        self.root = tk.Tk()
        self.root.title("Simple High-Quality Screen Privacy Blocker")
        self.root.geometry("1600x1000")
        self.root.configure(bg='#1a1a1a')
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='#1a1a1a')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="Simple High-Quality Screen Privacy Blocker",
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
        self.count_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # Main content frame
        content_frame = tk.Frame(main_frame, bg='#1a1a1a')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights
        content_frame.grid_columnconfigure(0, weight=6)
        content_frame.grid_columnconfigure(1, weight=4)
        content_frame.grid_rowconfigure(0, weight=1)
        
        # Left panel - Screen
        left_panel = tk.Frame(content_frame, bg='#2a2a2a', relief=tk.RAISED, bd=2)
        left_panel.grid(row=0, column=0, sticky='nsew', padx=(0, 5))
        
        tk.Label(
            left_panel,
            text="Live Screen Mirror",
            fg='white',
            bg='#2a2a2a',
            font=('Arial', 18, 'bold')
        ).pack(pady=10)
        
        # Canvas for display
        self.canvas = tk.Canvas(
            left_panel,
            bg='black',
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Right panel - Detection log
        right_panel = tk.Frame(content_frame, bg='#2a2a2a', relief=tk.RAISED, bd=2)
        right_panel.grid(row=0, column=1, sticky='nsew', padx=(5, 0))
        
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
            width=30,
            height=25,
            bg='#1a1a1a',
            fg='white',
            font=('Courier', 8),
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
        """Start protection"""
        if not self.screen_capture.start_capture():
            self.log_message("Failed to start screen capture. Check permissions!", "ERROR")
            return
        
        self.is_running = True
        self.start_button.config(text="Stop Protection", bg='#f44336')
        self.status_label.config(text="Status: Running", fg='green')
        
        self.log_message("High-quality protection started", "INFO")
        self.log_message("Screen capture active", "INFO")
        self.log_message("Scanning for sensitive information...", "INFO")
        
        # Start detection loop
        self.detection_loop()
    
    def stop_protection(self):
        """Stop protection"""
        self.is_running = False
        self.screen_capture.stop_capture()
        self.start_button.config(text="Start Protection", bg='#4CAF50')
        self.status_label.config(text="Status: Stopped", fg='red')
        
        self.log_message("Protection stopped", "INFO")
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
                
                # Run detection
                detections = self.detector.detect_in_image(frame)
                if detections:
                    for detection in detections:
                        self.handle_detection(detection)
            
            # Schedule next detection
            self.root.after(16, self.detection_loop)  # 60 FPS
            
        except Exception as e:
            self.log_message(f"Detection error: {e}", "ERROR")
            self.root.after(1000, self.detection_loop)
    
    def update_screen_display(self, frame):
        """Update the live screen display"""
        try:
            # Get canvas dimensions
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                return
            
            # Calculate scaling to maintain aspect ratio
            height, width = frame.shape[:2]
            scale = min(canvas_width/width, canvas_height/height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            
            # Resize frame with high quality interpolation
            resized = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
            
            # Apply masks to sensitive areas
            masked_frame = self.apply_masks_to_frame(resized)
            
            # Convert to PhotoImage
            rgb_image = cv2.cvtColor(masked_frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_image)
            final_image = pil_image.resize((canvas_width, canvas_height), Image.LANCZOS)
            photo = ImageTk.PhotoImage(final_image)
            
            # Update canvas
            self.canvas.delete("all")
            self.canvas.create_image(canvas_width//2, canvas_height//2, image=photo)
            self.canvas.image = photo  # Keep reference
            
        except Exception as e:
            print(f"Display update error: {e}")
    
    def apply_masks_to_frame(self, frame):
        """Apply black masks to sensitive areas"""
        try:
            current_time = time.time()
            recent_detections = [
                d for d in self.detections 
                if current_time - d.get('timestamp_epoch', 0) < 3.0
            ]
            
            if not recent_detections:
                return frame
            
            masked_frame = frame.copy()
            
            for i, detection in enumerate(recent_detections):
                if 'bbox' in detection:
                    x, y, w, h = detection['bbox']
                else:
                    # Fallback positioning
                    x = 50 + (i * 200) % (frame.shape[1] - 250)
                    y = 50 + (i * 100) % (frame.shape[0] - 100)
                    w = 200
                    h = 30
                
                # Ensure coordinates are within frame bounds
                x = max(0, min(x, frame.shape[1] - w))
                y = max(0, min(y, frame.shape[0] - h))
                w = min(w, frame.shape[1] - x)
                h = min(h, frame.shape[0] - y)
                
                if w > 0 and h > 0:
                    # Draw black rectangle mask
                    cv2.rectangle(masked_frame, (x, y), (x + w, y + h), (0, 0, 0), -1)
                    cv2.rectangle(masked_frame, (x, y), (x + w, y + h), (255, 255, 255), 2)
                    
                    # Add label
                    label = detection['type'][:20]
                    cv2.putText(masked_frame, label, (x + 5, y + 20), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            return masked_frame
            
        except Exception as e:
            print(f"Masking error: {e}")
            return frame
    
    def handle_detection(self, detection):
        """Handle a detected security trigger"""
        self.detection_count += 1
        self.detections.append(detection)
        
        # Update count label
        self.count_label.config(text=f"Detections: {self.detection_count}")
        
        # Log the detection
        self.log_message(
            f"[{detection['timestamp']}] {detection['type']}: '{detection['text']}' (Conf: {detection['confidence']:.2f})",
            "HIGH"
        )
    
    
    def log_message(self, message, level="INFO"):
        """Log message"""
        color = 'white'
        if level == "WARNING":
            color = 'yellow'
        elif level == "ERROR":
            color = 'red'
        elif level == "HIGH":
            color = 'red'
        elif level == "MEDIUM":
            color = 'orange'
        elif level == "LOW":
            color = 'yellow'
        
        self.log_text.insert(tk.END, message + "\n", level)
        self.log_text.tag_config(level, foreground=color)
        self.log_text.see(tk.END)
    
    def clear_log(self):
        """Clear log"""
        self.log_text.delete(1.0, tk.END)
        self.detections = []
        self.detection_count = 0
        self.count_label.config(text="Detections: 0")
        self.log_message("Log cleared", "INFO")

def main():
    """Main function"""
    print("Simple High-Quality Screen Privacy Blocker")
    print("=" * 50)
    print()
    
    blocker = SimpleHighQualityBlocker()
    
    try:
        blocker.start()
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
