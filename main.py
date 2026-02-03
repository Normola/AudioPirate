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


class AudioPirateApp:
    def __init__(self):
        self.running = False
        self.display = Display()
        self.buttons = ButtonHandler(self.on_button_press)
        self.recorder = AudioRecorder()
        
        # App state
        self.is_recording = False
        self.recording_name = None
        
    def on_button_press(self, button):
        """Handle button press events"""
        if button == "record":
            self.toggle_recording()
        elif button == "play":
            self.play_last_recording()
        elif button == "up":
            self.navigate_up()
        elif button == "down":
            self.navigate_down()
        elif button == "select":
            self.select_item()
            
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
            
    def play_last_recording(self):
        """Play the last recorded audio file"""
        if self.recording_name:
            self.display.show_message(f"Playing...")
            self.recorder.play_audio(self.recording_name)
            self.update_display()
        else:
            self.display.show_message("No recordings")
            time.sleep(1)
            self.update_display()
            
    def navigate_up(self):
        """Navigate up in menu"""
        self.display.show_message("Nav Up")
        
    def navigate_down(self):
        """Navigate down in menu"""
        self.display.show_message("Nav Down")
        
    def select_item(self):
        """Select current menu item"""
        self.display.show_message("Select")
        
    def update_display(self):
        """Update the display with current status"""
        if self.is_recording:
            duration = self.recorder.get_recording_duration()
            self.display.show_status(
                line1="RECORDING",
                line2=f"Time: {duration:.1f}s",
                line3=self.recording_name
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
        
        # Initialize display
        self.display.clear()
        self.update_display()
        
        try:
            while self.running:
                # Update display if recording
                if self.is_recording:
                    self.update_display()
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
