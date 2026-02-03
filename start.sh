#!/bin/bash

# AudioPirate Startup Script
# Starts ngrok tunnels and the main application

echo "🏴‍☠️ Starting AudioPirate..."

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok is not installed. Install it from https://ngrok.com/download"
    exit 1
fi

# Check if .venv exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Run: python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Kill any existing ngrok processes
echo "🧹 Cleaning up existing ngrok processes..."
pkill -f ngrok || true

# Start ngrok for HTTPS web server (port 8000) in background
echo "🌐 Starting ngrok tunnel for web server (port 8000)..."
ngrok http 8000 --log=stdout > ngrok_web.log 2>&1 &
NGROK_WEB_PID=$!

# Start ngrok for WebSocket server (port 8765) in background  
echo "🌐 Starting ngrok tunnel for WebSocket (port 8765)..."
ngrok http 8765 --log=stdout > ngrok_ws.log 2>&1 &
NGROK_WS_PID=$!

# Wait a moment for ngrok to start
sleep 3

# Get ngrok URLs
echo ""
echo "📡 Ngrok Tunnels:"
curl -s http://localhost:4040/api/tunnels | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for tunnel in data['tunnels']:
        proto = tunnel['proto']
        url = tunnel['public_url']
        addr = tunnel['config']['addr']
        if '8000' in addr:
            print(f\"  Web UI: {url}\")
        elif '8765' in addr:
            print(f\"  WebSocket: {url.replace('https://', 'wss://')}\")
except:
    print('  Check ngrok dashboard at: http://localhost:4040')
" 2>/dev/null || echo "  Check ngrok dashboard at: http://localhost:4040"

echo ""
echo "🚀 Starting AudioPirate application..."

# Activate virtual environment and run main.py
source .venv/bin/activate
python3 main.py

# Cleanup on exit
echo ""
echo "🛑 Shutting down..."
kill $NGROK_WEB_PID 2>/dev/null || true
kill $NGROK_WS_PID 2>/dev/null || true
pkill -f ngrok || true
echo "✅ Shutdown complete"
