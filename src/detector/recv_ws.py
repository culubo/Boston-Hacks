import asyncio
import websockets
import io
import time
import json
import sys
import os
import numpy as np
import cv2
from PIL import Image

# Add src directory to path for pattern_detector import
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from detector.pattern_detector import PatternDetector

detector = PatternDetector()
last_gray = None
last_detections_ts = 0

def decode_jpeg_to_numpy(b: bytes) -> np.ndarray:
    """Convert JPEG bytes to numpy array"""
    img = Image.open(io.BytesIO(b)).convert("RGB")
    return np.array(img)

def significant_change(prev: np.ndarray, curr: np.ndarray, pix_threshold=20_000) -> bool:
    """Check if there's significant change between frames"""
    if prev is None: 
        return True
    diff = cv2.absdiff(prev, curr)
    nz = cv2.countNonZero(cv2.cvtColor(diff, cv2.COLOR_RGB2GRAY))
    return nz > pix_threshold

async def handle(conn):
    """Handle WebSocket connection from Swift"""
    global last_gray, last_detections_ts
    
    print("Swift capture connected")
    
    while True:
        try:
            msg = await conn.recv()
            if isinstance(msg, (bytes, bytearray)):
                frame = decode_jpeg_to_numpy(msg)
                gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

                # Skip processing if no significant change
                if not significant_change(last_gray, gray):
                    continue
                last_gray = gray

                # Fast text regions: use OpenCV MSER as a cheap filter before OCR
                boxes = []
                try:
                    mser = cv2.MSER_create(_min_area=60, _max_area=5000)
                    regions, _ = mser.detectRegions(gray)
                    for cnt in regions:
                        x, y, w, h = cv2.boundingRect(cnt)
                        if w * h < 500: 
                            continue
                        boxes.append((x, y, w, h))
                except Exception as e:
                    print(f"MSER error: {e}")
                    # Fallback: use simple contour detection
                    contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    for cnt in contours:
                        x, y, w, h = cv2.boundingRect(cnt)
                        if w * h > 500 and w > 20 and h > 10:
                            boxes.append((x, y, w, h))

                # Cheap ROI OCR using tesseract
                text_blobs = []
                for (x, y, w, h) in boxes[:50]:  # cap to avoid spikes
                    try:
                        roi = frame[y:y+h, x:x+w]
                        # Quick binary for tesseract
                        roi_g = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY)
                        roi_b = cv2.threshold(roi_g, 0, 255, cv2.THRESH_OTSU|cv2.THRESH_BINARY)[1]
                        
                        # Use pytesseract for OCR
                        import pytesseract
                        txt = pytesseract.image_to_string(roi_b, config='--oem 3 --psm 6').strip()
                        if txt and len(txt) > 2:
                            text_blobs.append((txt, (x, y, w, h)))
                    except Exception as e:
                        # Skip this ROI if OCR fails
                        continue

                # Run pattern detection on OCR'd text
                detections = []
                for txt, bb in text_blobs:
                    try:
                        for m in detector.detect_patterns(txt):
                            if m['confidence'] > 0.7:  # Only high confidence detections
                                detections.append({
                                    "text": m["text"], 
                                    "pattern_type": m["type"],
                                    "confidence": m["confidence"],
                                    "bounding_box": list(bb),
                                    "timestamp": time.time()
                                })
                    except Exception as e:
                        print(f"Pattern detection error: {e}")
                        continue

                # Send to overlay (same 8765 server you already have)
                if detections:
                    payload = {
                        "type": "detections",
                        "detections": detections
                    }
                    try:
                        async with websockets.connect("ws://127.0.0.1:8765") as ov:
                            await ov.send(json.dumps(payload))
                    except Exception as e:
                        print(f"Overlay send error: {e}")
                        
        except websockets.exceptions.ConnectionClosed:
            print("Swift capture disconnected")
            break
        except Exception as e:
            print(f"Connection error: {e}")
            await asyncio.sleep(1)

async def main():
    """Main WebSocket server"""
    print("Starting thumbnail WebSocket receiver on :7777")
    print("Waiting for Swift ScreenCaptureKit connection...")
    
    async with websockets.serve(handle, "127.0.0.1", 7777, max_size=4*1024*1024):
        print("WebSocket server running on ws://127.0.0.1:7777")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down WebSocket receiver...")
