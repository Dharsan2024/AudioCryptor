"""
Steganography service for embedding and extracting messages in audio
"""

import struct
import numpy as np
import hashlib
import random
from typing import Tuple, Optional

from services.audio import AudioService
from utils.bytes import BitPacker, calculate_crc32
from utils.errors import StegoError


class StegoService:
    """Service for LSB steganography operations"""
    
    def __init__(self):
        self.audio_service = AudioService()
        self.magic_bytes = b'ASTG'  # Audio STеGanography
        self.version = 1
        self.header_size = 42  # Total header size in bytes
        
    def calculate_capacity(self, audio_file: str, lsb_bits: int = 1) -> int:
        """
        Calculate steganography capacity for an audio file
        
        Args:
            audio_file: Path to audio file
            lsb_bits: Number of LSB bits to use (1-2)
            
        Returns:
            Capacity in bytes (excluding header)
        """
        try:
            audio_data, sample_rate = self.audio_service.load_audio(audio_file)
            
            # Get total number of samples
            if len(audio_data.shape) == 1:
                total_samples = len(audio_data)
            else:
                total_samples = audio_data.shape[0] * audio_data.shape[1]
                
            # Calculate total bits available
            total_bits = total_samples * lsb_bits
            
            # Convert to bytes and subtract header size
            total_bytes = total_bits // 8
            available_bytes = max(0, total_bytes - self.header_size)
            
            return available_bytes
            
        except Exception as e:
            raise StegoError(f"Failed to calculate capacity: {str(e)}")
            
    def embed_message(self, audio_data: np.ndarray, encrypted_data: bytes,
                     salt: bytes, nonce: bytes, lsb_bits: int = 1, 
                     scatter: bool = True) -> np.ndarray:
        """
        Embed encrypted message in audio using LSB steganography
        
        Args:
            audio_data: Audio samples as numpy array
            encrypted_data: Encrypted message data
            salt: Salt for key derivation
            nonce: Nonce for encryption
            lsb_bits: Number of LSB bits to use
            scatter: Whether to scatter bits randomly
            
        Returns:
            Modified audio data with embedded message
        """
        try:
            # Create header
            header = self._create_header(salt, nonce, len(encrypted_data), lsb_bits, scatter)
            
            # Combine header and payload
            payload = header + encrypted_data
            
            # Check capacity
            total_samples = audio_data.size
            required_bits = len(payload) * 8
            available_bits = total_samples * lsb_bits
            
            if required_bits > available_bits:
                raise StegoError(
                    f"Insufficient capacity: need {required_bits} bits, "
                    f"but only {available_bits} available"
                )
                
            # Flatten audio data for easier processing
            original_shape = audio_data.shape
            flat_audio = audio_data.flatten().copy()
            
            # Convert payload to bits
            bit_packer = BitPacker()
            payload_bits = bit_packer.bytes_to_bits(payload)
            
            # Embed header bits first (always sequential)
            header_bits = payload_bits[:self.header_size * 8]
            payload_data_bits = payload_bits[self.header_size * 8:]
            
            # Embed header sequentially
            for i, bit in enumerate(header_bits):
                sample_idx = i
                sample = flat_audio[sample_idx]
                mask = ~((1 << lsb_bits) - 1)
                cleared_sample = sample & mask
                if bit:
                    new_sample = cleared_sample | 1
                else:
                    new_sample = cleared_sample
                flat_audio[sample_idx] = new_sample
            
            # Embed payload bits
            if scatter:
                payload_indices = self._generate_scatter_indices(
                    len(payload_data_bits), total_samples - self.header_size * 8, salt
                )
            
            for i, bit in enumerate(payload_data_bits):
                if scatter:
                    sample_idx = self.header_size * 8 + payload_indices[i]
                else:
                    sample_idx = self.header_size * 8 + i
                
                # Modify the LSBs of the sample
                sample = flat_audio[sample_idx]
                
                # Clear the specified number of LSBs
                mask = ~((1 << lsb_bits) - 1)
                cleared_sample = sample & mask
                
                # Set the new LSB value (for multi-bit LSB, we use just the lowest bit)
                if bit:
                    new_sample = cleared_sample | 1
                else:
                    new_sample = cleared_sample
                    
                flat_audio[sample_idx] = new_sample
                
            # Reshape back to original shape
            modified_audio = flat_audio.reshape(original_shape)
            
            return modified_audio
            
        except Exception as e:
            raise StegoError(f"Failed to embed message: {str(e)}")
            
    def extract_message(self, audio_data: np.ndarray) -> Tuple[bytes, bytes, bytes]:
        """
        Extract encrypted message from audio
        
        Args:
            audio_data: Audio samples with embedded message
            
        Returns:
            Tuple of (encrypted_data, salt, nonce)
        """
        try:
            # Flatten audio data
            flat_audio = audio_data.flatten()
            
            # Extract header first (try without scatter)
            header_bits_needed = self.header_size * 8
            header_bits = []
            
            for i in range(header_bits_needed):
                if i >= len(flat_audio):
                    raise StegoError("Audio file too short for header")
                sample = flat_audio[i]
                bit = sample & 1  # Extract LSB
                header_bits.append(bit)
                
            # Convert header bits to bytes
            bit_packer = BitPacker()
            header_bytes = bit_packer.bits_to_bytes(header_bits)
            
            # Parse header
            header_info = self._parse_header(header_bytes)
            
            # Extract payload based on header info
            payload_size = header_info['payload_length']
            lsb_bits = header_info['lsb_bits']
            scatter = header_info['scatter']
            salt = header_info['salt']
            nonce = header_info['nonce']
            
            # Calculate total bits needed
            total_bits_needed = (self.header_size + payload_size) * 8
            
            # Extract payload bits more efficiently
            payload_bits = []
            
            if scatter:
                # Generate scatter indices for payload only
                payload_indices = self._generate_scatter_indices(
                    payload_size * 8, len(flat_audio) - header_bits_needed, salt
                )
                # Extract payload bits using scatter pattern
                for idx in payload_indices:
                    actual_idx = header_bits_needed + idx
                    if actual_idx >= len(flat_audio):
                        raise StegoError("Audio file too short for complete message")
                    sample = flat_audio[actual_idx]
                    bit = sample & 1
                    payload_bits.append(bit)
            else:
                # Extract payload bits sequentially after header
                for i in range(payload_size * 8):
                    actual_idx = header_bits_needed + i
                    if actual_idx >= len(flat_audio):
                        raise StegoError("Audio file too short for complete message")
                    sample = flat_audio[actual_idx]
                    bit = sample & 1
                    payload_bits.append(bit)
                
            # Convert payload bits to bytes
            encrypted_data = bit_packer.bits_to_bytes(payload_bits)
            
            return encrypted_data, salt, nonce
            
        except Exception as e:
            raise StegoError(f"Failed to extract message: {str(e)}")
            
    def _create_header(self, salt: bytes, nonce: bytes, payload_length: int,
                      lsb_bits: int, scatter: bool) -> bytes:
        """Create steganography header"""
        try:
            # Create flags byte
            flags = lsb_bits & 0x03  # LSB bits in lower 2 bits
            if scatter:
                flags |= 0x04  # Scatter flag in bit 2
                
            # Pack header structure
            header = struct.pack(
                '>4s B B 16s 12s I',
                self.magic_bytes,     # Magic bytes (4)
                self.version,         # Version (1)
                flags,               # Flags (1)
                salt,                # Salt (16)
                nonce,               # Nonce (12)
                payload_length       # Payload length (4)
            )
            
            # Calculate and append CRC32
            crc32 = calculate_crc32(header)
            header += struct.pack('>I', crc32)
            
            return header
            
        except Exception as e:
            raise StegoError(f"Failed to create header: {str(e)}")
            
    def _parse_header(self, header_bytes: bytes) -> dict:
        """Parse steganography header"""
        try:
            if len(header_bytes) < self.header_size:
                raise StegoError("Header too short")
                
            # Extract header without CRC
            header_without_crc = header_bytes[:-4]
            
            # Verify CRC32
            expected_crc = calculate_crc32(header_without_crc)
            actual_crc = struct.unpack('>I', header_bytes[-4:])[0]
            
            if expected_crc != actual_crc:
                raise StegoError("Header CRC verification failed")
                
            # Unpack header
            magic, version, flags, salt, nonce, payload_length = struct.unpack(
                '>4s B B 16s 12s I', header_without_crc
            )
            
            # Verify magic bytes
            if magic != self.magic_bytes:
                raise StegoError("Invalid magic bytes - file not encoded with this tool")
                
            # Verify version
            if version != self.version:
                raise StegoError(f"Unsupported version: {version}")
                
            # Parse flags
            lsb_bits = flags & 0x03
            scatter = bool(flags & 0x04)
            
            if lsb_bits < 1 or lsb_bits > 3:
                raise StegoError(f"Invalid LSB bits: {lsb_bits}")
                
            return {
                'version': version,
                'lsb_bits': lsb_bits,
                'scatter': scatter,
                'salt': salt,
                'nonce': nonce,
                'payload_length': payload_length
            }
            
        except struct.error as e:
            raise StegoError(f"Header parsing failed: {str(e)}")
        except Exception as e:
            raise StegoError(f"Failed to parse header: {str(e)}")
            
    def _generate_scatter_indices(self, count: int, total_samples: int, 
                                 salt: bytes) -> list:
        """
        Generate pseudo-random indices for bit scattering
        
        Args:
            count: Number of indices needed
            total_samples: Total number of samples available
            salt: Salt for PRNG seeding
            
        Returns:
            List of sample indices
        """
        try:
            # Create deterministic seed from salt
            seed_data = salt + b"scatter"
            seed = int.from_bytes(hashlib.sha256(seed_data).digest()[:4], 'big')
            
            # Use random generator with fixed seed
            rng = random.Random(seed)
            
            # Generate unique random indices
            if count > total_samples:
                raise StegoError("Not enough samples for scatter pattern")
                
            indices = list(range(total_samples))
            rng.shuffle(indices)
            
            return indices[:count]
            
        except Exception as e:
            raise StegoError(f"Failed to generate scatter indices: {str(e)}")
            
    def analyze_audio_for_stego(self, audio_data: np.ndarray) -> dict:
        """
        Analyze audio for potential steganography presence
        
        Args:
            audio_data: Audio samples to analyze
            
        Returns:
            Dictionary with analysis results
        """
        try:
            # Basic analysis
            flat_audio = audio_data.flatten()
            
            # Check LSB distribution
            lsb_ones = np.sum(flat_audio & 1)
            lsb_zeros = len(flat_audio) - lsb_ones
            lsb_ratio = lsb_ones / len(flat_audio) if len(flat_audio) > 0 else 0
            
            # Check for header magic bytes
            has_header = False
            try:
                header_bits = []
                for i in range(min(self.header_size * 8, len(flat_audio))):
                    bit = flat_audio[i] & 1
                    header_bits.append(bit)
                    
                if len(header_bits) >= 32:  # At least magic bytes
                    bit_packer = BitPacker()
                    header_start = bit_packer.bits_to_bytes(header_bits[:32])
                    if header_start.startswith(self.magic_bytes):
                        has_header = True
            except:
                pass
                
            return {
                'total_samples': len(flat_audio),
                'lsb_ones_ratio': lsb_ratio,
                'lsb_distribution_suspicious': abs(lsb_ratio - 0.5) < 0.01,
                'has_stego_header': has_header,
                'estimated_capacity_1lsb': len(flat_audio) // 8 - self.header_size,
                'estimated_capacity_2lsb': len(flat_audio) // 4 - self.header_size
            }
            
        except Exception as e:
            return {'error': str(e)}
