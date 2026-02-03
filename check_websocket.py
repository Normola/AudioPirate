#!/usr/bin/env python3
"""
Quick check if WebSocket server can start
Run this on the Pi to diagnose the issue
"""

import sys

print("Checking WebSocket server...")
print("-" * 60)

# Check websockets library
try:
    import websockets
    print(f"✓ websockets library installed (version {websockets.__version__})")
except ImportError:
    print("✗ websockets library NOT installed")
    print("\nFIX: Run on the Pi:")
    print("  pip3 install websockets")
    print("  # or")
    print("  sudo pip3 install websockets")
    sys.exit(1)

# Check SSL certificates
import os
cert_file = 'certs/cert.pem'
key_file = 'certs/key.pem'

if os.path.exists(cert_file) and os.path.exists(key_file):
    print(f"✓ SSL certificates found in certs/")
else:
    print(f"⚠ SSL certificates NOT found")
    print(f"  Expected: {cert_file} and {key_file}")
    print("  The web server should create these automatically")

# Try to start WebSocket server
print("\nTrying to start WebSocket server...")
try:
    from ws_audio_server import AudioWebSocketServer
    import asyncio
    import signal
    
    server = AudioWebSocketServer(port=8765, password='audiopirate', use_ssl=True)
    
    async def test_start():
        await server.start()
    
    print("Starting server (press Ctrl+C to stop)...")
    print("-" * 60)
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    def signal_handler(sig, frame):
        print("\n\nStopping server...")
        loop.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    loop.run_until_complete(test_start())
    
except Exception as e:
    print(f"\n✗ Error starting server: {e}")
    import traceback
    traceback.print_exc()
    print("\nThis is the error preventing the WebSocket server from starting.")
    sys.exit(1)
