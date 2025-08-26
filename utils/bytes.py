"""
Utility functions for byte and bit manipulation
"""

import struct
import zlib
from typing import List


class BitPacker:
    """Utility class for packing and unpacking bits"""
    
    @staticmethod
    def bytes_to_bits(data: bytes) -> List[int]:
        """
        Convert bytes to list of bits (MSB first)
        
        Args:
            data: Byte data to convert
            
        Returns:
            List of bits (0 or 1)
        """
        bits = []
        for byte in data:
            for i in range(8):
                bit = (byte >> (7 - i)) & 1
                bits.append(bit)
        return bits
        
    @staticmethod
    def bits_to_bytes(bits: List[int]) -> bytes:
        """
        Convert list of bits to bytes (MSB first)
        
        Args:
            bits: List of bits (0 or 1)
            
        Returns:
            Byte data
        """
        # Pad bits to multiple of 8
        while len(bits) % 8 != 0:
            bits.append(0)
            
        bytes_data = bytearray()
        for i in range(0, len(bits), 8):
            byte = 0
            for j in range(8):
                if i + j < len(bits):
                    byte |= bits[i + j] << (7 - j)
            bytes_data.append(byte)
            
        return bytes(bytes_data)
        
    @staticmethod
    def int_to_bits(value: int, bit_count: int) -> List[int]:
        """
        Convert integer to list of bits with specified bit count
        
        Args:
            value: Integer value to convert
            bit_count: Number of bits to use
            
        Returns:
            List of bits (MSB first)
        """
        bits = []
        for i in range(bit_count):
            bit = (value >> (bit_count - 1 - i)) & 1
            bits.append(bit)
        return bits
        
    @staticmethod
    def bits_to_int(bits: List[int]) -> int:
        """
        Convert list of bits to integer
        
        Args:
            bits: List of bits (MSB first)
            
        Returns:
            Integer value
        """
        value = 0
        for i, bit in enumerate(bits):
            value |= bit << (len(bits) - 1 - i)
        return value


def calculate_crc32(data: bytes) -> int:
    """
    Calculate CRC32 checksum for data
    
    Args:
        data: Data to checksum
        
    Returns:
        CRC32 value as unsigned integer
    """
    return zlib.crc32(data) & 0xffffffff


def xor_bytes(data1: bytes, data2: bytes) -> bytes:
    """
    XOR two byte arrays
    
    Args:
        data1: First byte array
        data2: Second byte array
        
    Returns:
        XORed result
    """
    return bytes(a ^ b for a, b in zip(data1, data2))


def pad_bytes(data: bytes, block_size: int, padding_byte: int = 0) -> bytes:
    """
    Pad byte data to specified block size
    
    Args:
        data: Data to pad
        block_size: Target block size
        padding_byte: Byte value to use for padding
        
    Returns:
        Padded data
    """
    remainder = len(data) % block_size
    if remainder == 0:
        return data
        
    padding_needed = block_size - remainder
    padding = bytes([padding_byte] * padding_needed)
    return data + padding


def secure_compare(data1: bytes, data2: bytes) -> bool:
    """
    Constant-time comparison of byte arrays
    
    Args:
        data1: First byte array
        data2: Second byte array
        
    Returns:
        True if arrays are equal
    """
    if len(data1) != len(data2):
        return False
        
    result = 0
    for a, b in zip(data1, data2):
        result |= a ^ b
        
    return result == 0


def bytes_to_hex(data: bytes, separator: str = " ") -> str:
    """
    Convert bytes to hexadecimal string
    
    Args:
        data: Byte data
        separator: Separator between hex bytes
        
    Returns:
        Hexadecimal string representation
    """
    return separator.join(f"{byte:02x}" for byte in data)


def hex_to_bytes(hex_string: str) -> bytes:
    """
    Convert hexadecimal string to bytes
    
    Args:
        hex_string: Hexadecimal string (with or without separators)
        
    Returns:
        Byte data
    """
    # Remove common separators
    hex_string = hex_string.replace(" ", "").replace("-", "").replace(":", "")
    
    # Ensure even length
    if len(hex_string) % 2 != 0:
        hex_string = "0" + hex_string
        
    return bytes.fromhex(hex_string)


def format_byte_size(size_bytes: int) -> str:
    """
    Format byte size in human-readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024**2:
        return f"{size_bytes/1024:.1f} KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes/(1024**2):.1f} MB"
    else:
        return f"{size_bytes/(1024**3):.1f} GB"


def entropy(data: bytes) -> float:
    """
    Calculate Shannon entropy of byte data
    
    Args:
        data: Byte data to analyze
        
    Returns:
        Entropy value (0-8 bits per byte)
    """
    if not data:
        return 0.0
        
    # Count byte frequencies
    frequency = [0] * 256
    for byte in data:
        frequency[byte] += 1
        
    # Calculate entropy
    entropy_value = 0.0
    data_len = len(data)
    
    import math
    for count in frequency:
        if count > 0:
            probability = count / data_len
            entropy_value -= probability * math.log2(probability)
            
    return entropy_value
