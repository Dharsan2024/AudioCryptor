"""
Password generator utility for automatic password creation
"""

import secrets
import string
from typing import List


class PasswordGenerator:
    """Generate secure passwords automatically"""
    
    def __init__(self):
        self.lowercase = string.ascii_lowercase
        self.uppercase = string.ascii_uppercase
        self.digits = string.digits
        self.symbols = "!@#$%^&*()-_=+[]{}|;:,.<>?"
        
    def generate_password(self, length: int = 16, 
                         include_symbols: bool = True,
                         include_numbers: bool = True,
                         include_uppercase: bool = True,
                         include_lowercase: bool = True) -> str:
        """
        Generate a secure random password
        
        Args:
            length: Password length (default 16)
            include_symbols: Include special symbols
            include_numbers: Include numbers
            include_uppercase: Include uppercase letters
            include_lowercase: Include lowercase letters
            
        Returns:
            Generated password string
        """
        if length < 4:
            length = 4
            
        # Build character set
        chars = ""
        required_chars = []
        
        if include_lowercase:
            chars += self.lowercase
            required_chars.append(secrets.choice(self.lowercase))
            
        if include_uppercase:
            chars += self.uppercase
            required_chars.append(secrets.choice(self.uppercase))
            
        if include_numbers:
            chars += self.digits
            required_chars.append(secrets.choice(self.digits))
            
        if include_symbols:
            chars += self.symbols
            required_chars.append(secrets.choice(self.symbols))
            
        if not chars:
            # Fallback to alphanumeric
            chars = self.lowercase + self.uppercase + self.digits
            required_chars = [
                secrets.choice(self.lowercase),
                secrets.choice(self.uppercase),
                secrets.choice(self.digits)
            ]
            
        # Generate remaining characters
        remaining_length = length - len(required_chars)
        if remaining_length > 0:
            random_chars = [secrets.choice(chars) for _ in range(remaining_length)]
        else:
            random_chars = []
            
        # Combine and shuffle
        password_chars = required_chars + random_chars
        secrets.SystemRandom().shuffle(password_chars)
        
        return ''.join(password_chars[:length])
        
    def generate_passphrase(self, word_count: int = 4, 
                           separator: str = "-") -> str:
        """
        Generate a passphrase using random words
        
        Args:
            word_count: Number of words to use
            separator: Separator between words
            
        Returns:
            Generated passphrase
        """
        # Simple word list for passphrases
        words = [
            "apple", "brave", "cloud", "dream", "eagle", "flame", "grace", "happy",
            "island", "jungle", "kernel", "lemon", "magic", "noble", "ocean", "peace",
            "quiet", "river", "storm", "tiger", "unity", "vivid", "water", "xenon",
            "youth", "zebra", "anchor", "bridge", "castle", "dragon", "emerald", "forest",
            "golden", "harbor", "ignite", "jasper", "knight", "lovely", "marble", "nature",
            "onward", "purple", "quartz", "rocket", "silver", "temple", "unique", "violet",
            "wizard", "yellow", "crimson", "diamond", "eclipse", "falcon", "glacier", "horizon"
        ]
        
        selected_words = [secrets.choice(words) for _ in range(word_count)]
        
        # Add random numbers to some words
        for i in range(len(selected_words)):
            if secrets.randbelow(3) == 0:  # 33% chance
                selected_words[i] += str(secrets.randbelow(100))
                
        return separator.join(selected_words)
        
    def generate_memorable_password(self, length: int = 12) -> str:
        """
        Generate a password that's somewhat memorable but still secure
        
        Args:
            length: Target password length
            
        Returns:
            Generated memorable password
        """
        # Use a pattern: word + numbers + symbols + word
        min_length = max(8, length)
        
        words = ["Sun", "Sky", "Fox", "Cat", "Dog", "Car", "Sea", "Moon", "Star", "Fire"]
        word1 = secrets.choice(words)
        word2 = secrets.choice(words)
        
        numbers = str(secrets.randbelow(9999)).zfill(2)
        symbols = secrets.choice("!@#$%&*")
        
        base_password = word1 + numbers + symbols + word2
        
        # Pad or trim to desired length
        if len(base_password) < min_length:
            # Add more characters
            extra_chars = self.lowercase + self.digits
            while len(base_password) < min_length:
                base_password += secrets.choice(extra_chars)
        elif len(base_password) > length:
            # Trim to length
            base_password = base_password[:length]
            
        return base_password


def generate_secure_password(length: int = 16) -> str:
    """
    Quick function to generate a secure password
    
    Args:
        length: Password length
        
    Returns:
        Generated password
    """
    generator = PasswordGenerator()
    return generator.generate_password(length)


def generate_simple_password(length: int = 12) -> str:
    """
    Generate a simpler password (no symbols)
    
    Args:
        length: Password length
        
    Returns:
        Generated password without symbols
    """
    generator = PasswordGenerator()
    return generator.generate_password(
        length=length,
        include_symbols=False
    )