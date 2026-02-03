#!/usr/bin/env python3
"""
Web Server for AudioPirate
Serves recordings directory over HTTP for easy file access
"""

import os
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socket


class RecordingsHTTPHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler for serving recordings"""
    
    def __init__(self, *args, directory=None, **kwargs):
        self.directory = directory
        super().__init__(*args, directory=directory, **kwargs)
        
    def log_message(self, format, *args):
        """Override to reduce log spam"""
        # Only log successful requests and errors (not favicon 404s)
        if args[0].startswith('GET /favicon.ico'):
            return  # Suppress favicon requests
        # Only log errors (not 2xx or 3xx responses)
        if args[1][0] in ['4', '5']:
            return  # Suppress error logs
        # Log successful file access
        if args[1][0] in ['2', '3']:
            print(f"Web: {args[0]} - {args[1]}")
            
    def handle(self):
        """Override handle to catch broken pipe errors"""
        try:
            super().handle()
        except (BrokenPipeError, ConnectionResetError):
            # Client disconnected - this is normal, ignore it
            pass


class WebServer:
    def __init__(self, directory="recordings", port=8000):
        """
        Initialize web server
        
        Args:
            directory: Directory to serve files from
            port: Port to listen on
        """
        self.directory = os.path.abspath(directory)
        self.port = port
        self.server = None
        self.thread = None
        self.running = False
        
        # Create directory if it doesn't exist
        os.makedirs(self.directory, exist_ok=True)
        
    def start(self):
        """Start the web server in a background thread"""
        if self.running:
            print("Web server already running")
            return
            
        try:
            # Create handler with directory
            handler = lambda *args, **kwargs: RecordingsHTTPHandler(
                *args, directory=self.directory, **kwargs
            )
            
            self.server = HTTPServer(('0.0.0.0', self.port), handler)
            self.running = True
            
            # Get local IP address
            hostname = socket.gethostname()
            try:
                local_ip = socket.gethostbyname(hostname)
            except:
                local_ip = "localhost"
            
            print(f"Web server started at http://{local_ip}:{self.port}")
            print(f"Serving files from: {self.directory}")
            
            # Start server in background thread
            self.thread = threading.Thread(target=self._run_server, daemon=True)
            self.thread.start()
            
        except OSError as e:
            print(f"Failed to start web server: {e}")
            print(f"Port {self.port} may already be in use")
            self.running = False
            
    def _run_server(self):
        """Run the HTTP server (called in thread)"""
        try:
            self.server.serve_forever()
        except Exception as e:
            print(f"Web server error: {e}")
        finally:
            self.running = False
            
    def stop(self):
        """Stop the web server"""
        if self.server:
            print("Stopping web server...")
            self.server.shutdown()
            self.server.server_close()
            self.running = False
            
            if self.thread:
                self.thread.join(timeout=2.0)
                
        print("Web server stopped")
        
    def get_url(self):
        """Get the server URL"""
        if self.running:
            hostname = socket.gethostname()
            try:
                local_ip = socket.gethostbyname(hostname)
            except:
                local_ip = "localhost"
            return f"http://{local_ip}:{self.port}"
        return None


if __name__ == "__main__":
    # Test the web server
    import time
    
    server = WebServer(directory="recordings", port=8000)
    server.start()
    
    try:
        print("Web server running. Press Ctrl+C to stop...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.stop()
