# AudioPirate Changelog

## Latest Updates

### Screen Timeout Feature
- **Auto-sleep after 20 seconds**: Display backlight automatically turns off after 20 seconds of inactivity
- **Wake on button press**: Any button press wakes the display and resets the timer
- **Configurable timeout**: Change `timeout_seconds` in Display class `__init__` to adjust duration
- **Power saving**: Reduces power consumption and extends display lifespan

### Implementation Details
- Added timeout tracking to [display.py](display.py):
  - `set_backlight(state)` - Control backlight on/off
  - `reset_timeout()` - Reset inactivity timer (called on button press)
  - `check_timeout()` - Check if timeout reached (called in main loop)
- Modified [main.py](main.py):
  - Button press handler calls `display.reset_timeout()`
  - Main loop calls `display.check_timeout()` every 100ms
- Backlight state preserved across screen updates

### WebSocket Streaming Fixes
- Fixed duplicate variable declarations in [templates/live_stream.html](templates/live_stream.html)
- Removed code fragments from previous HTTP streaming attempt
- Clean WebSocket + Web Audio API implementation
- All syntax errors resolved

### Bug Fixes
- Fixed type error: `recording_name` can be None, now uses `self.recording_name or ""`
- Removed malformed code from multiple edits in live_stream.html
- Cleaned up event handler code

## Configuration

### Adjust Screen Timeout
Edit [display.py](display.py), line ~25:
```python
self.timeout_seconds = 20  # Change to desired seconds
```

### Disable Screen Timeout
Set to a very high value:
```python
self.timeout_seconds = 3600  # 1 hour
```

Or comment out the check in [main.py](main.py):
```python
# self.display.check_timeout()
```

## Testing
- Screen should turn off after 20 seconds of no button activity
- Any button press (A, B, X, Y) should wake the screen immediately
- Display shows "Display backlight ON/OFF" messages in console
- Mock mode logs: `[MOCK] Backlight: ON/OFF`
