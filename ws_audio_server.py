#!/usr/bin/env python3
"""
WebSocket Audio Streaming Server for AudioPirate
Low-latency real-time audio streaming using WebSocket + Web Audio API
"""

import asyncio
import struct
import json
import hashlib
import time

try:
    import websockets
    from websockets.server import serve
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    print("Warning: websockets not available, WebSocket streaming disabled")

try:
    import alsaaudio
    ALSA_AVAILABLE = True
except ImportError:
    ALSA_AVAILABLE = False
    print("Warning: alsaaudio not available")


class AudioWebSocketServer:
    """WebSocket server for real-time audio streaming"""
    
    def __init__(self, port=8765, audio_device='mic_with_gain', password='audiopirate'):
        self.port = port
        self.audio_device = audio_device
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
        self.auth_tokens = {}  # token -> expiry
        self.server = None
        self.running = False
        
    async def authenticate(self, websocket, message):
        """Handle authentication request"""
        try:
            data = json.loads(message)
            password = data.get('password', '')
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            if password_hash == self.password_hash:
                # Generate token
                import secrets
                token = secrets.token_urlsafe(32)
                expiry = time.time() + (24 * 60 * 60)
                self.auth_tokens[token] = expiry
                
                await websocket.send(json.dumps({
                    'type': 'auth_success',
                    'token': token
                }))
                return True
            else:
                await websocket.send(json.dumps({
                    'type': 'auth_failed',
                    'message': 'Invalid password'
                }))
                return False
        except Exception as e:
            print(f"Authentication error: {e}")
            return False
    
    def check_token(self, token):
        """Verify authentication token"""
        if token in self.auth_tokens:
            if time.time() < self.auth_tokens[token]:
                return True
            else:
                del self.auth_tokens[token]
        return False
    
    async def stream_audio(self, websocket, token):
        """Stream audio to authenticated client"""
        if not ALSA_AVAILABLE:
            await websocket.send(json.dumps({
                'type': 'error',
                'message': 'ALSA not available'
            }))
            return
        
        # Try configured device first, fall back to hw:0,0
        device = self.audio_device
        try:
            pcm = alsaaudio.PCM(
                alsaaudio.PCM_CAPTURE,
                alsaaudio.PCM_NORMAL,
                device=device
            )
        except alsaaudio.ALSAAudioError:
            print(f"Device '{device}' not found, falling back to 'hw:0,0'")
            device = 'hw:0,0'
            pcm = alsaaudio.PCM(
                alsaaudio.PCM_CAPTURE,
                alsaaudio.PCM_NORMAL,
                device=device
            )
        
        # Configure audio
        pcm.setchannels(2)
        pcm.setrate(48000)
        pcm.setformat(alsaaudio.PCM_FORMAT_S32_LE)
        pcm.setperiodsize(1024)  # Smaller chunks for lower latency
        
        # Send audio config to client
        await websocket.send(json.dumps({
            'type': 'audio_config',
            'sampleRate': 48000,
            'channels': 2,
            'bitsPerSample': 32
        }))
        
        print(f"Started audio stream for client (device: {device})")
        chunk_count = 0
        
        try:
            while True:
                # Check if token is still valid
                if not self.check_token(token):
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'message': 'Token expired'
                    }))
                    break
                
                # Read audio data
                length, data = pcm.read()
                if length > 0:
                    # Send raw binary data
                    await websocket.send(data)
                    chunk_count += 1
                    
                    if chunk_count % 100 == 0:
                        print(f"Streamed {chunk_count} chunks ({len(data)} bytes/chunk)")
                
                # Small delay to prevent blocking
                await asyncio.sleep(0.001)
                
        except websockets.exceptions.ConnectionClosed:
            print(f"Client disconnected after {chunk_count} chunks")
        except Exception as e:
            print(f"Streaming error: {e}")
        finally:
            pcm.close()
    
    async def handler(self, websocket, path):
        """Handle WebSocket connections"""
        print(f"Client connected from {websocket.remote_address}")
        token = None
        
        try:
            async for message in websocket:
                # Check if it's binary (shouldn't receive binary from client)
                if isinstance(message, bytes):
                    continue
                
                # Parse JSON message
                try:
                    data = json.loads(message)
                    msg_type = data.get('type', '')
                    
                    if msg_type == 'authenticate':
                        if await self.authenticate(websocket, message):
                            # Authentication successful, wait for stream request
                            pass
                    
                    elif msg_type == 'start_stream':
                        token = data.get('token', '')
                        if self.check_token(token):
                            await self.stream_audio(websocket, token)
                        else:
                            await websocket.send(json.dumps({
                                'type': 'error',
                                'message': 'Invalid or expired token'
                            }))
                    
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'message': 'Invalid JSON'
                    }))
                    
        except Exception as e:
            print(f"Handler error: {e}")
    
    async def start(self):
        """Start the WebSocket server"""
        if not WEBSOCKETS_AVAILABLE:
            print("WebSocket streaming not available - websockets library not installed")
            print("Install with: pip install websockets")
            return
        
        self.running = True
        self.server = await serve(self.handler, "0.0.0.0", self.port)
        print(f"WebSocket server started on ws://0.0.0.0:{self.port}")
        print("Waiting for connections...")
        
        await asyncio.Future()  # Run forever
    
    def run(self):
        """Run the server (blocking)"""
        try:
            asyncio.run(self.start())
        except KeyboardInterrupt:
            print("\nShutting down WebSocket server...")


if __name__ == "__main__":
    server = AudioWebSocketServer(port=8765, password='audiopirate')
    server.run()
