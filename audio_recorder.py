#!/usr/bin/env python3
"""
Audio Recorder for AudioPirate
Handles audio recording and playback using PyAudio
"""

try:
    import pyaudio
    import wave
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("Warning: PyAudio not installed. Audio will run in mock mode.")

import threading
import time
import os


class AudioRecorder:
    # Audio configuration
    CHUNK = 1024
    FORMAT = None  # Will be set based on pyaudio availability
    CHANNELS = 2
    RATE = 44100
    
    def __init__(self, output_dir="recordings"):
        """Initialize audio recorder"""
        self.output_dir = output_dir
        self.recording = False
        self.recording_thread = None
        self.frames = []
        self.current_filename = None
        self.recording_start_time = None
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        if AUDIO_AVAILABLE:
            try:
                self.audio = pyaudio.PyAudio()
                self.FORMAT = pyaudio.paInt16
                
                # Get default input device info
                default_input = self.audio.get_default_input_device_info()
                print(f"Default audio input: {default_input['name']}")
                print(f"Audio recorder initialized: {self.RATE}Hz, {self.CHANNELS} channels")
            except Exception as e:
                print(f"Failed to initialize PyAudio: {e}")
                print("Running in mock mode")
                self.audio = None
        else:
            self.audio = None
            print("Audio recorder running in mock mode")
            
    def start_recording(self, filename):
        """Start recording audio to a file"""
        if self.recording:
            print("Already recording!")
            return False
            
        self.current_filename = os.path.join(self.output_dir, filename)
        self.frames = []
        self.recording = True
        self.recording_start_time = time.time()
        
        if self.audio:
            # Start recording in a separate thread
            self.recording_thread = threading.Thread(target=self._record_audio)
            self.recording_thread.start()
        else:
            # Mock mode
            print(f"[AUDIO] Started recording to {self.current_filename}")
            
        return True
        
    def _record_audio(self):
        """Internal method to record audio in a thread"""
        try:
            stream = self.audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK
            )
            
            print(f"Recording to {self.current_filename}...")
            
            while self.recording:
                try:
                    data = stream.read(self.CHUNK, exception_on_overflow=False)
                    self.frames.append(data)
                except Exception as e:
                    print(f"Error reading audio: {e}")
                    break
                    
            # Stop and close the stream
            stream.stop_stream()
            stream.close()
            
        except Exception as e:
            print(f"Recording error: {e}")
            
    def stop_recording(self):
        """Stop recording and save to file"""
        if not self.recording:
            print("Not currently recording!")
            return False
            
        self.recording = False
        
        if self.audio and self.recording_thread:
            # Wait for recording thread to finish
            self.recording_thread.join(timeout=2.0)
            
            # Save the recorded audio to a WAV file
            try:
                wf = wave.open(self.current_filename, 'wb')
                wf.setnchannels(self.CHANNELS)
                wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
                wf.setframerate(self.RATE)
                wf.writeframes(b''.join(self.frames))
                wf.close()
                
                file_size = os.path.getsize(self.current_filename)
                print(f"Saved recording: {self.current_filename} ({file_size} bytes)")
                
            except Exception as e:
                print(f"Error saving audio file: {e}")
                return False
        else:
            # Mock mode
            duration = time.time() - self.recording_start_time
            print(f"[AUDIO] Stopped recording after {duration:.1f}s, saved to {self.current_filename}")
            
        return True
        
    def play_audio(self, filename):
        """Play an audio file"""
        filepath = os.path.join(self.output_dir, filename)
        
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            return False
            
        if self.audio:
            try:
                # Open the wave file
                wf = wave.open(filepath, 'rb')
                
                # Open stream
                stream = self.audio.open(
                    format=self.audio.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True
                )
                
                print(f"Playing {filepath}...")
                
                # Read and play data
                data = wf.readframes(self.CHUNK)
                while data:
                    stream.write(data)
                    data = wf.readframes(self.CHUNK)
                    
                # Clean up
                stream.stop_stream()
                stream.close()
                wf.close()
                
                print("Playback finished")
                return True
                
            except Exception as e:
                print(f"Playback error: {e}")
                return False
        else:
            # Mock mode
            print(f"[AUDIO] Playing {filepath}")
            time.sleep(2)  # Simulate playback
            print(f"[AUDIO] Playback finished")
            return True
            
    def get_recording_duration(self):
        """Get current recording duration in seconds"""
        if self.recording and self.recording_start_time:
            return time.time() - self.recording_start_time
        return 0.0
        
    def list_recordings(self):
        """List all recordings in the output directory"""
        recordings = []
        if os.path.exists(self.output_dir):
            for file in os.listdir(self.output_dir):
                if file.endswith('.wav'):
                    filepath = os.path.join(self.output_dir, file)
                    size = os.path.getsize(filepath)
                    recordings.append({
                        'filename': file,
                        'size': size,
                        'path': filepath
                    })
        return recordings
        
    def cleanup(self):
        """Clean up audio resources"""
        if self.recording:
            self.stop_recording()
            
        if self.audio:
            self.audio.terminate()
            
        print("Audio recorder cleanup complete")
