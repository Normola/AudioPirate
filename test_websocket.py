#!/usr/bin/env python3
"""
Test WebSocket Server
Quick test to verify WebSocket server starts correctly
"""

import sys

# Test websockets import
try:
    import websockets
    print(f"✓ websockets library installed (version {websockets.__version__})")
except ImportError:
    print("✗ websockets library NOT installed")
    print("  Install with: pip install websockets")
    sys.exit(1)

# Test alsaaudio import
try:
    import alsaaudio
    print("✓ alsaaudio library installed")
except ImportError:
    print("⚠ alsaaudio library NOT installed (will use mock mode)")

# Test server startup
print("\nStarting WebSocket server test...")
from ws_audio_server import AudioWebSocketServer

server = AudioWebSocketServer(port=8765, password='audiopirate')
print("WebSocket server object created successfully")
print("\nTo test the server:")
print("1. Run this script: python test_websocket.py")
print("2. In another terminal: python -m websockets ws://localhost:8765")
print("\nStarting server (Ctrl+C to stop)...")

try:
    server.run()
except KeyboardInterrupt:
    print("\nServer stopped")
