# AudioPirate

Audio recording application for Raspberry Pi Zero 2 W with Pimoroni Pirate Audio board.

## Features

- **Audio Recording**: Record audio in WAV format (44.1kHz, stereo)
- **ST7789 Display**: Real-time status display on 240x240 color LCD
- **Button Controls**: Four physical buttons for recording control
- **Mock Mode**: Can run on non-Pi systems for development/testing

## Hardware Requirements

- Raspberry Pi Zero 2 W
- Pimoroni Pirate Audio board (any variant)
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

4. Reboot:
```bash
sudo reboot
```

5. Install system dependencies:
```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-dev python3-numpy \
    libasound2-dev portaudio19-dev libportaudio2 \
    python3-spidev python3-gpiozero python3-pil \
    fonts-dejavu fonts-dejavu-core swig
```

6. Install Python dependencies:
```bash
pip3 install -r requirements.txt
```

7. Run the application:
```bash
python3 main.py
```

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
- Sample rate: 44.1kHz
- Channels: Stereo
- Filename: `recording_<timestamp>.wav`

## Project Structure

```
AudioPirate/
├── main.py              # Main application entry point
├── display.py           # OLED display handler
├── buttons.py           # GPIO button handler
├── audio_recorder.py    # Audio recording/playback
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
- Check DAC is loaded: `cat /proc/asound/cards` (should show "snd_rpi_hifiberry_dac")
- Verify `/boot/config.txt` has: `dtoverlay=hifiberry-dac`
- Test playback: `speaker-test -c2`
- Check audio devices: `aplay -l` and `arecord -l`
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

## Future Enhancements

- [ ] Audio level metering during recording
- [ ] Recording list browser
- [ ] File management (delete, rename)
- [ ] Audio format options (MP3, OGG)
- [ ] WiFi file transfer
- [ ] Settings menu
- [ ] Battery status display

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please open an issue or submit a pull request.
