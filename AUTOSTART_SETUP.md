# Auto-Start Setup for Raspberry Pi

This guide explains how to configure AudioPirate to automatically start when your Raspberry Pi boots.

## Method 1: systemd Service (Recommended)

### Installation Steps

1. **Update the service file paths** (if needed):
   
   Edit `audiopirate.service` and ensure the paths match your installation:
   - Update `User=pi` if using a different username
   - Update `WorkingDirectory=/home/pi/AudioPirate` to your actual path
   - Update `ExecStart=/home/pi/AudioPirate/start.sh` to your actual path

2. **Copy the service file to systemd**:
   ```bash
   sudo cp audiopirate.service /etc/systemd/system/
   ```

3. **Reload systemd to recognize the new service**:
   ```bash
   sudo systemctl daemon-reload
   ```

4. **Enable the service to start on boot**:
   ```bash
   sudo systemctl enable audiopirate.service
   ```

5. **Start the service now** (optional, to test):
   ```bash
   sudo systemctl start audiopirate.service
   ```

### Managing the Service

**Check status**:
```bash
sudo systemctl status audiopirate.service
```

**View logs**:
```bash
sudo journalctl -u audiopirate.service -f
```

**Stop the service**:
```bash
sudo systemctl stop audiopirate.service
```

**Restart the service**:
```bash
sudo systemctl restart audiopirate.service
```

**Disable auto-start**:
```bash
sudo systemctl disable audiopirate.service
```

## Method 2: Cron @reboot (Alternative)

If you prefer a simpler approach:

1. **Edit crontab**:
   ```bash
   crontab -e
   ```

2. **Add this line**:
   ```bash
   @reboot sleep 30 && /home/pi/AudioPirate/start.sh
   ```
   
   The `sleep 30` gives the system time to fully initialize networking and audio.

## Method 3: rc.local (Legacy)

For older Raspberry Pi OS versions:

1. **Edit rc.local**:
   ```bash
   sudo nano /etc/rc.local
   ```

2. **Add before `exit 0`**:
   ```bash
   # Start AudioPirate
   su - pi -c "/home/pi/AudioPirate/start.sh" &
   ```

## Troubleshooting

### Service won't start
- Check logs: `sudo journalctl -u audiopirate.service -n 50`
- Verify paths in the service file are correct
- Ensure start.sh has execute permissions: `chmod +x start.sh`
- Check that virtual environment exists: `ls -la .venv`

### Network services (ngrok) fail
- The service starts after `network.target`, but some network services may need more time
- Add `ExecStartPre=/bin/sleep 10` to the `[Service]` section in audiopirate.service

### Permission issues
- Ensure the `User=` in the service file matches your username
- Verify user has access to audio devices: `groups` should include `audio`

### Audio device not ready
- Add `sleep 5` at the start of start.sh to wait for audio hardware
- Or modify the service to depend on `sound.target`

## Verification

After setup, reboot your Pi:
```bash
sudo reboot
```

Wait 1-2 minutes, then check if the service is running:
```bash
sudo systemctl status audiopirate.service
```

The display should show the AudioPirate interface, and you can access the web interface via ngrok URLs.
