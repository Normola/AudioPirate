#!/usr/bin/env python3
"""
AudioPirate Diagnostic Tool
Checks if all dependencies are installed and services can start
"""

import sys

print("=" * 60)
print("AudioPirate Diagnostic Tool")
print("=" * 60)

# Check Python version
print(f"\n1. Python Version: {sys.version}")
if sys.version_info < (3, 7):
    print("   ⚠ WARNING: Python 3.7+ recommended")

# Check required libraries
print("\n2. Checking Python Libraries:")
libraries = {
    'websockets': 'WebSocket streaming',
    'alsaaudio': 'Audio recording (Pi only)',
    'cryptography': 'HTTPS certificates',
    'PIL': 'Display graphics',
    'gpiozero': 'Button controls (Pi only)',
    'ST7789': 'Display driver (Pi only)',
}

missing = []
for lib, description in libraries.items():
    try:
        if lib == 'PIL':
            __import__('PIL')
        else:
            __import__(lib)
        print(f"   ✓ {lib:15} - {description}")
    except ImportError:
        print(f"   ✗ {lib:15} - {description} [MISSING]")
        missing.append(lib)

# Check WebSocket server
print("\n3. WebSocket Server Test:")
try:
    from ws_audio_server import AudioWebSocketServer
    server = AudioWebSocketServer(port=8765, password='test')
    print("   ✓ WebSocket server can be created")
    
    # Check if websockets is available
    from ws_audio_server import WEBSOCKETS_AVAILABLE
    if WEBSOCKETS_AVAILABLE:
        print("   ✓ websockets library loaded")
    else:
        print("   ✗ websockets library NOT available")
        missing.append('websockets')
except Exception as e:
    print(f"   ✗ WebSocket server error: {e}")

# Check HTTPS server
print("\n4. HTTPS Web Server Test:")
try:
    from web_server import WebServer
    web = WebServer(directory="recordings", port=8000, use_ssl=True)
    print("   ✓ Web server can be created")
except Exception as e:
    print(f"   ✗ Web server error: {e}")

# Check audio recorder
print("\n5. Audio Recorder Test:")
try:
    from audio_recorder import AudioRecorder, ALSA_AVAILABLE
    recorder = AudioRecorder()
    if ALSA_AVAILABLE:
        print("   ✓ ALSA audio available")
    else:
        print("   ⚠ ALSA not available (mock mode)")
except Exception as e:
    print(f"   ✗ Audio recorder error: {e}")

# Check display
print("\n6. Display Test:")
try:
    from display import Display, DISPLAY_AVAILABLE
    display = Display()
    if DISPLAY_AVAILABLE:
        print("   ✓ ST7789 display available")
    else:
        print("   ⚠ Display not available (mock mode)")
except Exception as e:
    print(f"   ✗ Display error: {e}")

# Check buttons
print("\n7. Button Controls Test:")
try:
    from buttons import ButtonHandler, GPIOZERO_AVAILABLE
    # Don't actually create buttons (might fail without hardware)
    if GPIOZERO_AVAILABLE:
        print("   ✓ gpiozero available")
    else:
        print("   ⚠ gpiozero not available (mock mode)")
except Exception as e:
    print(f"   ✗ Button handler error: {e}")

# Summary
print("\n" + "=" * 60)
if missing:
    print(f"ISSUES FOUND: {len(missing)} missing libraries")
    print("\nTo fix, run:")
    if 'websockets' in missing:
        print("  pip3 install websockets")
    if 'cryptography' in missing:
        print("  pip3 install cryptography")
    if 'PIL' in missing:
        print("  pip3 install Pillow")
    print("\nOr install all:")
    print("  pip3 install -r requirements.txt")
    print("  ./install_deps.sh")
else:
    print("✓ All required libraries installed!")
    print("\nYou can start AudioPirate:")
    print("  python3 main.py")

print("=" * 60)
