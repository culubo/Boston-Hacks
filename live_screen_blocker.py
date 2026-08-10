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

# Disable ML model to avoid false positives and version warnings
ML_MODEL_AVAILABLE = False
print("Using pattern detector only for better accuracy")

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
    """Live screen capture using macOS screencapture with high efficiency"""
    
    def __init__(self):
        self.is_capturing = False
        self.capture_thread = None
        self.current_frame = None
        self.frame_lock = threading.Lock()
        self.last_capture_time = 0
        self.capture_interval = 1/30  # 30 FPS but with smart skipping
        
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
        """Continuous screen capture loop with efficiency optimization"""
        while self.is_capturing:
            try:
                current_time = time.time()
                
                # Only capture if enough time has passed (30 FPS max)
                if current_time - self.last_capture_time >= self.capture_interval:
                    # Capture screen with highest quality settings
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
    """Detects sensitive information using both pattern detector and ML model from the repo"""
    
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
            'high_entropy': 'MEDIUM',
            'ml_detection': 'HIGH'  # ML model detections
        }
    
    def detect_in_image(self, image):
        """Detect sensitive information using both pattern detector and ML model"""
        if not TESSERACT_AVAILABLE:
            return []
        
        try:
            # Convert to grayscale for better OCR
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Use Tesseract to get bounding box data
            ocr_data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
            
            # Build full text for pattern detection
            full_text = " ".join([text for text in ocr_data['text'] if text.strip()])
            
            # Debug: Show what OCR is reading
            if full_text.strip():
                print(f"\n[OCR] Read {len(full_text)} chars from screen")
                print(f"[OCR] First 200 chars: {full_text[:200]}")
            
            detections = []
            
            # 1. Use pattern detector for known patterns (balanced confidence threshold)
            pattern_detections = self.pattern_detector.detect_patterns(full_text)
            print(f"[DETECT] Found {len(pattern_detections)} potential patterns")
            
            for detection in pattern_detections:
                # Only include confident detections to reduce false positives  
                print(f"[PATTERN] {detection['type']}: confidence={detection['confidence']:.2f}, text={detection['text'][:50]}")
                
                if detection['confidence'] >= 0.7:  # Lowered from 0.85 for testing
                    pattern_name = detection.get('pattern_name', 'unknown')
                    severity = self.severity_map.get(pattern_name, 'LOW')
                    detected_text = detection['text']
                    
                    # Skip if text is too short (likely false positive)
                    if len(detected_text.strip()) < 5:  # Lowered from 8
                        print(f"[SKIP] Too short: {detected_text}")
                        continue
                    
                    # Find bounding box for this detected text in OCR data
                    bbox = self._find_text_bbox(detected_text, ocr_data)
                    
                    if bbox:
                        detections.append({
                            'text': detected_text,
                            'type': detection['type'],
                            'confidence': detection['confidence'],
                            'severity': severity,
                            'start': detection['start'],
                            'end': detection['end'],
                            'pattern_name': pattern_name,
                            'timestamp': datetime.now().strftime('%H:%M:%S'),
                            'timestamp_epoch': time.time(),
                            'source': 'pattern_detector',
                            'bbox': bbox  # (x, y, w, h)
                        })
            
            # 2. ML model disabled to avoid false positives and version warnings
            
            return detections
            
        except Exception as e:
            print(f"OCR error: {e}")
            return []
    
    def _find_text_bbox(self, search_text, ocr_data):
        """Find bounding box for specific text in OCR data"""
        try:
            n_boxes = len(ocr_data['text'])
            search_text_lower = search_text.lower().strip()
            
            # Try to find exact match first
            for i in range(n_boxes):
                text = ocr_data['text'][i].strip()
                if text.lower() == search_text_lower:
                    x = ocr_data['left'][i]
                    y = ocr_data['top'][i]
                    w = ocr_data['width'][i]
                    h = ocr_data['height'][i]
                    return (x, y, w, h)
            
            # Try to find partial match by checking consecutive words
            words = search_text.split()
            if len(words) > 1:
                for i in range(n_boxes - len(words) + 1):
                    matched = True
                    for j, word in enumerate(words):
                        if ocr_data['text'][i + j].lower() != word.lower():
                            matched = False
                            break
                    
                    if matched:
                        # Calculate bounding box that encompasses all words
                        x_min = ocr_data['left'][i]
                        y_min = ocr_data['top'][i]
                        x_max = ocr_data['left'][i + len(words) - 1] + ocr_data['width'][i + len(words) - 1]
                        y_max = ocr_data['top'][i + len(words) - 1] + ocr_data['height'][i + len(words) - 1]
                        return (x_min, y_min, x_max - x_min, y_max - y_min)
            
            # If no exact match, try fuzzy match (contains)
            for i in range(n_boxes):
                text = ocr_data['text'][i].strip()
                if search_text_lower in text.lower() or text.lower() in search_text_lower:
                    x = ocr_data['left'][i]
                    y = ocr_data['top'][i]
                    w = ocr_data['width'][i]
                    h = ocr_data['height'][i]
                    # Add padding for better coverage
                    return (max(0, x - 5), max(0, y - 5), w + 10, h + 10)
            
            return None
            
        except Exception as e:
            print(f"Bbox search error: {e}")
            return None

class LiveScreenBlocker:
    """Main application with live screen capture and detection"""
    
    def __init__(self):
        self.root = None
        self.screen_capture = LiveScreenCapture()
        self.detector = SecurityDetector()
        self.is_running = False
        self.detection_count = 0
        self.detections_log = []
        self.masking_enabled = True
        self.last_detection_time = 0
        
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
        """Create the main GUI with bigger mirror screen"""
        self.root = tk.Tk()
        self.root.title("Screen Privacy Blocker - Live Detection")
        self.root.geometry("2000x1400")  # Even bigger window
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
            font=('Arial', 18, 'bold')
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
            font=('Arial', 14, 'bold'),
            padx=25,
            pady=8
        )
        self.start_button.pack(side=tk.LEFT, padx=(0, 15))
        
        # Status label
        self.status_label = tk.Label(
            control_frame,
            text="Status: Stopped",
            fg='red',
            bg='#1a1a1a',
            font=('Arial', 14)
        )
        self.status_label.pack(side=tk.LEFT, padx=(0, 25))
        
        # Detection count
        self.count_label = tk.Label(
            control_frame,
            text="Detections: 0",
            fg='yellow',
            bg='#1a1a1a',
            font=('Arial', 14)
        )
        self.count_label.pack(side=tk.LEFT, padx=(0, 25))
        
        # Masking toggle
        self.mask_button = tk.Button(
            control_frame,
            text="Disable Masking",
            command=self.toggle_masking,
            bg='#FF9800',
            fg='white',
            font=('Arial', 12),
            padx=15,
            pady=5
        )
        self.mask_button.pack(side=tk.LEFT)
        
        # Main content frame - horizontal layout with 60/40 split
        content_frame = tk.Frame(main_frame, bg='#1a1a1a')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights for 60/40 split
        content_frame.grid_columnconfigure(0, weight=6)  # 60% for screen
        content_frame.grid_columnconfigure(1, weight=4)  # 40% for log
        content_frame.grid_rowconfigure(0, weight=1)
        
        # Left panel - Live screen (60% of window)
        left_panel = tk.Frame(content_frame, bg='#2a2a2a', relief=tk.RAISED, bd=2)
        left_panel.grid(row=0, column=0, sticky='nsew', padx=(0, 5))
        
        # Title at top
        tk.Label(
            left_panel,
            text="Live Screen Mirror",
            fg='white',
            bg='#2a2a2a',
            font=('Arial', 18, 'bold')
        ).pack(pady=10)
        
        # Canvas for live screen - use pack to fill remaining space
        self.canvas = tk.Canvas(
            left_panel,
            bg='black',
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Bind resize event to update canvas
        self.canvas.bind('<Configure>', self.on_canvas_resize)
        
        # Force initial canvas sizing
        self.root.after(100, self.force_canvas_update)
        
        # Right panel - Detection log (40% of window)
        right_panel = tk.Frame(content_frame, bg='#2a2a2a', relief=tk.RAISED, bd=2)
        right_panel.grid(row=0, column=1, sticky='nsew', padx=(5, 0))
        
        tk.Label(
            right_panel,
            text="Security Detection Log",
            fg='white',
            bg='#2a2a2a',
            font=('Arial', 14, 'bold')
        ).pack(pady=10)
        
        # Log text area - smaller to fit 40% width
        self.log_text = scrolledtext.ScrolledText(
            right_panel,
            width=35,
            height=35,
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
    
    def toggle_masking(self):
        """Toggle masking on/off"""
        self.masking_enabled = not self.masking_enabled
        if self.masking_enabled:
            self.mask_button.config(text="Disable Masking", bg='#FF9800')
            self.log_message("Masking enabled", "INFO")
        else:
            self.mask_button.config(text="Enable Masking", bg='#4CAF50')
            self.log_message("Masking disabled", "INFO")
    
    def on_canvas_resize(self, event):
        """Handle canvas resize events"""
        # Force a redraw when canvas is resized
        if hasattr(self, 'canvas') and event.width > 1 and event.height > 1:
            # Get current frame and redraw
            frame = self.screen_capture.get_current_frame()
            if frame is not None:
                self.update_screen_display(frame)
    
    def force_canvas_update(self):
        """Force canvas to update its size and redraw"""
        if hasattr(self, 'canvas'):
            # Force the canvas to expand
            self.canvas.update_idletasks()
            self.root.update_idletasks()
            
            # Get the actual available space
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # If canvas is still too small, force it to expand
            if canvas_width < 100 or canvas_height < 100:
                # Force parent to update
                self.canvas.master.update_idletasks()
                self.canvas.update_idletasks()
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()
            
            # Get current frame and redraw
            frame = self.screen_capture.get_current_frame()
            if frame is not None:
                self.update_screen_display(frame)
    
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
        """Main detection loop with high efficiency"""
        if not self.is_running:
            return
        
        try:
            # Get current frame
            frame = self.screen_capture.get_current_frame()
            
            if frame is not None:
                # Update live screen display
                self.update_screen_display(frame)
                
                # Only run detection every 1 second for efficiency
                current_time = time.time()
                if current_time - self.last_detection_time >= 1.0:
                    # Detect sensitive information
                    detections = self.detector.detect_in_image(frame)
                    
                    if detections:
                        for detection in detections:
                            self.handle_detection(detection)
                    
                    self.last_detection_time = current_time
            
            # High frame rate for display (60 FPS)
            self.root.after(16, self.detection_loop)  # 60 FPS
            
        except Exception as e:
            self.log_message(f"Detection error: {e}", "ERROR")
            self.root.after(1000, self.detection_loop)
    
    def update_screen_display(self, frame):
        """Update the live screen display with masking and improved quality"""
        try:
            # Get actual canvas dimensions dynamically
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # Skip if canvas not ready yet
            if canvas_width <= 1 or canvas_height <= 1:
                return
            
            # Get frame dimensions
            height, width = frame.shape[:2]
            
            # Calculate scaling to maintain aspect ratio and fit container
            scale = min(canvas_width/width, canvas_height/height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            
            # Resize frame with highest quality interpolation
            resized = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
            
            # Apply sharpening filter for better quality
            kernel = np.array([[-1,-1,-1],
                             [-1, 9,-1],
                             [-1,-1,-1]])
            sharpened = cv2.filter2D(resized, -1, kernel)
            
            # Apply slight contrast enhancement
            lab = cv2.cvtColor(sharpened, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            l = clahe.apply(l)
            enhanced = cv2.merge([l, a, b])
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
            
            # Apply masks to sensitive areas if enabled
            if self.masking_enabled:
                masked_frame = self.apply_masks_to_frame(enhanced, scale)
            else:
                masked_frame = enhanced
            
            # Convert to PhotoImage with better quality
            rgb_image = cv2.cvtColor(masked_frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_image)
            
            # Resize PIL image to exact canvas size for crisp display
            final_image = pil_image.resize((canvas_width, canvas_height), Image.LANCZOS)
            photo = ImageTk.PhotoImage(final_image)
            
            # Update canvas - center the image
            self.canvas.delete("all")
            self.canvas.create_image(canvas_width//2, canvas_height//2, image=photo)
            self.canvas.image = photo  # Keep reference
            
        except Exception as e:
            print(f"Display update error: {e}")
    
    def apply_masks_to_frame(self, frame, scale):
        """Apply black masks to sensitive areas in the frame using actual bounding boxes"""
        try:
            # Get recent detections (last 2 seconds)
            current_time = time.time()
            recent_detections = [
                d for d in self.detections_log 
                if current_time - d.get('timestamp_epoch', 0) < 2.0 and 'bbox' in d
            ]
            
            if not recent_detections:
                return frame
            
            # Create a copy to avoid modifying original
            masked_frame = frame.copy()
            frame_height, frame_width = masked_frame.shape[:2]
            
            print(f"Applying {len(recent_detections)} masks to frame of size {frame_width}x{frame_height}")
            
            # For each recent detection, apply a mask at the actual location
            for i, detection in enumerate(recent_detections):
                bbox = detection.get('bbox')
                if not bbox or len(bbox) != 4:
                    print(f"  Detection {i}: Invalid bbox {bbox}")
                    continue
                
                # Get original bounding box coordinates
                x_orig, y_orig, w_orig, h_orig = bbox
                
                # Scale coordinates to match the resized frame
                x = int(x_orig * scale)
                y = int(y_orig * scale)
                w = int(w_orig * scale)
                h = int(h_orig * scale)
                
                print(f"  Detection {i}: Original bbox ({x_orig}, {y_orig}, {w_orig}, {h_orig}) -> Scaled ({x}, {y}, {w}, {h})")
                
                # Validate dimensions
                if w <= 0 or h <= 0:
                    print(f"  Detection {i}: Invalid dimensions, skipping")
                    continue
                
                # Ensure coordinates are within frame bounds
                x = max(0, min(x, frame_width - w))
                y = max(0, min(y, frame_height - h))
                
                # Clamp dimensions to fit within frame
                if x + w > frame_width:
                    w = frame_width - x
                if y + h > frame_height:
                    h = frame_height - y
                
                if w > 5 and h > 5:  # Only draw if big enough
                    print(f"  Detection {i}: Drawing mask at ({x}, {y}, {w}, {h})")
                    # Draw black rectangle mask
                    cv2.rectangle(masked_frame, (x, y), (x + w, y + h), (0, 0, 0), -1)
                    # Add white border
                    cv2.rectangle(masked_frame, (x, y), (x + w, y + h), (255, 255, 255), 2)
                    
                    # Add label above the box if there's space
                    label = detection['type'][:15]
                    font_scale = 0.4
                    thickness = 1
                    label_y = max(y - 5, 15)  # Place above box or at top
                    cv2.putText(masked_frame, label, (x + 2, label_y), 
                               cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 0, 0), thickness)
                else:
                    print(f"  Detection {i}: Too small to draw ({w}x{h})")
            
            return masked_frame
            
        except Exception as e:
            print(f"Masking error: {e}")
            import traceback
            traceback.print_exc()
            return frame
    
    def handle_detection(self, detection):
        """Handle a detected security trigger with deduplication"""
        # Check if this detection already exists in recent logs (last 5 seconds)
        current_time = time.time()
        detection_key = f"{detection['text']}_{detection['type']}"
        
        # Check for duplicates in recent detections
        for existing_detection in self.detections_log:
            if (current_time - existing_detection.get('timestamp_epoch', 0) < 5.0 and
                f"{existing_detection['text']}_{existing_detection['type']}" == detection_key):
                # This is a duplicate, skip logging but keep in detections_log for masking
                self.detections_log.append(detection)
                return
        
        # New unique detection
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