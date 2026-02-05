#!/usr/bin/env python3
"""
AudioPirate - Main Application
Raspberry Pi Zero 2 W + AudioPirate Board
"""

import time
import threading
import json
import urllib.request
from display import Display
from buttons import ButtonHandler
from audio_recorder import AudioRecorder
from web_server import WebServer
from ws_audio_server import AudioWebSocketServer
import asyncio


class AudioPirateApp:
    def __init__(self):
        self.running = False
        self.display = Display()
        self.buttons = ButtonHandler(self.on_button_press)
        self.recorder = AudioRecorder()
        # Disable SSL when using ngrok (ngrok handles SSL termination)
        import os
        use_ssl = not os.path.exists('ngrok.yml')
        self.web_server = WebServer(directory="recordings", port=8000, use_ssl=use_ssl)
        # Use hw:0,0 directly instead of mic_with_gain (softvol not working)
        # Disable SSL on WebSocket - let reverse proxy (ngrok/nginx) handle SSL termination
        self.ws_server = AudioWebSocketServer(port=8765, password='audiopirate', use_ssl=False, audio_device='hw:0,0')
        
        # App state
        self.ngrok_url = None
        
    def on_button_press(self, button):
        """Handle button press events"""
        if button == "info":
            self.show_recordings_info()
        elif button == "up":
            self.navigate_up()
        elif button == "down":
            self.navigate_down()
            
    def get_ngrok_url(self):
        """Get the ngrok public URL from the local API"""
        try:
            response = urllib.request.urlopen('http://localhost:4040/api/tunnels', timeout=2)
            data = json.loads(response.read().decode('utf-8'))
            
            for tunnel in data.get('tunnels', []):
                if tunnel.get('name') == 'web':
                    url = tunnel.get('public_url', '')
                    # Remove https:// prefix for display
                    if url.startswith('https://'):
                        url = url[8:]
                    elif url.startswith('http://'):
                        url = url[7:]
                    return url
            return None
        except Exception as e:
            print(f"Error getting ngrok URL: {e}")
            return None
            
    def show_recordings_info(self):
        """Show information about recordings"""
        recordings = self.recorder.list_recordings()
        count = len(recordings)
        total_size = sum(r['size'] for r in recordings) / (1024 * 1024)  # MB
        self.display.show_message(f"{count} recordings")
        print(f"Recordings: {count}, Total: {total_size:.1f}MB")
        time.sleep(2)
        self.update_display()
            
    def navigate_up(self):
        """Navigate up in menu"""
        self.display.show_message("Nav Up")
        
    def navigate_down(self):
        """Navigate down in menu"""
        self.display.show_message("Nav Down")
        time.sleep(1)
        self.update_display()
        
    def update_display(self):
        """Update the display with current status"""
        # Get fresh ngrok URL
        url = self.get_ngrok_url()
        
        if url:
            self.display.show_status(
                line1="AudioPirate",
                line2="Web UI:",
                line3=url[:30],  # First 30 chars
                line4=url[30:] if len(url) > 30 else ""  # Remaining chars if needed
            )
        else:
            self.display.show_status(
                line1="AudioPirate",
                line2="Starting...",
                line3="Waiting for ngrok",
                line4=""
            )
            
    def run(self):
        """Main application loop"""
        self.running = True
        print("AudioPirate App Starting...")
        
        # Start web server
        self.web_server.start()
        
        # Start WebSocket server in separate thread
        ws_thread = threading.Thread(target=self.ws_server.run, daemon=True)
        ws_thread.start()
        
        # Initialize display
        self.display.clear()
        self.update_display()
        
        last_url_update = 0
        
        try:
            while self.running:
                # Update display periodically to get latest ngrok URL
                if time.time() - last_url_update > 5:
                    self.update_display()
                    last_url_update = time.time()
                
                # Check for display timeout
                self.display.check_timeout()
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.cleanup()
            
    def cleanup(self):
        """Clean up resources"""
        self.buttons.cleanup()
        self.display.clear()
        self.display.cleanup()
        print("Cleanup complete")


if __name__ == "__main__":
    app = AudioPirateApp()
    app.run()
