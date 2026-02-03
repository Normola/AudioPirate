# Password Authentication Configuration

The live stream webpage now requires password authentication!

## Default Password
**Default password: `audiopirate`**

⚠️ **IMPORTANT**: Change this password for production use!

## How to Change the Password

Edit `main.py` and modify the WebServer initialization:

```python
self.web_server = WebServer(
    directory="recordings", 
    port=8000,
    password='your-secure-password-here'  # Change this!
)
```

## How Authentication Works

1. User visits `/live` endpoint
2. Password login screen appears
3. User enters password
4. Server validates password (SHA-256 hash)
5. Server generates secure token (valid for 24 hours)
6. Token is used for audio streaming requests

## Security Features

- Passwords are never sent in plain text (hashed with SHA-256)
- Authentication tokens expire after 24 hours
- Tokens are cryptographically secure (secrets.token_urlsafe)
- Stream requests require valid token in query parameter

## Accessing the Live Stream

1. Navigate to: `http://<pi-ip>:8000/live`
2. Enter password: `audiopirate` (or your custom password)
3. Click "Start Stream" to begin listening
4. Use "Logout" button to end session

## File Recording Access

File browsing at `http://<pi-ip>:8000/` does NOT require authentication.
Only the live audio stream (`/live` and `/stream_audio`) is protected.
