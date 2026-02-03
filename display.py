#!/usr/bin/env python3
"""
Display Handler for AudioPirate
Supports SSD1306 OLED display (128x64)
"""

try:
    from luma.core.interface.serial import i2c
    from luma.core.render import canvas
    from luma.oled.device import ssd1306
    from PIL import ImageFont
    DISPLAY_AVAILABLE = True
except ImportError:
    DISPLAY_AVAILABLE = False
    print("Warning: luma.oled not installed. Display will run in mock mode.")


class Display:
    def __init__(self, width=128, height=64):
        self.width = width
        self.height = height
        self.device = None
        
        if DISPLAY_AVAILABLE:
            try:
                # Initialize I2C interface (address 0x3C is common for SSD1306)
                serial = i2c(port=1, address=0x3C)
                self.device = ssd1306(serial, width=width, height=height)
                self.font = ImageFont.load_default()
                print("Display initialized successfully")
            except Exception as e:
                print(f"Failed to initialize display: {e}")
                print("Running in mock mode")
                self.device = None
        else:
            print("Running display in mock mode")
            
    def clear(self):
        """Clear the display"""
        if self.device:
            with canvas(self.device) as draw:
                draw.rectangle(self.device.bounding_box, outline="black", fill="black")
        else:
            print("[DISPLAY] Clear")
            
    def show_message(self, message, duration=None):
        """Show a single message on the display"""
        if self.device:
            with canvas(self.device) as draw:
                draw.text((0, 28), message, fill="white", font=self.font)
        else:
            print(f"[DISPLAY] {message}")
            
    def show_status(self, line1="", line2="", line3="", line4=""):
        """Show multiple lines of status information"""
        if self.device:
            with canvas(self.device) as draw:
                y_offset = 0
                line_height = 16
                
                if line1:
                    draw.text((0, y_offset), line1, fill="white", font=self.font)
                    y_offset += line_height
                if line2:
                    draw.text((0, y_offset), line2, fill="white", font=self.font)
                    y_offset += line_height
                if line3:
                    draw.text((0, y_offset), line3, fill="white", font=self.font)
                    y_offset += line_height
                if line4:
                    draw.text((0, y_offset), line4, fill="white", font=self.font)
        else:
            print(f"[DISPLAY] {line1} | {line2} | {line3} | {line4}")
            
    def show_recording_level(self, level):
        """Show audio level meter during recording"""
        if self.device:
            with canvas(self.device) as draw:
                # Draw title
                draw.text((0, 0), "RECORDING", fill="white", font=self.font)
                
                # Draw level meter (0-100)
                bar_width = int(self.width * (level / 100.0))
                draw.rectangle([(0, 20), (self.width, 40)], outline="white", fill="black")
                draw.rectangle([(0, 20), (bar_width, 40)], outline="white", fill="white")
        else:
            bar = "█" * int(level / 5)
            print(f"[DISPLAY] REC: [{bar:<20}] {level}%")
            
    def show_menu(self, items, selected_index=0):
        """Show a menu with selectable items"""
        if self.device:
            with canvas(self.device) as draw:
                y_offset = 0
                line_height = 16
                
                for i, item in enumerate(items[:4]):  # Show up to 4 items
                    prefix = "> " if i == selected_index else "  "
                    draw.text((0, y_offset), f"{prefix}{item}", fill="white", font=self.font)
                    y_offset += line_height
        else:
            for i, item in enumerate(items[:4]):
                prefix = "> " if i == selected_index else "  "
                print(f"[DISPLAY] {prefix}{item}")
                
    def cleanup(self):
        """Clean up display resources"""
        if self.device:
            self.clear()
        print("Display cleanup complete")
