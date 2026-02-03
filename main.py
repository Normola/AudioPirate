#!/usr/bin/env python3
"""
AudioPirate - Main Application
Raspberry Pi Zero 2 W + AudioPirate Board
"""

import time
import threading
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
        self.web_server = WebServer(directory="recordings", port=8000, use_ssl=True)
        self.ws_server = AudioWebSocketServer(port=8765, password='audiopirate', use_ssl=True)
        
        # App state
        self.is_recording = False
        self.recording_name = None
        
    def on_button_press(self, button):
        """Handle button press events"""
        if button == "record":
            self.toggle_recording()
        elif button == "info":
            self.show_recordings_info()
        elif button == "up":
            self.navigate_up()
        elif button == "down":
            self.navigate_down()
            
    def toggle_recording(self):
        """Start or stop audio recording"""
        if not self.is_recording:
            # Start recording
            filename = f"recording_{int(time.time())}.wav"
            self.recorder.start_recording(filename)
            self.is_recording = True
            self.recording_name = filename
            self.display.show_message(f"REC: {filename}")
            print(f"Started recording: {filename}")
        else:
            # Stop recording
            self.recorder.stop_recording()
            self.is_recording = False
            self.display.show_message(f"Saved: {self.recording_name}")
            print(f"Stopped recording: {self.recording_name}")
            time.sleep(1)
            self.update_display()
            
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
        if self.is_recording:
            duration = self.recorder.get_recording_duration()
            self.display.show_status(
                line1="RECORDING",
                line2=f"Time: {duration:.1f}s",
                line3=self.recording_name or ""
            )
        else:
            self.display.show_status(
                line1="AudioPirate Ready",
                line2="Press REC to start",
                line3=""
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
        
        try:
            while self.running:
                # Update display if recording
                if self.is_recording:
                    self.update_display()
                
                # Check for display timeout
                self.display.check_timeout()
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.cleanup()
            
    def cleanup(self):
        """Clean up resources"""
        if self.is_recording:
            self.recorder.stop_recording()
        self.buttons.cleanup()
        self.display.clear()
        self.display.cleanup()
        print("Cleanup complete")


if __name__ == "__main__":
    app = AudioPirateApp()
    app.run()
