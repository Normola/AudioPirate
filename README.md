# AudioPirate

Audio recording application for Raspberry Pi Zero 2 W with Pimoroni Pirate Audio board.

## Features

- **Audio Recording**: Record audio in WAV format (48kHz, stereo, 32-bit)
- **ST7789 Display**: Real-time status display on 240x240 color LCD
- **Button Controls**: Four physical buttons for recording control
- **Microphone Gain Control**: Software gain adjustment (-5dB to +20dB) for far-field recording
- **Live Audio Streaming**: Real-time low-latency streaming via WebSocket + Web Audio API
- **Web Server**: Built-in HTTPS server for accessing recordings and live stream
- **Password Authentication**: Secure access to web interface and live stream
- **Mock Mode**: Can run on non-Pi systems for development/testing

## Hardware Requirements

- Raspberry Pi Zero 2 W
- Pimoroni Pirate Audio Dual Mic board (with ADAU7002 microphones)
- MicroSD card (8GB+ recommended)

## Default GPIO Pin Mapping

```
Button A: GPIO 5  (Record)
Button B: GPIO 6  (Play)
Button X: GPIO 16 (Up/Menu)
Button Y: GPIO 24 (Down/Menu)

Display: SPI0 (ST7789 240x240)
  - MOSI: GPIO 10
  - SCLK: GPIO 11
  - CS:   GPIO 1
  - DC:   GPIO 9
  - BL:   GPIO 13
```

## Installation

### On Raspberry Pi

1. Clone this repository:
```bash
git clone <repository-url>
cd AudioPirate
```

2. Add device tree overlays to `/boot/config.txt`:
```bash
sudo nano /boot/config.txt
```

Add these lines:
```
# Enable HiFiBerry DAC for Pirate Audio
dtoverlay=hifiberry-dac
gpio=25=op,dh

# Disable onboard audio (optional but recommended)
dtparam=audio=off

# For Dual Mic variant, also add:
# dtoverlay=adau7002-simple
```

3. Enable SPI interface:
```bash
sudo raspi-config
# Navigate to: Interface Options -> SPI -> Enable
```

4. Install ALSA configuration for microphone gain control:
```bash
# Copy the configuration file
sudo cp asound.conf /etc/asound.conf

# Initialize ALSA controls
sudo alsactl init

# Verify the Mic Boost control is available
amixer -c 0 controls | grep 'Mic Boost'
```

You can now control microphone gain:
```bash
# Set gain to 80% (~15dB boost, good for far-field recording)
amixer -c 0 set 'Mic Boost' 80%

# Check current gain
amixer -c 0 get 'Mic Boost'
```

**Gain range:**
- 0% = -5dB (quietest, use for close/loud sources)
- 50% = ~7.5dB (medium boost, balanced)
- 80% = ~15dB (good for far-field recording)
- 100% = +20dB (maximum boost, may introduce noise)

5. Reboot:
```bash
sudo reboot
```

6. Install system dependencies:
```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-dev python3-numpy \
    libasound2-dev python3-alsaaudio \
    python3-spidev python3-gpiozero python3-pil \
    fonts-dejavu fonts-dejavu-core swig liblgpio-dev
```

7. Install Python dependencies:
```bash
pip3 install -r requirements.txt
```

Or use the install script:
```bash
chmod +x install_deps.sh
./install_deps.sh
```

8. Run the application:
```bash
python3 main.py
```

The application will start:
- HTTPS web server on port 8000
- WebSocket server on port 8765 (for live streaming)
- Display and button controls active

### Development Mode (Non-Pi Systems)

The app can run in mock mode for development:

```bash
pip install -r requirements.txt
python main.py
```

Display and button outputs will print to console. GPIO and audio hardware are simulated.

## Usage

### Button Controls

- **Button A (Record)**: Start/stop audio recording
- **Button B (Info)**: Show recordings count and total size
- **Button X (Up)**: Navigate menus (future feature)
- **Button Y (Down)**: Navigate menus (future feature)

### Recordings

Audio files are saved in the `recordings/` directory with timestamps:
- Format: WAV (uncompressed)
- Sample rate: 48kHz (required for ADAU7002)
- Channels: Stereo (dual MEMS microphones)
- Bit depth: 32-bit
- Filename: `recording_<timestamp>.wav`

### Web Interface

1. **File Access** (HTTPS, port 8000):
   - Navigate to `https://<pi-ip>:8000`
   - Accept self-signed certificate warning
   - Browse and download recordings

2. **Live Stream** (WebSocket, port 8765):
   - Navigate to `https://<pi-ip>:8000/live`
   - Enter password (default: `audiopirate`)
   - Click "Start Stream" for real-time audio
   - See [WEBSOCKET_STREAMING.md](WEBSOCKET_STREAMING.md) for details

### Web Access

The app automatically starts a web server on port 8000:
- **Browse recordings**: `http://<pi-ip-address>:8000`
- **Live audio stream**: `http://<pi-ip-address>:8000/live`
- Download recordings directly from your browser
- Real-time audio streaming with waveform visualization

#### Live Streaming
Access the `/live` endpoint to stream audio in real-time from the microphones. Features:
- Live audio playback in browser
- Real-time waveform visualization
- Volume meter
- Works on any device with a web browser

## Project Structure

```
AudioPirate/
├── main.py              # Main application entry point
├── display.py           # ST7789 display handler
├── buttons.py           # GPIO button handler
├── audio_recorder.py    # Audio recording
├── web_server.py        # HTTP server for file access
├── requirements.txt     # Python dependencies
├── recordings/          # Recorded audio files (created at runtime)
└── README.md           # This file
```

## Configuration

Edit the class constants in each module to customize:

- **Display** ([display.py](display.py)): Screen dimensions, SPI pins, backlight
- **Buttons** ([buttons.py](buttons.py)): GPIO pin assignments (BCM 5, 6, 16, 24)
- **Audio** ([audio_recorder.py](audio_recorder.py)): Sample rate, channels, format

## Troubleshooting

### Display not working
- Check SPI is enabled: `ls /dev/spidev*` (should show spidev0.0, spidev0.1)
- Verify with: `sudo raspi-config` -> Interface Options -> SPI -> Enabled
- Check for errors in: `sudo dmesg | grep spi`

### Audio issues
- Verify `/boot/config.txt` has: `dtoverlay=adau7002-simple`
- Test recording: `arecord -D hw:0,0 -f S32_LE -r 48000 -c 2 -d 5 test.wav`
- Check audio devices: `arecord -l` (should list ADAU7002)
- Audio uses ALSA directly for better MEMS mic support
- For Dual Mic variant, ensure `dtoverlay=adau7002-simple` is in config.txt

### Button issues
- Buttons use gpiozero library (more reliable than RPi.GPIO)
- No sudo or special permissions needed on recent Raspberry Pi OS
- If buttons don't work, try: `sudo apt-get install python3-gpiozero`
- Test button pins: `pinout` (shows GPIO layout)

### Permission errors
- GPIO access: `sudo usermod -a -G gpio $USER`
- SPI access: `sudo usermod -a -G spi $USER`
- Audio access: `sudo usermod -a -G audio $USER`
- Then logout/login or reboot

### Live streaming issues

**"Connection error. Is the server running?"**
1. Check if websockets library is installed:
   ```bash
   python3 -c "import websockets; print('OK')"
   ```
   If not installed: `pip3 install websockets`

2. Verify WebSocket server is running:
   ```bash
   ps aux | grep ws_audio_server
   # Should show the WebSocket server process
   ```

3. Check server logs when starting main.py:
   ```
   WebSocket server started on ws://0.0.0.0:8765
   Waiting for connections...
   ```
   If you see "WebSocket streaming disabled", install websockets library

4. Test WebSocket server separately:
   ```bash
   python3 test_websocket.py
   ```

5. Check firewall allows port 8765:
   ```bash
   sudo ufw allow 8765/tcp
   ```

**Other streaming issues:**
- No audio playing: Check browser console, verify microphones working
- High CPU usage: See [WEBSOCKET_STREAMING.md](WEBSOCKET_STREAMING.md) for optimization
- Authentication errors: Password is case-sensitive, tokens expire after 24h

## Documentation

- [WEBSOCKET_STREAMING.md](WEBSOCKET_STREAMING.md) - Live audio streaming setup and optimization
- [HTTPS_SETUP.md](HTTPS_SETUP.md) - SSL certificate configuration
- [AUTHENTICATION.md](AUTHENTICATION.md) - Password authentication system
- [ALSA_SETUP.md](ALSA_SETUP.md) - Audio configuration and gain control

## Future Enhancements

- [ ] Audio level metering on display during recording
- [ ] Recording list browser on display
- [ ] File management (delete) via web interface
- [ ] Automatic reconnection for WebSocket streaming
- [ ] Recording controls in web interface
- [ ] File management via web interface (delete, rename)
- [ ] Audio format options (MP3, OGG)ns (MP3, OGG)
- [ ] WiFi file transfer
- [ ] Settings menu
- [ ] Battery status display

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please open an issue or submit a pull request.
