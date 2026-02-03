"""
Audio Recorder for ADAU7002 Dual Microphone Board using ALSA
Records stereo audio at 48kHz with 32-bit samples
"""

import os
import wave
import time
import threading
from datetime import datetime
from pathlib import Path

try:
    import alsaaudio
    ALSA_AVAILABLE = True
except ImportError:
    ALSA_AVAILABLE = False
    print("Warning: alsaaudio not available, running in mock mode")


class AudioRecorder:
    """Audio recorder using ALSA for ADAU7002 dual microphone board"""
    
    def __init__(self, recordings_dir="recordings", device="mic_with_gain"):
        """
        Initialize the audio recorder
        
        Args:
            recordings_dir: Directory to save recordings
            device: ALSA device name (default: mic_with_gain for gain control)
                   Use 'hw:0,0' for direct hardware access without gain
        """
        self.recordings_dir = Path(recordings_dir)
        self.recordings_dir.mkdir(exist_ok=True)
        
        # Audio configuration for ADAU7002
        self.device = device
        self.sample_rate = 48000
        self.channels = 2
        self.format = alsaaudio.PCM_FORMAT_S32_LE if ALSA_AVAILABLE else None
        self.chunk_size = 2048
        
        # Recording state
        self.is_recording = False
        self.recording_thread = None
        self.pcm = None
        self.wav_file = None
        self.current_filename = None
        self.frames = []
        self.start_time = None
        
    def start_recording(self, filename=None):
        """
        Start recording audio
        
        Args:
            filename: Optional filename (without extension). If None, generates timestamp-based name
            
        Returns:
            str: Path to the recording file
        """
        if self.is_recording:
            print("Already recording")
            return None
            
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recording_{timestamp}"
        
        # Ensure .wav extension
        if not filename.endswith('.wav'):
            filename += '.wav'
            
        self.current_filename = self.recordings_dir / filename
        
        if ALSA_AVAILABLE:
            try:
                # Initialize ALSA PCM device
                self.pcm = alsaaudio.PCM(
                    alsaaudio.PCM_CAPTURE,
                    alsaaudio.PCM_NORMAL,
                    device=self.device
                )
                
                # Set attributes
                self.pcm.setchannels(self.channels)
                self.pcm.setrate(self.sample_rate)
                self.pcm.setformat(self.format)
                self.pcm.setperiodsize(self.chunk_size)
                
                print(f"ALSA device configured: {self.device}")
                
            except alsaaudio.ALSAAudioError as e:
                print(f"Error initializing ALSA device: {e}")
                return None
        else:
            print("Mock mode: Simulating ALSA recording")
        
        # Initialize WAV file
        self.wav_file = wave.open(str(self.current_filename), 'wb')
        self.wav_file.setnchannels(self.channels)
        self.wav_file.setsampwidth(4)  # 32-bit = 4 bytes
        self.wav_file.setframerate(self.sample_rate)
        
        self.frames = []
        self.is_recording = True
        self.start_time = time.time()
        # Start recording thread
        if ALSA_AVAILABLE:
            self.recording_thread = threading.Thread(target=self._record_loop, daemon=True)
            self.recording_thread.start()
        
        print(f"Recording started: {self.current_filename}")
        return str(self.current_filename)
    
    def _record_loop(self):
        """Continuous recording loop (runs in thread)"""
        while self.is_recording:
            try:
                # Read audio data from ALSA device
                length, data = self.pcm.read()
                if length > 0:
                    self.frames.append(data)
                    if self.wav_file:
                        self.wav_file.writeframes(data)
            except alsaaudio.ALSAAudioError as e:
                print(f"ALSA read error: {e}")
                time.sleep(0.01)
            except Exception as e:
                print(f"Recording error: {e}")
                break
    
    def stop_recording(self):
        """Stop recording and save the file"""
        if not self.is_recording:
            print("Not currently recording")
            return None
        
        self.is_recording = False
        duration = time.time() - self.start_time if self.start_time else 0
        
        # Wait for recording thread to finish
        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join(timeout=2.0)
        
        # Close WAV file
        if self.wav_file:
            self.wav_file.close()
            self.wav_file = None
        
        # Close ALSA device
        if ALSA_AVAILABLE and self.pcm:
            self.pcm.close()
            self.pcm = None
        
        # Get file size
        file_size = 0
        if self.current_filename and self.current_filename.exists():
            file_size = self.current_filename.stat().st_size
        
        metadata = {
            'filename': str(self.current_filename),
            'duration': round(duration, 2),
            'size': file_size,
            'sample_rate': self.sample_rate,
            'channels': self.channels
        }
        
        print(f"Recording stopped: {metadata['filename']} ({metadata['duration']}s, {metadata['size']} bytes)")
        
        self.frames = []
        self.start_time = None
        
        return metadata
    
    def get_recording_duration(self):
        """
        Get current recording duration
        
        Returns:
            float: Duration in seconds, or None if not recording
        """
        if not self.is_recording or not self.start_time:
            return None
        return time.time() - self.start_time
    
    def set_gain(self, percent):
        """
        Set microphone gain level (0-100%)
        Requires asound.conf with softvol plugin
        
        Args:
            percent: Gain level 0-100
                    0% = -5dB, 50% = ~7.5dB, 100% = +20dB
        
        Returns:
            bool: True if successful
        """
        if not ALSA_AVAILABLE:
            print("ALSA not available, cannot set gain")
            return False
        
        try:
            import subprocess
            result = subprocess.run(
                ['amixer', '-c', '0', 'set', 'Mic Boost', f'{percent}%'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"Mic gain set to {percent}%")
                return True
            else:
                print(f"Failed to set gain: {result.stderr}")
                return False
        except Exception as e:
            print(f"Error setting gain: {e}")
            return False
    
    def get_gain(self):
        """
        Get current microphone gain level
        
        Returns:
            int: Current gain percentage (0-100), or None if unavailable
        """
        if not ALSA_AVAILABLE:
            return None
        
        try:
            import subprocess
            result = subprocess.run(
                ['amixer', '-c', '0', 'get', 'Mic Boost'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                import re
                match = re.search(r'\[(\d+)%\]', result.stdout)
                if match:
                    return int(match.group(1))
            return None
        except Exception as e:
            print(f"Error getting gain: {e}")
            return None
    
    def list_recordings(self):
        """
        List all recordings in the recordings directory
        
        Returns:
            list: List of recording metadata dictionaries
        """
        recordings = []
        
        if not self.recordings_dir.exists():
            return recordings
        
        for file_path in sorted(self.recordings_dir.glob('*.wav')):
            try:
                with wave.open(str(file_path), 'rb') as wf:
                    frames = wf.getnframes()
                    rate = wf.getframerate()
                    duration = frames / float(rate) if rate > 0 else 0
                    
                    recordings.append({
                        'filename': file_path.name,
                        'path': str(file_path),
                        'size': file_path.stat().st_size,
                        'duration': round(duration, 2),
                        'sample_rate': rate,
                        'channels': wf.getnchannels(),
                        'modified': datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    })
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        
        return recordings
    
    def cleanup(self):
        """Clean up resources"""
        if self.is_recording:
            self.stop_recording()
        
        if self.wav_file:
            self.wav_file.close()
            self.wav_file = None
        
        if ALSA_AVAILABLE and self.pcm:
            self.pcm.close()
            self.pcm = None
        
        print("Audio recorder cleanup complete")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()
        return False


if __name__ == "__main__":
    # Example usage
    print("Audio Recorder Test")
    print(f"ALSA Available: {ALSA_AVAILABLE}")
    
    with AudioRecorder() as recorder:
        # List existing recordings
        recordings = recorder.list_recordings()
        print(f"\nExisting recordings: {len(recordings)}")
        for rec in recordings:
            print(f"  - {rec['filename']}: {rec['duration']}s ({rec['size']} bytes)")
        
        # Test recording (mock mode if ALSA not available)
        print("\nStarting 3-second test recording...")
        recorder.start_recording("test_recording")
        
        # In a real application, you would call _record_chunk() in a loop
        # or use threading to continuously record
        for i in range(150):  # ~3 seconds at 2048 chunk size
            if not recorder._record_chunk():
                break
            
            # Print progress every second
            duration = recorder.get_recording_duration()
            if duration and int(duration) != int(duration - 0.02):
                print(f"Recording... {duration:.1f}s")
        
        metadata = recorder.stop_recording()
        print(f"\nRecording complete: {metadata}")
