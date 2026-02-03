#!/usr/bin/env python3
"""
Button/GPIO Handler for AudioPirate
Manages button inputs via GPIO pins
"""

try:
    from gpiozero import Button
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    print("Warning: gpiozero not installed. Buttons will run in mock mode.")

import time
import threading


class ButtonHandler:
    # Pimoroni Pirate Audio button GPIO pin mappings
    # Buttons are active LOW (pressed = LOW, released = HIGH)
    BUTTON_PINS = {
        "A": 5,         # GPIO 5 (Button A)
        "B": 6,         # GPIO 6 (Button B)
        "X": 16,        # GPIO 16 (Button X)
        "Y": 24,        # GPIO 24 (Button Y)
    }
    
    # Friendly aliases for button functions
    BUTTON_ALIASES = {
        "record": "A",
        "info": "B",      # Show recordings info
        "up": "X",
        "down": "Y",
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
        self.buttons = {}
        
        if GPIO_AVAILABLE:
            try:
                # Setup buttons with gpiozero (pull_up=True for active LOW)
                for button_name, pin in self.BUTTON_PINS.items():
                    btn = Button(pin, pull_up=True, bounce_time=self.DEBOUNCE_TIME)
                    btn.when_pressed = lambda b=button_name: self._on_button_event(b)
                    self.buttons[button_name] = btn
                    self.last_press_time[button_name] = 0
                    
                print("Button handler initialized successfully")
            except Exception as e:
                print(f"Failed to initialize GPIO: {e}")
                print("Running in mock mode")
                self.mock_mode = True
        
        # Start mock button thread if needed (for testing on non-Pi systems)
        if self.mock_mode:
            print("Button handler running in mock mode")
            print("Button mapping: A=record, B=play, X=up, Y=down")
            self._start_mock_input()
            
    def _on_button_event(self, button_name):
        """Handle button press with debouncing"""
        current_time = time.time()
        
        # Check debounce
        if current_time - self.last_press_time[button_name] < self.DEBOUNCE_TIME:
            return
            
        self.last_press_time[button_name] = current_time
        
        # Map to friendly name if using aliases
        friendly_name = button_name
        for alias, btn in self.BUTTON_ALIASES.items():
            if btn == button_name:
                friendly_name = alias
                break
        
        print(f"Button pressed: {button_name} ({friendly_name})")
        
        # Call the callback with the friendly name
        if self.callback:
            self.callback(friendly_name)
            
    def _start_mock_input(self):
        """Start a thread to simulate button presses from keyboard (for testing)"""
        def input_loop():
            key_map = {
                'a': 'record',  # Button A
                'b': 'play',    # Button B
                'x': 'up',      # Button X
                'y': 'down',    # Button Y
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
            for btn in self.buttons.values():
                btn.close()
        print("Button handler cleanup complete")
