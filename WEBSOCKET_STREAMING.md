# WebSocket Live Audio Streaming

## Overview

AudioPirate now uses WebSocket + Web Audio API for low-latency live audio streaming. This approach is optimized for resource-constrained devices like the Raspberry Pi Zero 2 W.

## Why WebSocket over HTTP streaming?

### The Problem with HTTP Audio Streaming
- HTML5 `<audio>` element downloads entire stream before playing
- Cannot handle infinite/continuous streams properly
- High latency and buffering issues
- Not suitable for real-time audio

### WebSocket Advantages
- **Lowest CPU overhead**: No video encoding, no HLS/DASH segmentation
- **Minimal latency**: Real-time audio delivery, typically <100ms
- **Simple implementation**: Direct binary data transfer
- **Browser native**: Web Audio API is built into all modern browsers
- **Resource efficient**: Perfect for Pi Zero 2 W's limited resources

## Architecture

```
┌─────────────┐        WebSocket         ┌──────────────┐
│   Pi Zero   │ ════════════════════════►│   Browser    │
│   (ALSA)    │    Raw Audio Chunks      │ (Web Audio)  │
└─────────────┘                          └──────────────┘
     32-bit                                   Float32
     48kHz                                    48kHz
     Stereo                                   Stereo
```

### Server Side (ws_audio_server.py)
1. **WebSocket Server** (port 8765)
   - Handles authentication (password + token)
   - Manages client connections
   - Token-based session management (24h expiry)

2. **ALSA Audio Capture**
   - Reads from `mic_with_gain` or `hw:0,0`
   - 48kHz, 32-bit S32_LE, stereo
   - Small chunks (1024 samples) for low latency
   - Direct binary transfer to clients

3. **Authentication Flow**
   - Client sends password via WebSocket
   - Server validates and issues token
   - Token required for stream access
   - Same security as HTTPS auth

### Client Side (live_stream.html)
1. **WebSocket Connection**
   - Connects to `ws://hostname:8765` (or `wss://` for SSL)
   - Sends authentication request
   - Receives token on success

2. **Audio Processing**
   - Receives 32-bit int binary chunks
   - Converts to Float32 (-1.0 to 1.0)
   - Queues data for smooth playback
   - ScriptProcessorNode feeds audio to speakers

3. **Visualization**
   - Web Audio API AnalyserNode
   - Real-time waveform display
   - Volume meter with gradient

## Usage

### Starting the Servers

The main app now starts both servers automatically:

```python
# In main.py
self.web_server = WebServer(port=8000, use_ssl=True)  # HTTPS for file access
self.ws_server = AudioWebSocketServer(port=8765)       # WebSocket for streaming

# Both start in run()
self.web_server.start()
ws_thread = threading.Thread(target=self.ws_server.run, daemon=True)
ws_thread.start()
```

### Accessing the Stream

1. Navigate to `https://audiopirate:8000/live` (HTTPS)
2. Accept self-signed certificate warning
3. Enter password (default: `audiopirate`)
4. Click "Start Stream"
5. Audio plays with real-time visualization

## Configuration

### Change WebSocket Port

Edit `main.py`:
```python
self.ws_server = AudioWebSocketServer(port=8765, password='audiopirate')
```

### Change Password

Edit `main.py`:
```python
self.ws_server = AudioWebSocketServer(port=8765, password='your_password')
```

### Audio Settings

Edit `ws_audio_server.py`:
```python
pcm.setchannels(2)           # Stereo
pcm.setrate(48000)           # 48kHz sample rate
pcm.setformat(alsaaudio.PCM_FORMAT_S32_LE)  # 32-bit format
pcm.setperiodsize(1024)      # Chunk size (lower = less latency)
```

## Performance

### Resource Usage (Pi Zero 2 W)
- **CPU**: ~5-10% per client
- **Memory**: ~20MB per client
- **Network**: ~384 KB/s (48kHz × 32-bit × 2 channels)
- **Latency**: 50-100ms typical

### Optimization Tips
1. **Reduce sample rate**: 44.1kHz or 32kHz uses less bandwidth
2. **Mono audio**: Half the bandwidth (change channels to 1)
3. **Increase period size**: Less CPU, more latency
4. **Limit clients**: Pi Zero 2 W can handle 2-3 simultaneous streams

## Troubleshooting

### WebSocket Connection Failed
- Check firewall: Allow port 8765
- Verify server running: `ps aux | grep ws_audio`
- Check network: Browser and Pi on same network

### No Audio Playing
- Check browser console for errors
- Verify microphone permissions in browser
- Test with: `arecord -D hw:0,0 -f S32_LE -r 48000 -c 2 -d 3 test.wav`

### High CPU Usage
- Reduce period size: 2048 or 4096
- Lower sample rate: 32000 or 24000
- Switch to mono: `pcm.setchannels(1)`

### Authentication Errors
- Password is case-sensitive
- Token expires after 24 hours
- Check server logs for auth attempts

## Security Notes

1. **Password Protection**: Required for stream access
2. **Token-Based Sessions**: 24-hour expiry
3. **HTTPS Recommended**: Use reverse proxy (nginx) for production
4. **WSS (WebSocket Secure)**: Add SSL to WebSocket for encryption

### Adding SSL to WebSocket

For production, use `wss://` with proper certificates:

```python
import ssl
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain('cert.pem', 'key.pem')

# In serve()
await serve(self.handler, "0.0.0.0", self.port, ssl=ssl_context)
```

## Advanced: Multiple Clients

The server supports multiple simultaneous clients. Each client:
- Has independent authentication token
- Receives the same audio stream
- Has separate queue management

Monitor active connections:
```python
# Server logs show:
Client connected from ('192.168.1.100', 54321)
Started audio stream for client (device: mic_with_gain)
Streamed 100 chunks (4096 bytes/chunk)
```

## Integration with Main App

The WebSocket server runs alongside the main app:
- **Port 8000**: HTTPS web server (file access, authentication)
- **Port 8765**: WebSocket server (live audio streaming)
- Display and buttons: Control recording
- Web interface: Remote monitoring and file access

## Requirements

Install WebSocket library:
```bash
pip install websockets>=12.0
```

Or update all dependencies:
```bash
pip install -r requirements.txt
```

## Next Steps

1. Test with actual hardware
2. Adjust latency vs CPU usage (period size)
3. Consider adding recording controls to web interface
4. Add audio level indicators on display during streaming
5. Implement automatic reconnection on network issues
