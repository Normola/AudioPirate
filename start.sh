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
sleep 1

# Start ngrok using config file (supports multiple tunnels with hobby plan)
echo "🌐 Starting ngrok tunnels..."
ngrok start --all --config=ngrok.yml --log=stdout > ngrok.log 2>&1 &
NGROK_PID=$!

# Wait a moment for ngrok to start
sleep 4

# Get ngrok URLs
echo ""
echo "📡 Ngrok Tunnels:"
curl -s http://localhost:4040/api/tunnels | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    web_url = None
    ws_url = None
    for tunnel in data['tunnels']:
        name = tunnel['name']
        url = tunnel['public_url']
        if name == 'web':
            web_url = url
        elif name == 'websocket':
            ws_url = url.replace('https://', 'wss://')
    
    if web_url:
        print(f'  Web UI: {web_url}')
    if ws_url:
        print(f'  WebSocket: {ws_url}')
    
    if not web_url and not ws_url:
        print('  No tunnels found')
        for tunnel in data['tunnels']:
            print(f\"    {tunnel['name']}: {tunnel['public_url']}\")
except Exception as e:
    print(f'  Check ngrok dashboard at: http://localhost:4040')
" 2>/dev/null || echo "  Check ngrok dashboard at: http://localhost:4040"

echo ""
echo "🚀 Starting AudioPirate application..."

# Activate virtual environment and run main.py
source .venv/bin/activate
python3 main.py

# Cleanup on exit
echo ""
echo "🛑 Shutting down..."
kill $NGROK_PID 2>/dev/null || true
pkill -f ngrok || true
echo "✅ Shutdown complete"
