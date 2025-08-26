"""
Custom exception classes for the Audio Steganography application
"""

from typing import Optional


class StegoError(Exception):
    """Base exception for steganography operations"""
    
    def __init__(self, message: str, error_code: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        
    def __str__(self):
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class AudioError(StegoError):
    """Exception for audio-related operations"""
    
    def __init__(self, message: str):
        super().__init__(message, "AUDIO_ERROR")


class CryptoError(StegoError):
    """Exception for cryptographic operations"""
    
    def __init__(self, message: str):
        super().__init__(message, "CRYPTO_ERROR")


class CapacityError(StegoError):
    """Exception for capacity-related issues"""
    
    def __init__(self, message: str, required: Optional[int] = None, available: Optional[int] = None):
        super().__init__(message, "CAPACITY_ERROR")
        self.required = required
        self.available = available
        
    def __str__(self):
        base_msg = super().__str__()
        if self.required is not None and self.available is not None:
            return f"{base_msg} (Required: {self.required}, Available: {self.available})"
        return base_msg


class ValidationError(StegoError):
    """Exception for input validation issues"""
    
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message, "VALIDATION_ERROR")
        self.field = field
        
    def __str__(self):
        base_msg = super().__str__()
        if self.field:
            return f"{base_msg} (Field: {self.field})"
        return base_msg


class HeaderError(StegoError):
    """Exception for header parsing/validation issues"""
    
    def __init__(self, message: str):
        super().__init__(message, "HEADER_ERROR")


class FileError(StegoError):
    """Exception for file operation issues"""
    
    def __init__(self, message: str, file_path: Optional[str] = None):
        super().__init__(message, "FILE_ERROR")
        self.file_path = file_path
        
    def __str__(self):
        base_msg = super().__str__()
        if self.file_path:
            return f"{base_msg} (File: {self.file_path})"
        return base_msg


class PlaybackError(StegoError):
    """Exception for audio playback issues"""
    
    def __init__(self, message: str):
        super().__init__(message, "PLAYBACK_ERROR")


class DependencyError(StegoError):
    """Exception for missing dependencies"""
    
    def __init__(self, message: str, dependency: Optional[str] = None):
        super().__init__(message, "DEPENDENCY_ERROR")
        self.dependency = dependency
        
    def __str__(self):
        base_msg = super().__str__()
        if self.dependency:
            return f"{base_msg} (Missing: {self.dependency})"
        return base_msg


# Error code mappings for user-friendly messages
ERROR_MESSAGES = {
    "AUDIO_ERROR": "Audio processing error",
    "CRYPTO_ERROR": "Encryption/decryption error", 
    "CAPACITY_ERROR": "Storage capacity error",
    "VALIDATION_ERROR": "Input validation error",
    "HEADER_ERROR": "Data header error",
    "FILE_ERROR": "File operation error",
    "PLAYBACK_ERROR": "Audio playback error",
    "DEPENDENCY_ERROR": "Missing dependency error"
}


def get_user_friendly_message(error: StegoError) -> str:
    """
    Get a user-friendly error message
    
    Args:
        error: StegoError instance
        
    Returns:
        User-friendly error message
    """
    if error.error_code in ERROR_MESSAGES:
        category = ERROR_MESSAGES[error.error_code]
        return f"{category}: {error.message}"
    return str(error)


def handle_common_errors(func):
    """
    Decorator to handle common errors and convert to user-friendly messages
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            raise FileError(f"File not found: {str(e)}")
        except PermissionError as e:
            raise FileError(f"Permission denied: {str(e)}")
        except MemoryError as e:
            raise StegoError("Insufficient memory for operation")
        except KeyboardInterrupt:
            raise StegoError("Operation cancelled by user")
        except Exception as e:
            # Re-raise StegoError instances as-is
            if isinstance(e, StegoError):
                raise
            # Convert other exceptions to generic StegoError
            raise StegoError(f"Unexpected error: {str(e)}")
            
    return wrapper


# Context manager for error handling
class ErrorContext:
    """Context manager for consistent error handling"""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            return False
            
        # Convert known exceptions to StegoError
        if exc_type == FileNotFoundError:
            raise FileError(f"File not found during {self.operation_name}")
        elif exc_type == PermissionError:
            raise FileError(f"Permission denied during {self.operation_name}")
        elif exc_type == MemoryError:
            raise StegoError(f"Insufficient memory for {self.operation_name}")
        elif exc_type == KeyboardInterrupt:
            raise StegoError(f"{self.operation_name} cancelled by user")
        elif not isinstance(exc_val, StegoError):
            raise StegoError(f"Error during {self.operation_name}: {str(exc_val)}")
            
        return False  # Re-raise the exception
