#!/bin/bash
# Setup ALSA gain control for ADAU7002 microphones

echo "Setting up ALSA softvol for microphone gain control..."

# Check if asound.conf exists
if [ ! -f /etc/asound.conf ]; then
    echo "Creating /etc/asound.conf with softvol plugin..."
    sudo tee /etc/asound.conf > /dev/null << 'EOF'
# ALSA configuration for ADAU7002 with software volume control
pcm.mic_with_gain {
    type softvol
    slave.pcm "hw:0,0"
    control {
        name "Mic Boost"
        card 0
    }
    min_dB -5.0
    max_dB 20.0
}

# Default capture device
pcm.!default {
    type asym
    capture.pcm "mic_with_gain"
}
EOF
    echo "✓ /etc/asound.conf created"
else
    echo "✓ /etc/asound.conf already exists"
    cat /etc/asound.conf
fi

# Initialize ALSA controls
echo ""
echo "Initializing ALSA controls..."
sudo alsactl init 2>/dev/null || true

# Set gain to 100% (20dB boost)
echo ""
echo "Setting Mic Boost to 100% (20dB boost)..."
amixer -c 0 set 'Mic Boost' 100% 2>/dev/null || echo "⚠ Mic Boost control not found"

# Show current settings
echo ""
echo "Current ALSA controls:"
amixer -c 0 controls | head -10

echo ""
echo "Mic Boost status:"
amixer -c 0 get 'Mic Boost' 2>/dev/null || echo "Mic Boost control not available"

echo ""
echo "Done! Restart your app: python3 main.py"
