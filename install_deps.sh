#!/bin/bash
# Install all required dependencies for AudioPirate

echo "Installing AudioPirate dependencies..."

# Update pip
pip3 install --upgrade pip

# Install from requirements.txt
pip3 install -r requirements.txt

# Verify installations
echo ""
echo "Verifying installations..."
python3 -c "import websockets; print('✓ websockets:', websockets.__version__)"
python3 -c "import alsaaudio; print('✓ alsaaudio installed')" 2>/dev/null || echo "⚠ alsaaudio not available (OK if not on Pi)"
python3 -c "import cryptography; print('✓ cryptography installed')"
python3 -c "from PIL import Image; print('✓ Pillow installed')"
python3 -c "import gpiozero; print('✓ gpiozero installed')" 2>/dev/null || echo "⚠ gpiozero not available (OK if not on Pi)"
python3 -c "import ST7789; print('✓ st7789 installed')" 2>/dev/null || echo "⚠ ST7789 not available (OK if not on Pi)"

echo ""
echo "Installation complete!"
echo "Run 'python3 main.py' to start AudioPirate"
