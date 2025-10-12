#!/usr/bin/env python3
"""
Overlay WebSocket Server for Screen Privacy Blocker
Receives detections from recv_ws.py and serves them to Swift overlay
"""

import asyncio
import websockets
import json
import time
from typing import Dict, List, Any

class OverlayServer:
    def __init__(self):
        self.connected_clients = set()
        self.current_detections = []
        self.last_update = 0
        
    async def register_client(self, websocket):
        """Register a new client connection"""
        self.connected_clients.add(websocket)
        print(f"Client connected. Total clients: {len(self.connected_clients)}")
        
        # Send current detections to new client
        if self.current_detections:
            await websocket.send(json.dumps({
                "type": "detections",
                "detections": self.current_detections
            }))
    
    async def unregister_client(self, websocket):
        """Unregister a client connection"""
        self.connected_clients.discard(websocket)
        print(f"Client disconnected. Total clients: {len(self.connected_clients)}")
    
    async def handle_detection_update(self, websocket):
        """Handle detection updates from recv_ws.py"""
        await self.register_client(websocket)
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    if data.get("type") == "detections":
                        self.current_detections = data.get("detections", [])
                        self.last_update = time.time()
                        
                        # Broadcast to all connected clients
                        if self.connected_clients:
                            message = json.dumps(data)
                            await asyncio.gather(
                                *[client.send(message) for client in self.connected_clients],
                                return_exceptions=True
                            )
                            
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                except Exception as e:
                    print(f"Message handling error: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister_client(websocket)
    
    async def cleanup_old_detections(self):
        """Clean up old detections periodically"""
        while True:
            await asyncio.sleep(5)  # Clean up every 5 seconds
            current_time = time.time()
            
            # Remove detections older than 10 seconds
            self.current_detections = [
                det for det in self.current_detections 
                if current_time - det.get('timestamp', 0) < 10.0
            ]

async def main():
    """Start the overlay WebSocket server"""
    server = OverlayServer()
    
    # Start cleanup task
    cleanup_task = asyncio.create_task(server.cleanup_old_detections())
    
    print("Starting overlay WebSocket server on :8765")
    print("Waiting for connections...")
    
    try:
        async with websockets.serve(server.handle_detection_update, "127.0.0.1", 8765):
            print("Overlay server running on ws://127.0.0.1:8765")
            await asyncio.Future()  # Run forever
    except KeyboardInterrupt:
        print("Shutting down overlay server...")
    finally:
        cleanup_task.cancel()

if __name__ == "__main__":
    asyncio.run(main())
