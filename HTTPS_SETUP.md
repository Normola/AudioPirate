# HTTPS Configuration for AudioPirate

## HTTPS is Now Enabled by Default! 🔒

The web server now uses HTTPS with self-signed SSL certificates for encrypted communication.

## How It Works

1. **Automatic Certificate Generation**: On first run, the server generates a self-signed SSL certificate
2. **OpenSSL First**: Tries to use system OpenSSL for certificate generation
3. **Python Fallback**: If OpenSSL isn't available, uses Python's `cryptography` module
4. **HTTP Fallback**: If neither works, falls back to HTTP

## Browser Security Warning

⚠️ **You will see a security warning in your browser** because the certificate is self-signed (not from a trusted authority).

### To Access the Site:

**Chrome/Edge:**
1. Click "Advanced"
2. Click "Proceed to [site] (unsafe)"

**Firefox:**
1. Click "Advanced"
2. Click "Accept the Risk and Continue"

**Safari:**
1. Click "Show Details"
2. Click "visit this website"

This is **normal and safe** for a local device on your own network.

## Using HTTP Instead (Optional)

If you prefer to use HTTP without encryption, edit `main.py`:

```python
self.web_server = WebServer(
    directory="recordings",
    port=8000,
    password='audiopirate',
    use_ssl=False  # Disable HTTPS
)
```

## Installing Cryptography Module

For Python-based certificate generation, install:

```bash
pip install cryptography
```

## Certificate Files

- `audiopirate.crt` - SSL certificate (365 day validity)
- `audiopirate.key` - Private key

These files are generated automatically and saved in the project directory.

## Production Deployment

For production use with a domain name, consider using Let's Encrypt for free, trusted certificates:
- https://letsencrypt.org/
- Use certbot: `sudo apt-get install certbot`

## Security Benefits

✅ Encrypted communication between browser and device
✅ Password authentication over secure connection  
✅ Protects audio stream from eavesdropping on local network
