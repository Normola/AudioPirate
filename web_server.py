#!/usr/bin/env python3
"""
Web Server for AudioPirate
Serves recordings directory over HTTP and provides live audio streaming with authentication
"""

import os
import threading
import time
import wave
import io
import json
import secrets
import hashlib
import ssl
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import socket

try:
    import alsaaudio
    ALSA_AVAILABLE = True
except ImportError:
    ALSA_AVAILABLE = False


class RecordingsHTTPHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler for serving recordings and live audio stream"""
    
    # Class-level storage for authentication
    auth_tokens = {}
    password_hash = None
    
    def __init__(self, *args, directory=None, audio_device='mic_with_gain', **kwargs):
        self.directory = directory
        self.audio_device = audio_device
        super().__init__(*args, directory=directory, **kwargs)
        
    def log_message(self, format, *args):
        """Override to reduce log spam"""
        if args[0].startswith('GET /favicon.ico'):
            return
        if args[1][0] in ['4', '5']:
            return
        if args[1][0] in ['2', '3']:
            print(f"Web: {args[0]} - {args[1]}")
            
    def handle(self):
        """Override handle to catch broken pipe errors"""
        try:
            super().handle()
        except (BrokenPipeError, ConnectionResetError):
            pass
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/live':
            self.serve_live_page()
        elif self.path.startswith('/stream_audio'):
            if self.check_auth():
                self.stream_audio()
            else:
                self.send_error(401, 'Unauthorized')
        else:
            super().do_GET()
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/authenticate':
            self.handle_authentication()
        else:
            self.send_error(404, 'Not found')
    
    def check_auth(self):
        """Check if request has valid authentication token"""
        if '?' in self.path:
            query = self.path.split('?', 1)[1]
            params = dict(param.split('=') for param in query.split('&') if '=' in param)
            token = params.get('token', '')
            
            if token in self.auth_tokens:
                if time.time() < self.auth_tokens[token]:
                    return True
                else:
                    del self.auth_tokens[token]
        return False
    
    def handle_authentication(self):
        """Handle password authentication"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)
            password = data.get('password', '')
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            if password_hash == self.password_hash:
                token = secrets.token_urlsafe(32)
                expiry = time.time() + (24 * 60 * 60)
                self.auth_tokens[token] = expiry
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = json.dumps({'success': True, 'token': token})
                self.wfile.write(response.encode())
            else:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = json.dumps({'success': False, 'message': 'Invalid password'})
                self.wfile.write(response.encode())
        except Exception as e:
            print(f"Authentication error: {e}")
            self.send_error(500, 'Authentication error')
    
    def serve_live_page(self):
        """Serve the live stream HTML page"""
        html_file = Path(__file__).parent / 'templates' / 'live_stream.html'
        
        if html_file.exists():
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open(html_file, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404, 'Live stream page not found')
    
    def stream_audio(self):
        """Stream live audio from microphones"""
        if not ALSA_AVAILABLE:
            self.send_error(503, 'ALSA not available - cannot stream audio')
            return
        
        try:
            pcm = alsaaudio.PCM(
                alsaaudio.PCM_CAPTURE,
                alsaaudio.PCM_NORMAL,
                device=self.audio_device
            )
            pcm.setchannels(2)
            pcm.setrate(48000)
            pcm.setformat(alsaaudio.PCM_FORMAT_S16_LE)
            pcm.setperiodsize(2048)
            
            self.send_response(200)
            self.send_header('Content-Type', 'audio/wav')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'close')
            self.end_headers()
            
            wav_header = self._create_wav_header(48000, 2, 16)
            self.wfile.write(wav_header)
            
            print("Starting audio stream...")
            try:
                while True:
                    length, data = pcm.read()
                    if length > 0:
                        self.wfile.write(data)
                        self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                print("Client disconnected from audio stream")
            finally:
                pcm.close()
        except alsaaudio.ALSAAudioError as e:
            print(f"ALSA error during streaming: {e}")
            self.send_error(500, f'Audio streaming error: {e}')
        except Exception as e:
            print(f"Error streaming audio: {e}")
    
    def _create_wav_header(self, sample_rate, channels, bits_per_sample):
        """Create a WAV file header for streaming"""
        data_size = 0xFFFFFFFF - 36
        header = io.BytesIO()
        header.write(b'RIFF')
        header.write((data_size + 36).to_bytes(4, 'little'))
        header.write(b'WAVE')
        header.write(b'fmt ')
        header.write((16).to_bytes(4, 'little'))
        header.write((1).to_bytes(2, 'little'))
        header.write(channels.to_bytes(2, 'little'))
        header.write(sample_rate.to_bytes(4, 'little'))
        byte_rate = sample_rate * channels * bits_per_sample // 8
        header.write(byte_rate.to_bytes(4, 'little'))
        block_align = channels * bits_per_sample // 8
        header.write(block_align.to_bytes(2, 'little'))
        header.write(bits_per_sample.to_bytes(2, 'little'))
        header.write(b'data')
        header.write(data_size.to_bytes(4, 'little'))
        return header.getvalue()


class WebServer:
    def __init__(self, directory="recordings", port=8000, audio_device='mic_with_gain', password='audiopirate', use_ssl=True):
        """
        Initialize web server
        
        Args:
            directory: Directory to serve files from
            port: Port to listen on
            audio_device: ALSA device for audio streaming
            password: Password for live stream access
            use_ssl: Enable HTTPS with self-signed certificate
        """
        self.directory = os.path.abspath(directory)
        self.port = port
        self.audio_device = audio_device
        self.password = password
        self.use_ssl = use_ssl
        self.cert_file = 'audiopirate.crt'
        self.key_file = 'audiopirate.key'
        self.server = None
        self.thread = None
        self.running = False
        os.makedirs(self.directory, exist_ok=True)
        
    def start(self):
        """Start the web server in a background thread"""
        if self.running:
            print("Web server already running")
            return
            
        try:
            # Generate SSL certificates if needed
            if self.use_ssl:
                self._ensure_certificates()
            
            RecordingsHTTPHandler.password_hash = hashlib.sha256(self.password.encode()).hexdigest()
            
            handler = lambda *args, **kwargs: RecordingsHTTPHandler(
                *args, directory=self.directory, audio_device=self.audio_device, **kwargs
            )
            
            self.server = HTTPServer(('0.0.0.0', self.port), handler)
            
            # Wrap with SSL if enabled
            if self.use_ssl:
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                context.load_cert_chain(self.cert_file, self.key_file)
                self.server.socket = context.wrap_socket(self.server.socket, server_side=True)
            
            self.running = True
            
            hostname = socket.gethostname()
            try:
                local_ip = socket.gethostbyname(hostname)
            except:
                local_ip = "localhost"
            
            protocol = "https" if self.use_ssl else "http"
            print(f"Web server started at {protocol}://{local_ip}:{self.port}")
            print(f"Live stream available at {protocol}://{local_ip}:{self.port}/live")
            print(f"Stream password: {self.password}")
            if self.use_ssl:
                print(f"⚠️  Using self-signed certificate - browsers will show security warning")
            print(f"Serving files from: {self.directory}")
            
            self.thread = threading.Thread(target=self._run_server, daemon=True)
            self.thread.start()
        except OSError as e:
            print(f"Failed to start web server: {e}")
            print(f"Port {self.port} may already be in use")
            self.running = False
            
    def _ensure_certificates(self):
        """Generate self-signed SSL certificates if they don't exist"""
        if os.path.exists(self.cert_file) and os.path.exists(self.key_file):
            return
        
        print("Generating self-signed SSL certificate...")
        try:
            import subprocess
            # Generate private key and certificate
            subprocess.run([
                'openssl', 'req', '-x509', '-newkey', 'rsa:4096',
                '-keyout', self.key_file,
                '-out', self.cert_file,
                '-days', '365', '-nodes',
                '-subj', '/CN=AudioPirate/O=AudioPirate/C=US'
            ], check=True, capture_output=True)
            print(f"✓ SSL certificate generated: {self.cert_file}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to generate certificate with openssl: {e}")
            print("Falling back to Python certificate generation...")
            self._generate_cert_python()
        except FileNotFoundError:
            print("OpenSSL not found, using Python certificate generation...")
            self._generate_cert_python()
    
    def _generate_cert_python(self):
        """Generate certificate using pure Python (fallback)"""
        try:
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.primitives import serialization
            import datetime
            
            # Generate private key
            key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
            
            # Generate certificate
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "AudioPirate"),
                x509.NameAttribute(NameOID.COMMON_NAME, "AudioPirate"),
            ])
            
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.datetime.utcnow()
            ).not_valid_after(
                datetime.datetime.utcnow() + datetime.timedelta(days=365)
            ).sign(key, hashes.SHA256())
            
            # Write private key
            with open(self.key_file, "wb") as f:
                f.write(key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            # Write certificate
            with open(self.cert_file, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            
            print(f"✓ SSL certificate generated: {self.cert_file}")
        except ImportError:
            print("⚠️  cryptography module not installed. Install with: pip install cryptography")
            print("   Falling back to HTTP (no SSL)")
            self.use_ssl = False
        except Exception as e:
            print(f"Failed to generate certificate: {e}")
            print("Falling back to HTTP (no SSL)")
            self.use_ssl = False
    
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
            protocol = "https" if self.use_ssl else "http"
            return f"{protocol}://{local_ip}:{self.port}"
        return None


if __name__ == "__main__":
    import time
    server = WebServer(directory="recordings", port=8000, use_ssl=True)
    server.start()
    try:
        print("Web server running. Press Ctrl+C to stop...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.stop()
