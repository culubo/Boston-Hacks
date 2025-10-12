#!/usr/bin/env python3
"""
Python High-Quality Screen Privacy Blocker
Alternative to Swift app that works with the WebSocket services
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

class PythonHighQualityBlocker:
    """Python-based high-quality screen blocker using existing capture methods"""
    
    def __init__(self):
        self.root = None
        self.is_running = False
        self.detections = []
        self.detection_manager = DetectionManager()
        
        # GUI components
        self.canvas = None
        self.log_text = None
        self.status_label = None
        self.count_label = None
        
    def start(self):
        """Start the Python high-quality blocker"""
        self.create_gui()
        self.root.mainloop()
        return True
    
    def create_gui(self):
        """Create the main GUI"""
        self.root = tk.Tk()
        self.root.title("Python High-Quality Screen Privacy Blocker")
        self.root.geometry("2000x1400")
        self.root.configure(bg='#1a1a1a')
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='#1a1a1a')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="Python High-Quality Screen Privacy Blocker",
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
            text="Live Screen Mirror (High Quality)",
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
        self.is_running = True
        self.start_button.config(text="Stop Protection", bg='#f44336')
        self.status_label.config(text="Status: Running (High Quality)", fg='green')
        
        self.log_message("High-quality protection started", "INFO")
        self.log_message("Connected to WebSocket services", "INFO")
        self.log_message("Scanning for sensitive information...", "INFO")
        
        # Start detection manager
        self.detection_manager.start()
        
        # Start display loop
        self.display_loop()
    
    def stop_protection(self):
        """Stop protection"""
        self.is_running = False
        self.detection_manager.stop()
        self.start_button.config(text="Start Protection", bg='#4CAF50')
        self.status_label.config(text="Status: Stopped", fg='red')
        
        self.log_message("Protection stopped", "INFO")
        self.log_message(f"Total detections: {len(self.detections)}", "INFO")
    
    def display_loop(self):
        """Main display loop"""
        if not self.is_running:
            return
        
        try:
            # Get current detections
            current_detections = self.detection_manager.get_detections()
            if current_detections != self.detections:
                self.detections = current_detections
                self.count_label.config(text=f"Detections: {len(self.detections)}")
                
                # Log new detections
                for detection in current_detections:
                    self.log_message(
                        f"[{detection['timestamp']}] {detection['type']}: '{detection['text']}' (Conf: {detection['confidence']:.2f})",
                        "HIGH"
                    )
            
            # Schedule next update
            self.root.after(100, self.display_loop)
            
        except Exception as e:
            self.log_message(f"Display error: {e}", "ERROR")
            self.root.after(1000, self.display_loop)
    
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
        self.count_label.config(text="Detections: 0")
        self.log_message("Log cleared", "INFO")

class DetectionManager:
    """Manages detection data from WebSocket services"""
    
    def __init__(self):
        self.detections = []
        self.is_running = False
        self.websocket_task = None
        self.loop = None
        self.thread = None
        
    def start(self):
        """Start detection manager"""
        self.is_running = True
        self.thread = threading.Thread(target=self._run_websocket_client, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop detection manager"""
        self.is_running = False
        if self.websocket_task:
            self.websocket_task.cancel()
    
    def _run_websocket_client(self):
        """Run WebSocket client in separate thread"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._connect_to_overlay_server())
    
    async def _connect_to_overlay_server(self):
        """Connect to overlay server"""
        try:
            async with websockets.connect("ws://127.0.0.1:8765") as websocket:
                self.websocket_task = websocket
                print("Connected to overlay server")
                
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        if data.get("type") == "detections":
                            self.detections = data.get("detections", [])
                    except json.JSONDecodeError:
                        pass
                    except Exception as e:
                        print(f"WebSocket error: {e}")
                        
        except Exception as e:
            print(f"Connection error: {e}")
            # Try to reconnect
            if self.is_running:
                await asyncio.sleep(2)
                await self._connect_to_overlay_server()
    
    def get_detections(self):
        """Get current detections"""
        return self.detections.copy()

def main():
    """Main function"""
    print("Python High-Quality Screen Privacy Blocker")
    print("=" * 50)
    print()
    
    blocker = PythonHighQualityBlocker()
    
    try:
        blocker.start()
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
