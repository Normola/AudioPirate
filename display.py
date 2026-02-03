#!/usr/bin/env python3
"""
Display Handler for AudioPirate (Pimoroni Pirate Audio)
Supports ST7789 SPI display (240x240)
"""

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
                
                # Load font
                try:
                    self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
                    self.font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
                except:
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
            y_offset = 20
            
            if line1:
                self.draw.text((10, y_offset), line1, fill=(255, 255, 255), font=self.font)
                y_offset += 60
            if line2:
                self.draw.text((10, y_offset), line2, fill=(200, 200, 200), font=self.font_small)
                y_offset += 50
            if line3:
                self.draw.text((10, y_offset), line3, fill=(200, 200, 200), font=self.font_small)
                y_offset += 50
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
            self.draw.text((10, 20), "RECORDING", fill=(255, 0, 0), font=self.font)
            
            # Draw level meter (0-100)
            bar_width = int((self.width - 20) * (level / 100.0))
            self.draw.rectangle([(10, 100), (self.width - 10, 140)], outline=(100, 100, 100), fill=(0, 0, 0))
            if bar_width > 0:
                color = (0, 255, 0) if level < 80 else (255, 255, 0) if level < 95 else (255, 0, 0)
                self.draw.rectangle([(10, 100), (10 + bar_width, 140)], fill=color)
            
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
        if self.device:
            self.clear()
        print("Display cleanup complete")
