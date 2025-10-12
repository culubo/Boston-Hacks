#!/usr/bin/env python3
"""
macOS Improved Screen Capture - Fixed version with better video quality and proper blocker tracking
"""

import sys
import os
import time
import threading
import subprocess
import cv2
import numpy as np
from datetime import datetime
from typing import List, Dict, Tuple, Optional

# Import detection modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from detector.pattern_detector import PatternDetector

# Disable ML model for now to focus on pattern detection
ML_MODEL_AVAILABLE = False
print("Using pattern detector only for better performance")

try:
    import tkinter as tk
    from tkinter import ttk, scrolledtext
    from PIL import Image, ImageTk
    import pytesseract
    TKINTER_AVAILABLE = True
    print("GUI components available")
except ImportError as e:
    print(f"GUI not available: {e}")
    TKINTER_AVAILABLE = False

class ImprovedScreenCapture:
    """Improved screen capture with better quality and OCR-based positioning"""
    
    def __init__(self):
        self.is_capturing = False
        self.capture_thread = None
        self.current_frame = None
        self.frame_lock = threading.Lock()
        self.frame_callback = None
        self.last_capture_time = 0
        self.capture_interval = 1/30  # 30 FPS for better quality
        
    def start_capture(self):
        """Start improved screen capture"""
        if not self.check_permissions():
            return False
            
        self.is_capturing = True
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        return True
    
    def check_permissions(self):
        """Check screen recording permissions"""
        try:
            # Test screencapture
            result = subprocess.run(['screencapture', '-x', '-t', 'png', '/tmp/test_capture.png'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and os.path.exists('/tmp/test_capture.png'):
                os.remove('/tmp/test_capture.png')
                return True
            return False
        except Exception:
            return False
    
    def _capture_loop(self):
        """High-quality capture loop"""
        while self.is_capturing:
            try:
                current_time = time.time()
                
                # Only capture if enough time has passed
                if current_time - self.last_capture_time >= self.capture_interval:
                    # Use high-quality screencapture settings
                    result = subprocess.run([
                        'screencapture', 
                        '-x',  # No sound
                        '-t', 'png',  # PNG format for quality
                        '-S',  # Capture screen (not window)
                        '/tmp/improved_capture.png'
                    ], capture_output=True, text=True, timeout=2)
                    
                    if result.returncode == 0 and os.path.exists('/tmp/improved_capture.png'):
                        # Load with OpenCV
                        frame = cv2.imread('/tmp/improved_capture.png')
                        if frame is not None:
                            # Apply gentle quality enhancement
                            enhanced_frame = self._enhance_frame(frame)
                            
                            with self.frame_lock:
                                self.current_frame = enhanced_frame
                            
                            if self.frame_callback:
                                self.frame_callback(enhanced_frame)
                            
                            self.last_capture_time = current_time
                
                time.sleep(0.01)  # Small delay to prevent excessive CPU usage
                
            except Exception as e:
                print(f"Capture error: {e}")
                time.sleep(0.1)
    
    def _enhance_frame(self, frame):
        """Apply gentle enhancement to improve quality without graininess"""
        try:
            # Convert to float for processing
            enhanced = frame.astype(np.float32) / 255.0
            
            # Gentle sharpening (much lighter than before)
            kernel = np.array([[0, -0.1, 0],
                             [-0.1, 1.4, -0.1],
                             [0, -0.1, 0]])
            enhanced = cv2.filter2D(enhanced, -1, kernel)
            
            # Gentle contrast enhancement
            enhanced = np.clip(enhanced * 1.05, 0, 1)  # Slight brightness boost
            
            # Convert back to uint8
            enhanced = (enhanced * 255).astype(np.uint8)
            
            return enhanced
            
        except Exception as e:
            print(f"Enhancement error: {e}")
            return frame
    
    def stop_capture(self):
        """Stop screen capture"""
        self.is_capturing = False
        if self.capture_thread:
            self.capture_thread.join(timeout=1)
    
    def get_current_frame(self):
        """Get current frame"""
        with self.frame_lock:
            return self.current_frame.copy() if self.current_frame is not None else None
    
    def set_frame_callback(self, callback):
        """Set frame callback"""
        self.frame_callback = callback

class ImprovedSecurityDetector:
    """Improved security detector with OCR-based positioning"""
    
    def __init__(self):
        self.pattern_detector = PatternDetector()
        self.last_detection_time = 0
        self.detection_interval = 0.5  # 2 FPS detection
        self.detection_count = 0
        
    def detect_in_image(self, frame):
        """Detect sensitive information with OCR positioning"""
        if frame is None:
            return []
        
        # Only run detection every 0.5 seconds
        current_time = time.time()
        if current_time - self.last_detection_time < self.detection_interval:
            return []
        
        self.last_detection_time = current_time
        
        try:
            # Preprocess for OCR
            processed_frame = self._preprocess_for_ocr(frame)
            
            # Get OCR data with bounding boxes
            ocr_data = pytesseract.image_to_data(
                processed_frame, 
                output_type=pytesseract.Output.DICT,
                config='--oem 3 --psm 6'
            )
            
            detections = []
            
            # Process each detected text element
            for i in range(len(ocr_data['text'])):
                text = ocr_data['text'][i].strip()
                if len(text) < 3:  # Skip very short text
                    continue
                
                # Get bounding box
                x = ocr_data['left'][i]
                y = ocr_data['top'][i]
                w = ocr_data['width'][i]
                h = ocr_data['height'][i]
                conf = ocr_data['conf'][i]
                
                # Skip low confidence text
                if conf < 30:
                    continue
                
                # Check for sensitive patterns
                pattern_detections = self.pattern_detector.detect_patterns(text)
                
                for detection in pattern_detections:
                    if detection['confidence'] > 0.7:  # Only high confidence detections
                        detections.append({
                            'text': detection['text'],
                            'type': detection['type'],
                            'confidence': detection['confidence'],
                            'severity': 'HIGH' if detection['confidence'] > 0.8 else 'MEDIUM',
                            'bbox': (x, y, w, h),  # Actual bounding box
                            'timestamp': datetime.now().strftime('%H:%M:%S'),
                            'timestamp_epoch': time.time(),
                            'source': 'pattern_detector'
                        })
                        self.detection_count += 1
                
                # ML model detection (if available and not too frequent)
                if ML_MODEL_AVAILABLE and len(text) > 10 and self.detection_count % 10 == 0:
                    try:
                        ml_result = predict_text(text)
                        if ml_result['prediction'] == 1 and ml_result['probability'] > 0.8:
                            detections.append({
                                'text': text[:50] + ('...' if len(text) > 50 else ''),
                                'type': 'ML Detected Sensitive Content',
                                'confidence': ml_result['probability'],
                                'severity': 'HIGH',
                                'bbox': (x, y, w, h),
                                'timestamp': datetime.now().strftime('%H:%M:%S'),
                                'timestamp_epoch': time.time(),
                                'source': 'ml_model'
                            })
                            self.detection_count += 1
                    except Exception as ml_error:
                        # Only log ML errors occasionally to avoid spam
                        if self.detection_count % 50 == 0:
                            print(f"ML model error: {ml_error}")
            
            return detections
            
        except Exception as e:
            print(f"Detection error: {e}")
            return []
    
    def _preprocess_for_ocr(self, frame):
        """Preprocess frame for better OCR"""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Apply gentle sharpening
            kernel = np.array([[0, -0.2, 0],
                             [-0.2, 1.8, -0.2],
                             [0, -0.2, 0]])
            sharpened = cv2.filter2D(gray, -1, kernel)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                sharpened, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            return thresh
            
        except Exception as e:
            print(f"OCR preprocessing error: {e}")
            return frame

class ImprovedScreenBlocker:
    """Main application with improved quality and tracking"""
    
    def __init__(self):
        self.root = None
        self.capture = ImprovedScreenCapture()
        self.detector = ImprovedSecurityDetector()
        self.is_running = False
        self.detections_log = []
        self.masking_enabled = True
        
        # GUI components
        self.canvas = None
        self.log_text = None
        self.status_label = None
        self.count_label = None
        
    def start(self):
        """Start the improved blocker application"""
        if not TKINTER_AVAILABLE:
            print("Error: tkinter not available")
            return False
        
        self.create_gui()
        self.root.mainloop()
        return True
    
    def create_gui(self):
        """Create the main GUI"""
        self.root = tk.Tk()
        self.root.title("Improved Screen Privacy Blocker")
        self.root.geometry("2000x1400")
        self.root.configure(bg='#1a1a1a')
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='#1a1a1a')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="Improved Screen Privacy Blocker",
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
    
    def start_protection(self):
        """Start protection"""
        if not self.capture.start_capture():
            self.log_message("Failed to start screen capture. Check permissions!", "ERROR")
            return
        
        self.is_running = True
        self.start_button.config(text="Stop Protection", bg='#f44336')
        self.status_label.config(text="Status: Running", fg='green')
        
        self.log_message("Improved screen capture started", "INFO")
        self.log_message("Using OCR-based positioning for accurate blockers", "INFO")
        self.log_message("Scanning for sensitive information...", "INFO")
        
        # Set up frame callback
        self.capture.set_frame_callback(self.process_frame)
        
        # Start detection loop
        self.detection_loop()
    
    def stop_protection(self):
        """Stop protection"""
        self.is_running = False
        self.capture.stop_capture()
        self.start_button.config(text="Start Protection", bg='#4CAF50')
        self.status_label.config(text="Status: Stopped", fg='red')
        
        self.log_message("Protection stopped", "INFO")
        self.log_message(f"Total detections: {len(self.detections_log)}", "INFO")
    
    def process_frame(self, frame):
        """Process frame in real-time"""
        if frame is not None:
            self.update_display(frame)
    
    def detection_loop(self):
        """Main detection loop"""
        if not self.is_running:
            return
        
        try:
            frame = self.capture.get_current_frame()
            if frame is not None:
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
    
    def update_display(self, frame):
        """Update display with improved quality"""
        try:
            # Get canvas dimensions
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                return
            
            # Calculate scaling
            height, width = frame.shape[:2]
            scale = min(canvas_width/width, canvas_height/height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            
            # Resize with high quality
            resized = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
            
            # Apply masks if enabled
            if self.masking_enabled:
                masked_frame = self.apply_masks(resized, scale)
            else:
                masked_frame = resized
            
            # Convert to PhotoImage
            rgb_image = cv2.cvtColor(masked_frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_image)
            final_image = pil_image.resize((canvas_width, canvas_height), Image.LANCZOS)
            photo = ImageTk.PhotoImage(final_image)
            
            # Update canvas
            self.canvas.delete("all")
            self.canvas.create_image(canvas_width//2, canvas_height//2, image=photo)
            self.canvas.image = photo
            
        except Exception as e:
            print(f"Display update error: {e}")
    
    def apply_masks(self, frame, scale):
        """Apply masks using actual OCR bounding boxes"""
        try:
            current_time = time.time()
            recent_detections = [
                d for d in self.detections_log 
                if current_time - d.get('timestamp_epoch', 0) < 3.0
            ]
            
            if not recent_detections:
                return frame
            
            masked_frame = frame.copy()
            
            for detection in recent_detections:
                if 'bbox' in detection:
                    # Use actual OCR bounding box
                    x, y, w, h = detection['bbox']
                    
                    # Scale coordinates to match resized frame
                    x = int(x * scale)
                    y = int(y * scale)
                    w = int(w * scale)
                    h = int(h * scale)
                    
                    # Ensure bounds
                    x = max(0, min(x, frame.shape[1] - w))
                    y = max(0, min(y, frame.shape[0] - h))
                    w = min(w, frame.shape[1] - x)
                    h = min(h, frame.shape[0] - y)
                    
                    if w > 0 and h > 0:
                        # Draw mask
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
        """Handle detection (only log once per unique detection)"""
        # Check if we already logged this detection recently
        current_time = time.time()
        recent_similar = [
            d for d in self.detections_log 
            if (current_time - d.get('timestamp_epoch', 0) < 5.0 and 
                d.get('text') == detection['text'] and 
                d.get('type') == detection['type'])
        ]
        
        if not recent_similar:  # Only log if not recently logged
            self.detections_log.append(detection)
            self.log_message(
                f"[{detection['timestamp']}] {detection['severity']}: {detection['type']} - '{detection['text']}' (Conf: {detection['confidence']:.2f})",
                detection['severity']
            )
            self.count_label.config(text=f"Detections: {len(self.detections_log)}")
    
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
        self.detections_log = []
        self.count_label.config(text="Detections: 0")
        self.log_message("Log cleared", "INFO")

if __name__ == "__main__":
    print("Improved Screen Privacy Blocker")
    print("===============================")
    
    blocker = ImprovedScreenBlocker()
    blocker.start()
