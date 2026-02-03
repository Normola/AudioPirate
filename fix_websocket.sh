#!/bin/bash
# Quick fix for WebSocket connection issues
# Run this on the Pi: bash fix_websocket.sh

echo "AudioPirate WebSocket Fix Script"
echo "================================="
echo ""

# Check if websockets is installed
echo "1. Checking websockets library..."
if python3 -c "import websockets" 2>/dev/null; then
    VERSION=$(python3 -c "import websockets; print(websockets.__version__)")
    echo "   ✓ websockets is installed (version $VERSION)"
else
    echo "   ✗ websockets is NOT installed"
    echo "   Installing now..."
    pip3 install websockets
    
    if [ $? -eq 0 ]; then
        echo "   ✓ websockets installed successfully!"
    else
        echo "   ✗ Installation failed. Trying with sudo..."
        sudo pip3 install websockets
    fi
fi

echo ""
echo "2. Checking if port 8765 is in use..."
if netstat -tuln 2>/dev/null | grep -q ":8765 "; then
    echo "   ✓ Port 8765 is in use (server might be running)"
else
    echo "   ⚠ Port 8765 is not in use (server not running)"
fi

echo ""
echo "3. Checking SSL certificates..."
if [ -f "certs/cert.pem" ] && [ -f "certs/key.pem" ]; then
    echo "   ✓ SSL certificates found"
else
    echo "   ⚠ SSL certificates not found in certs/"
    echo "   The web server should create these automatically"
fi

echo ""
echo "4. Testing WebSocket server startup..."
python3 check_websocket.py &
SERVER_PID=$!
sleep 3
kill $SERVER_PID 2>/dev/null

echo ""
echo "================================="
echo "Fix complete! Now:"
echo "1. Stop main.py if it's running (Ctrl+C)"
echo "2. Start it again: python3 main.py"
echo "3. Look for: 'WebSocket server started on wss://0.0.0.0:8765'"
echo "================================="
