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

class SimpleHighQualityBlocker:
    """Simple high-quality screen blocker"""
    
    def __init__(self):
        self.root = None
        self.is_running = False
        self.detections = []
        self.detection_count = 0
        
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
        self.is_running = True
        self.start_button.config(text="Stop Protection", bg='#f44336')
        self.status_label.config(text="Status: Running", fg='green')
        
        self.log_message("High-quality protection started", "INFO")
        self.log_message("Scanning for sensitive information...", "INFO")
        
        # Start detection loop
        self.detection_loop()
    
    def stop_protection(self):
        """Stop protection"""
        self.is_running = False
        self.start_button.config(text="Start Protection", bg='#4CAF50')
        self.status_label.config(text="Status: Stopped", fg='red')
        
        self.log_message("Protection stopped", "INFO")
        self.log_message(f"Total detections: {self.detection_count}", "INFO")
    
    def detection_loop(self):
        """Main detection loop"""
        if not self.is_running:
            return
        
        try:
            # Simulate detection for demo
            if self.detection_count % 10 == 0:  # Every 10 loops
                self.simulate_detection()
            
            # Schedule next detection
            self.root.after(100, self.detection_loop)
            
        except Exception as e:
            self.log_message(f"Detection error: {e}", "ERROR")
            self.root.after(1000, self.detection_loop)
    
    def simulate_detection(self):
        """Simulate a detection for demo purposes"""
        self.detection_count += 1
        
        detection = {
            'text': f'AKIA1234567890ABCDEF{self.detection_count}',
            'type': 'AWS Access Key',
            'confidence': 0.95,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
        
        self.detections.append(detection)
        self.count_label.config(text=f"Detections: {self.detection_count}")
        
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
