#!/usr/bin/env python3
"""
Display Handler for AudioPirate (Pimoroni Pirate Audio)
Supports ST7789 SPI display (240x240)
"""

import time

try:
    import ST7789
    from PIL import Image, ImageDraw, ImageFont
    DISPLAY_AVAILABLE = True
except ImportError:
    DISPLAY_AVAILABLE = False
    print("Warning: ST7789 library not installed. Display will run in mock mode.")


class Display:
    def __init__(self, width=240, height=240):
        self.width = width
        self.height = height
        self.device = None
        self.image = None
        self.draw = None
        self.backlight_on = True
        self.last_activity = time.time()
        self.timeout_seconds = 20
        
        if DISPLAY_AVAILABLE:
            try:
                # Initialize ST7789 SPI display
                self.device = ST7789.ST7789(
                    port=0,
                    cs=1,
                    dc=9,
                    backlight=13,
                    rotation=90,
                    spi_speed_hz=80 * 1000 * 1000
                )
                self.device.begin()
                
                # Create image buffer
                self.image = Image.new('RGB', (width, height), color=(0, 0, 0))
                self.draw = ImageDraw.Draw(self.image)
                
                # Load font - try multiple paths
                self.font = None
                self.font_small = None
                
                font_paths = [
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                    "/usr/share/fonts/truetype/DejaVuSans-Bold.ttf",
                    "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
                ]
                
                for font_path in font_paths:
                    try:
                        self.font = ImageFont.truetype(font_path, 28)
                        self.font_small = ImageFont.truetype(font_path.replace("-Bold", ""), 20)
                        print(f"Loaded font from: {font_path}")
                        break
                    except Exception as e:
                        continue
                
                if not self.font:
                    print("WARNING: Could not load TrueType fonts, using default (will be tiny)")
                    self.font = ImageFont.load_default()
                    self.font_small = ImageFont.load_default()
                    
                print("ST7789 display initialized successfully")
            except Exception as e:
                print(f"Failed to initialize display: {e}")
                print("Running in mock mode")
                self.device = None
        else:
            print("Running display in mock mode")
            
    def clear(self):
        """Clear the display"""
        if self.device:
            self.image.paste((0, 0, 0), [0, 0, self.width, self.height])
            self.device.display(self.image)
        else:
            print("[DISPLAY] Clear")
            
    def show_message(self, message, duration=None):
        """Show a single message on the display"""
        if self.device:
            self.image.paste((0, 0, 0), [0, 0, self.width, self.height])
            self.draw.text((10, 90), message, fill=(255, 255, 255), font=self.font)
            self.device.display(self.image)
        else:
            print(f"[DISPLAY] {message}")
            
    def show_status(self, line1="", line2="", line3="", line4=""):
        """Show multiple lines of status information"""
        if self.device:
            self.image.paste((0, 0, 0), [0, 0, self.width, self.height])
            y_offset = 30
            
            if line1:
                self.draw.text((10, y_offset), line1, fill=(255, 255, 255), font=self.font)
                y_offset += 40
            if line2:
                self.draw.text((10, y_offset), line2, fill=(200, 200, 200), font=self.font_small)
                y_offset += 35
            if line3:
                self.draw.text((10, y_offset), line3, fill=(200, 200, 200), font=self.font_small)
                y_offset += 35
            if line4:
                self.draw.text((10, y_offset), line4, fill=(200, 200, 200), font=self.font_small)
            
            self.device.display(self.image)
        else:
            print(f"[DISPLAY] {line1} | {line2} | {line3} | {line4}")
            
    def show_recording_level(self, level):
        """Show audio level meter during recording"""
        if self.device:
            self.image.paste((0, 0, 0), [0, 0, self.width, self.height])
            
            # Draw title
            self.draw.text((10, 30), "RECORDING", fill=(255, 0, 0), font=self.font)
            
            # Draw level meter (0-100)
            bar_width = int((self.width - 20) * (level / 100.0))
            self.draw.rectangle([(10, 120), (self.width - 10, 180)], outline=(100, 100, 100), fill=(0, 0, 0))
            if bar_width > 0:
                color = (0, 255, 0) if level < 80 else (255, 255, 0) if level < 95 else (255, 0, 0)
                self.draw.rectangle([(10, 120), (10 + bar_width, 180)], fill=color)
            
            self.device.display(self.image)
        else:
            bar = "█" * int(level / 5)
            print(f"[DISPLAY] REC: [{bar:<20}] {level}%")
            
    def show_menu(self, items, selected_index=0):
        """Show a menu with selectable items"""
        if self.device:
            self.image.paste((0, 0, 0), [0, 0, self.width, self.height])
            y_offset = 20
            line_height = 35
            
            for i, item in enumerate(items[:6]):  # Show up to 6 items on larger display
                if i == selected_index:
                    # Highlight selected item
                    self.draw.rectangle([(5, y_offset - 2), (self.width - 5, y_offset + 28)], 
                                      fill=(50, 50, 150), outline=(100, 100, 200))
                    color = (255, 255, 0)
                else:
                    color = (200, 200, 200)
                    
                self.draw.text((15, y_offset), item, fill=color, font=self.font_small)
                y_offset += line_height
            
            self.device.display(self.image)
        else:
            for i, item in enumerate(items[:6]):
                prefix = "> " if i == selected_index else "  "
                print(f"[DISPLAY] {prefix}{item}")
                
    def cleanup(self):
        """Clean up display resources"""
    
    def set_backlight(self, state):
        """Turn backlight on or off"""
        if self.device:
            try:
                self.device.set_backlight(1 if state else 0)
                self.backlight_on = state
                if state:
                    print("Display backlight ON")
                else:
                    print("Display backlight OFF")
            except Exception as e:
                print(f"Backlight control error: {e}")
        else:
            print(f"[MOCK] Backlight: {'ON' if state else 'OFF'}")
    
    def reset_timeout(self):
        """Reset the inactivity timer"""
        self.last_activity = time.time()
        if not self.backlight_on:
            self.set_backlight(True)
    
    def check_timeout(self):
        """Check if screen should timeout and disable backlight"""
        if self.backlight_on and (time.time() - self.last_activity) > self.timeout_seconds:
            self.set_backlight(False)
            return True
        return False
        if self.device:
            self.clear()
        print("Display cleanup complete")
