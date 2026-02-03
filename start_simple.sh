#!/bin/bash

# Simple startup script without ngrok (for local network use)
# Use this if you don't need external access via ngrok

echo "🏴‍☠️ Starting AudioPirate (local mode)..."

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found."
    echo "Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment and run main.py
source venv/bin/activate
python3 main.py
