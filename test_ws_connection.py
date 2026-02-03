#!/usr/bin/env python3
"""
Simple test to verify WebSocket server is reachable
Run this while main.py is running
"""

import asyncio
import sys

try:
    import websockets
except ImportError:
    print("ERROR: websockets library not installed")
    print("Run: pip3 install websockets")
    sys.exit(1)

async def test_connection():
    uri = "wss://localhost:8765"
    print(f"Testing connection to {uri}...")
    
    try:
        # Try to connect with SSL verification disabled for self-signed cert
        import ssl
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        async with websockets.connect(uri, ssl=ssl_context) as websocket:
            print("✓ Connected successfully!")
            print("Sending test message...")
            
            # Send authentication attempt
            await websocket.send('{"type":"authenticate","password":"test"}')
            
            # Wait for response
            response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
            print(f"✓ Received response: {response}")
            
    except asyncio.TimeoutError:
        print("⚠ Connected but no response (timeout)")
    except ConnectionRefusedError:
        print("✗ Connection refused - server not running on port 8765")
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("WebSocket Connection Test")
    print("-" * 60)
    asyncio.run(test_connection())
