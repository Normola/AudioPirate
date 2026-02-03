#!/usr/bin/env python3
"""
Button/GPIO Handler for AudioPirate
Manages button inputs via GPIO pins
"""

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    print("Warning: RPi.GPIO not installed. Buttons will run in mock mode.")

import time
import threading


class ButtonHandler:
    # Define GPIO pin mappings (adjust these based on your AudioPirate board)
    BUTTON_PINS = {
        "record": 17,   # GPIO 17
        "play": 27,     # GPIO 27
        "up": 22,       # GPIO 22
        "down": 23,     # GPIO 23
        "select": 24,   # GPIO 24
    }
    
    DEBOUNCE_TIME = 0.2  # 200ms debounce
    
    def __init__(self, callback):
        """
        Initialize button handler
        
        Args:
            callback: Function to call when button is pressed, receives button name
        """
        self.callback = callback
        self.last_press_time = {}
        self.mock_mode = not GPIO_AVAILABLE
        
        if GPIO_AVAILABLE:
            try:
                # Setup GPIO
                GPIO.setmode(GPIO.BCM)
                GPIO.setwarnings(False)
                
                # Configure each button pin
                for button_name, pin in self.BUTTON_PINS.items():
                    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                    GPIO.add_event_detect(
                        pin,
                        GPIO.FALLING,
                        callback=lambda channel, btn=button_name: self._on_button_event(btn),
                        bouncetime=int(self.DEBOUNCE_TIME * 1000)
                    )
                    self.last_press_time[button_name] = 0
                    
                print("Button handler initialized successfully")
            except Exception as e:
                print(f"Failed to initialize GPIO: {e}")
                print("Running in mock mode")
                self.mock_mode = True
        
        # Start mock button thread if needed (for testing on non-Pi systems)
        if self.mock_mode:
            print("Button handler running in mock mode")
            print("Press keys: r=record, p=play, u=up, d=down, s=select")
            self._start_mock_input()
            
    def _on_button_event(self, button_name):
        """Handle button press with debouncing"""
        current_time = time.time()
        
        # Check debounce
        if current_time - self.last_press_time[button_name] < self.DEBOUNCE_TIME:
            return
            
        self.last_press_time[button_name] = current_time
        
        print(f"Button pressed: {button_name}")
        
        # Call the callback
        if self.callback:
            self.callback(button_name)
            
    def _start_mock_input(self):
        """Start a thread to simulate button presses from keyboard (for testing)"""
        def input_loop():
            key_map = {
                'r': 'record',
                'p': 'play',
                'u': 'up',
                'd': 'down',
                's': 'select',
            }
            
            try:
                while True:
                    # This is a simple implementation - could be enhanced with proper keyboard handling
                    time.sleep(0.1)
            except KeyboardInterrupt:
                pass
                
        # Note: In mock mode, you'd typically use a library like 'keyboard' or 'pynput'
        # For now, this is just a placeholder
        # threading.Thread(target=input_loop, daemon=True).start()
        
    def simulate_button_press(self, button_name):
        """Manually trigger a button press (useful for testing)"""
        if button_name in self.BUTTON_PINS:
            self._on_button_event(button_name)
        else:
            print(f"Unknown button: {button_name}")
            
    def cleanup(self):
        """Clean up GPIO resources"""
        if GPIO_AVAILABLE and not self.mock_mode:
            GPIO.cleanup()
        print("Button handler cleanup complete")
