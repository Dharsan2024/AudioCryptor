"""
Audio service for loading, converting, and playing audio files
"""

import numpy as np
import wave
import os
import tempfile
from typing import Tuple, Optional

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    print("Warning: pydub not available. Only WAV files will be supported.")

try:
    import simpleaudio as sa
    SIMPLEAUDIO_AVAILABLE = True
except ImportError:
    SIMPLEAUDIO_AVAILABLE = False
    print("Warning: simpleaudio not available. Audio playback will be disabled.")

from utils.errors import StegoError


class AudioService:
    """Service for handling audio operations"""
    
    def __init__(self):
        self.current_playback = None
        
    def load_audio(self, file_path: str) -> Tuple[np.ndarray, int]:
        """
        Load audio file and return PCM data and sample rate
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Tuple of (audio_data, sample_rate)
            audio_data is numpy array of int16 samples
        """
        if not os.path.exists(file_path):
            raise StegoError(f"Audio file not found: {file_path}")
            
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.wav':
            return self._load_wav(file_path)
        elif file_ext in ['.mp3', '.flac', '.m4a', '.ogg']:
            if not PYDUB_AVAILABLE:
                raise StegoError(f"pydub not available for {file_ext} format")
            return self._load_with_pydub(file_path)
        else:
            raise StegoError(f"Unsupported audio format: {file_ext}")
            
    def _load_wav(self, file_path: str) -> Tuple[np.ndarray, int]:
        """Load WAV file directly"""
        try:
            with wave.open(file_path, 'rb') as wav_file:
                # Get parameters
                sample_rate = wav_file.getframerate()
                num_channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
                num_frames = wav_file.getnframes()
                
                # Read raw audio data
                raw_audio = wav_file.readframes(num_frames)
                
                # Convert to numpy array
                if sample_width == 1:
                    dtype = np.uint8
                elif sample_width == 2:
                    dtype = np.int16
                elif sample_width == 4:
                    dtype = np.int32
                else:
                    raise StegoError(f"Unsupported sample width: {sample_width}")
                    
                audio_data = np.frombuffer(raw_audio, dtype=dtype)
                
                # Reshape for multi-channel audio
                if num_channels > 1:
                    audio_data = audio_data.reshape(-1, num_channels)
                    
                # Convert to int16 if needed
                if dtype != np.int16:
                    if dtype == np.uint8:
                        audio_data = ((audio_data.astype(np.float32) - 128) * 256).astype(np.int16)
                    elif dtype == np.int32:
                        audio_data = (audio_data / 65536).astype(np.int16)
                        
                return audio_data, sample_rate
                
        except Exception as e:
            raise StegoError(f"Failed to load WAV file: {str(e)}")
            
    def _load_with_pydub(self, file_path: str) -> Tuple[np.ndarray, int]:
        """Load audio file using pydub and convert to WAV"""
        try:
            # Load with pydub
            from pydub import AudioSegment
            audio_segment = AudioSegment.from_file(file_path)
            
            # Convert to 16-bit PCM WAV format
            audio_segment = audio_segment.set_sample_width(2)  # 16-bit
            
            # Get sample rate
            sample_rate = audio_segment.frame_rate
            
            # Convert to numpy array
            raw_data = audio_segment.raw_data
            audio_data = np.frombuffer(raw_data, dtype=np.int16)
            
            # Reshape for stereo
            if audio_segment.channels > 1:
                audio_data = audio_data.reshape(-1, audio_segment.channels)
                
            return audio_data, sample_rate
            
        except Exception as e:
            raise StegoError(f"Failed to load audio file with pydub: {str(e)}")
            
    def save_audio(self, audio_data: np.ndarray, sample_rate: int, output_path: str) -> None:
        """
        Save audio data as WAV file
        
        Args:
            audio_data: Audio samples as numpy array
            sample_rate: Sample rate in Hz
            output_path: Output file path
        """
        try:
            # Ensure audio data is int16
            if audio_data.dtype != np.int16:
                audio_data = audio_data.astype(np.int16)
                
            # Determine number of channels
            if len(audio_data.shape) == 1:
                num_channels = 1
                frames = audio_data
            else:
                num_channels = audio_data.shape[1]
                frames = audio_data.flatten()
                
            # Write WAV file
            with wave.open(output_path, 'wb') as wav_file:
                wav_file.setnchannels(num_channels)
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(frames.tobytes())
                
        except Exception as e:
            raise StegoError(f"Failed to save audio file: {str(e)}")
            
    def get_audio_info(self, file_path: str) -> dict:
        """
        Get information about audio file
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Dictionary with audio information
        """
        try:
            audio_data, sample_rate = self.load_audio(file_path)
            
            if len(audio_data.shape) == 1:
                num_channels = 1
                num_frames = len(audio_data)
            else:
                num_channels = audio_data.shape[1]
                num_frames = audio_data.shape[0]
                
            duration = num_frames / sample_rate
            
            return {
                'sample_rate': sample_rate,
                'channels': num_channels,
                'frames': num_frames,
                'duration': duration,
                'format': 'PCM 16-bit'
            }
            
        except Exception as e:
            raise StegoError(f"Failed to get audio info: {str(e)}")
            
    def start_playback(self, audio_data: np.ndarray, sample_rate: int, volume: float = 1.0) -> None:
        """
        Start audio playback
        
        Args:
            audio_data: Audio samples
            sample_rate: Sample rate
            volume: Volume level (0.0 to 1.0)
        """
        if not SIMPLEAUDIO_AVAILABLE:
            raise StegoError("Audio playback not available (simpleaudio not installed)")
            
        try:
            # Stop any current playback
            self.stop_playback()
            
            # Apply volume
            if volume != 1.0:
                audio_data = (audio_data * volume).astype(np.int16)
                
            # Ensure correct format for playback
            if len(audio_data.shape) == 1:
                # Mono audio
                num_channels = 1
                playback_data = audio_data
            else:
                # Multi-channel audio
                num_channels = audio_data.shape[1]
                playback_data = audio_data.flatten()
                
            # Start playback
            import simpleaudio as sa
            self.current_playback = sa.play_buffer(
                playback_data.tobytes(),
                num_channels=num_channels,
                bytes_per_sample=2,
                sample_rate=sample_rate
            )
            
        except Exception as e:
            raise StegoError(f"Failed to start playback: {str(e)}")
            
    def stop_playback(self) -> None:
        """Stop current audio playback"""
        try:
            if self.current_playback and self.current_playback.is_playing():
                self.current_playback.stop()
            self.current_playback = None
        except:
            # Ignore errors when stopping playback
            pass
            
    def is_playing(self) -> bool:
        """Check if audio is currently playing"""
        try:
            return (self.current_playback is not None and 
                   self.current_playback.is_playing())
        except:
            return False
            
    def convert_to_wav(self, input_path: str, output_path: str) -> None:
        """
        Convert audio file to WAV format
        
        Args:
            input_path: Input audio file path
            output_path: Output WAV file path
        """
        try:
            audio_data, sample_rate = self.load_audio(input_path)
            self.save_audio(audio_data, sample_rate, output_path)
        except Exception as e:
            raise StegoError(f"Failed to convert audio: {str(e)}")
