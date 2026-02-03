# AudioPirate

Audio recording application for Raspberry Pi Zero 2 W with AudioPirate board.

## Features

- **Audio Recording**: Record audio in WAV format (44.1kHz, stereo)
- **OLED Display**: Real-time status display on SSD1306 128x64 OLED
- **Button Controls**: Physical button interface for all operations
- **Mock Mode**: Can run on non-Pi systems for development/testing

## Hardware Requirements

- Raspberry Pi Zero 2 W
- AudioPirate board (audio interface + OLED display + buttons)
- MicroSD card (8GB+ recommended)

## Default GPIO Pin Mapping

```
Record Button: GPIO 17
Play Button:   GPIO 27
Up Button:     GPIO 22
Down Button:   GPIO 23
Select Button: GPIO 24
Display I2C:   SDA=GPIO 2, SCL=GPIO 3 (I2C address 0x3C)
```

Adjust pin mappings in [buttons.py](buttons.py) if your board uses different pins.

## Installation

### On Raspberry Pi

1. Clone this repository:
```bash
git clone <repository-url>
cd AudioPirate
```

2. Install system dependencies:
```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-dev libasound2-dev portaudio19-dev
```

3. Install Python dependencies:
```bash
pip3 install -r requirements.txt
```

4. Enable I2C interface:
```bash
sudo raspi-config
# Navigate to: Interface Options -> I2C -> Enable
```

5. Run the application:
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

- **Record**: Start/stop audio recording
- **Play**: Play the last recorded audio
- **Up/Down**: Navigate menus (future feature)
- **Select**: Confirm selection (future feature)

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

- **Display** ([display.py](display.py)): Screen dimensions, I2C address
- **Buttons** ([buttons.py](buttons.py)): GPIO pin assignments, debounce time
- **Audio** ([audio_recorder.py](audio_recorder.py)): Sample rate, channels, format

## Troubleshooting

### Display not working
- Check I2C is enabled: `sudo i2cdetect -y 1`
- Verify I2C address (usually 0x3C or 0x3D)
- Check connections: SDA to GPIO 2, SCL to GPIO 3

### Audio issues
- Check audio devices: `arecord -l` and `aplay -l`
- Test recording: `arecord -d 5 test.wav`
- Ensure user is in audio group: `sudo usermod -a -G audio $USER`

### Permission errors
- GPIO access: `sudo usermod -a -G gpio $USER`
- I2C access: `sudo usermod -a -G i2c $USER`
- Then logout/login

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
