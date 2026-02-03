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
import ssl
import os

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
    
    def __init__(self, port=8765, audio_device='hw:0,0', password='audiopirate', use_ssl=True, cert_dir='certs', gain=3.0):
        self.port = port
        self.audio_device = audio_device
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
        self.auth_tokens = {}  # token -> expiry
        self.server = None
        self.running = False
        self.use_ssl = use_ssl
        self.cert_dir = cert_dir
        self.ssl_context = None
        self.gain = gain  # Software gain multiplier for ADAU7002 (start conservative)
        
        print(f"[WebSocket] Server initialized on port {port}")
        
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
        pcm.setperiodsize(2048)  # Match closer to browser buffer size for smooth playback
        
        # Send audio config to client
        await websocket.send(json.dumps({
            'type': 'audio_config',
            'sampleRate': 48000,
            'channels': 2,
            'bitsPerSample': 32
        }))
        
        print(f"Started audio stream for client (device: {device})")
        chunk_count = 0
        max_sample = 0
        
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
                    # Apply software gain boost (ADAU7002 has no hardware gain)
                    import struct
                    samples = struct.unpack(f'<{len(data)//4}i', data)
                    
                    # Amplify by configured gain with simple limiting
                    max_val = 2147483647
                    amplified = []
                    for s in samples:
                        amplified_sample = int(s * self.gain)
                        # Simple hard limit to prevent overflow
                        amplified_sample = max(-max_val, min(max_val, amplified_sample))
                        amplified.append(amplified_sample)
                    
                    data = struct.pack(f'<{len(amplified)}i', *amplified)
                    
                    # Send amplified binary data
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
    
    def _create_ssl_context(self):
        """Create SSL context for WSS connections"""
        # Try multiple certificate locations
        cert_locations = [
            ('certs/cert.pem', 'certs/key.pem'),  # Expected location
            ('audiopirate.crt', 'audiopirate.key'),  # Web server location
            ('cert.pem', 'key.pem'),  # Current directory
        ]
        
        cert_file = None
        key_file = None
        
        for cert, key in cert_locations:
            if os.path.exists(cert) and os.path.exists(key):
                cert_file = cert
                key_file = key
                print(f"[WebSocket] Found SSL certificates: {cert_file}")
                break
        
        if not cert_file:
            print(f"[WebSocket] SSL certificates not found in:")
            for cert, key in cert_locations:
                print(f"  - {cert} / {key}")
            return None
        
        try:
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ssl_context.load_cert_chain(cert_file, key_file)
            return ssl_context
        except Exception as e:
            print(f"[WebSocket] Error loading SSL certificates: {e}")
            return None
    
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
        try:
            # Setup SSL if enabled
            if self.use_ssl:
                self.ssl_context = self._create_ssl_context()
                if self.ssl_context:
                    print(f"[WebSocket] SSL/TLS enabled (wss://)")
                else:
                    print(f"[WebSocket] SSL certificates not found, falling back to ws://")
                    self.use_ssl = False
            
            # Start server
            self.server = await serve(
                self.handler, 
                "0.0.0.0", 
                self.port,
                ssl=self.ssl_context if self.use_ssl else None
            )
            
            protocol = "wss" if self.use_ssl else "ws"
            print(f"WebSocket server started on {protocol}://0.0.0.0:{self.port}")
            print("Waiting for connections...")
            
            await asyncio.Future()  # Run forever
        except Exception as e:
            print(f"WebSocket server error: {e}")
            import traceback
            traceback.print_exc()
    
    def run(self):
        """Run the server (blocking) - thread-safe"""
        if not WEBSOCKETS_AVAILABLE:
            print("[WebSocket] DISABLED - websockets library not installed")
            print("[WebSocket] To enable live streaming, run: pip3 install websockets")
            return
        
        print(f"[WebSocket] Starting server thread...")
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            print(f"[WebSocket] Event loop created")
            loop.run_until_complete(self.start())
        except KeyboardInterrupt:
            print("\n[WebSocket] Shutting down...")
        except Exception as e:
            print(f"[WebSocket] Startup error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    server = AudioWebSocketServer(port=8765, password='audiopirate')
    server.run()
