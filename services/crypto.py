"""
Cryptographic service for encrypting and decrypting messages
"""

import os
import hashlib
from typing import Tuple

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

from utils.errors import StegoError


class CryptoService:
    """Service for cryptographic operations"""
    
    def __init__(self):
        self.key_iterations = 200000  # PBKDF2 iterations
        self.key_length = 32  # 256-bit AES key
        self.salt_length = 16  # 128-bit salt
        self.nonce_length = 12  # 96-bit nonce for GCM
        
    def encrypt_message(self, message: str, password: str) -> Tuple[bytes, bytes, bytes]:
        """
        Encrypt a message using AES-GCM with PBKDF2 key derivation
        
        Args:
            message: Plain text message to encrypt
            password: Password for encryption
            
        Returns:
            Tuple of (encrypted_data, salt, nonce)
        """
        try:
            # Convert message to bytes
            message_bytes = message.encode('utf-8')
            
            # Generate random salt and nonce
            salt = os.urandom(self.salt_length)
            nonce = os.urandom(self.nonce_length)
            
            # Derive key from password using PBKDF2
            key = self._derive_key(password, salt)
            
            # Encrypt using AES-GCM
            aesgcm = AESGCM(key)
            encrypted_data = aesgcm.encrypt(nonce, message_bytes, None)
            
            return encrypted_data, salt, nonce
            
        except Exception as e:
            raise StegoError(f"Encryption failed: {str(e)}")
            
    def decrypt_message(self, encrypted_data: bytes, password: str, 
                       salt: bytes, nonce: bytes) -> str:
        """
        Decrypt a message using AES-GCM with PBKDF2 key derivation
        
        Args:
            encrypted_data: Encrypted message data
            password: Password for decryption
            salt: Salt used for key derivation
            nonce: Nonce used for encryption
            
        Returns:
            Decrypted plain text message
        """
        try:
            # Derive key from password using same salt
            key = self._derive_key(password, salt)
            
            # Decrypt using AES-GCM
            aesgcm = AESGCM(key)
            decrypted_bytes = aesgcm.decrypt(nonce, encrypted_data, None)
            
            # Convert back to string
            message = decrypted_bytes.decode('utf-8')
            
            return message
            
        except InvalidTag:
            raise StegoError("Decryption failed: Invalid password or corrupted data")
        except UnicodeDecodeError:
            raise StegoError("Decryption failed: Invalid message encoding")
        except Exception as e:
            raise StegoError(f"Decryption failed: {str(e)}")
            
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """
        Derive encryption key from password using PBKDF2-HMAC-SHA256
        
        Args:
            password: User password
            salt: Random salt
            
        Returns:
            Derived key bytes
        """
        try:
            password_bytes = password.encode('utf-8')
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=self.key_length,
                salt=salt,
                iterations=self.key_iterations,
            )
            
            key = kdf.derive(password_bytes)
            return key
            
        except Exception as e:
            raise StegoError(f"Key derivation failed: {str(e)}")
            
    def generate_key_for_scatter(self, password: str, salt: bytes) -> bytes:
        """
        Generate a separate key for bit scattering PRNG seeding
        
        Args:
            password: User password
            salt: Salt from encryption
            
        Returns:
            Key for scatter PRNG
        """
        try:
            # Use HKDF-like approach with different info
            base_key = self._derive_key(password, salt)
            
            # Create scatter key by hashing base key with constant
            scatter_info = b"AudioStegoScatter"
            hasher = hashlib.sha256()
            hasher.update(base_key)
            hasher.update(scatter_info)
            
            return hasher.digest()[:16]  # 128-bit key for scatter
            
        except Exception as e:
            raise StegoError(f"Scatter key generation failed: {str(e)}")
            
    def calculate_encrypted_size(self, message: str) -> int:
        """
        Calculate the size of encrypted message
        
        Args:
            message: Plain text message
            
        Returns:
            Size of encrypted data in bytes
        """
        message_bytes = message.encode('utf-8')
        # AES-GCM adds 16 bytes authentication tag
        return len(message_bytes) + 16
        
    def verify_password_strength(self, password: str) -> Tuple[bool, str]:
        """
        Verify password strength
        
        Args:
            password: Password to check
            
        Returns:
            Tuple of (is_strong, message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
            
        if len(password) < 12:
            return True, "Password is acceptable but could be longer"
            
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        strength_count = sum([has_upper, has_lower, has_digit, has_special])
        
        if strength_count >= 3:
            return True, "Strong password"
        elif strength_count >= 2:
            return True, "Good password"
        else:
            return True, "Weak password - consider adding uppercase, lowercase, numbers, and symbols"
