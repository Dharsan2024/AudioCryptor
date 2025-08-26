"""
Decode tab for extracting messages from audio files
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os

from widgets import (ModernFrame, ModernButton, ModernLabel, ModernText, 
                    PasswordEntry, FileSelector, ModernProgressBar, CardFrame,
                    StatusBar)
from services.audio import AudioService
from services.crypto import CryptoService
from services.stego import StegoService
from utils.errors import StegoError


class DecodeTab:
    """Tab for decoding messages from audio files"""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = ModernFrame(parent)
        
        # Services
        self.audio_service = AudioService()
        self.crypto_service = CryptoService()
        self.stego_service = StegoService()
        
        # Variables
        self.decoding = False
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the decode tab UI"""
        # Configure grid weights
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        
        # Main container
        main_container = ModernFrame(self.frame)
        main_container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_container.grid_rowconfigure(1, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        
        # Title
        title = ModernLabel(main_container, text="Extract Hidden Message", 
                           style='Heading.TLabel')
        title.grid(row=0, column=0, sticky="w", pady=(0, 20))
        
        # Content frame
        content_frame = CardFrame(main_container)
        content_frame.grid(row=1, column=0, sticky="nsew")
        content_frame.grid_rowconfigure(4, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Input file selection
        ModernLabel(content_frame, text="Select Encoded Audio File:", 
                   style='Card.TLabel').grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.file_selector = FileSelector(
            content_frame,
            title="Select Encoded Audio File",
            filetypes=[
                ("WAV files", "*.wav"),
                ("Audio files", "*.wav *.mp3 *.flac *.m4a *.ogg"),
                ("All files", "*.*")
            ]
        )
        self.file_selector.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        
        # Password input
        ModernLabel(content_frame, text="Password:", 
                   style='Card.TLabel').grid(row=2, column=0, sticky="w", pady=(0, 5))
        
        self.password_entry = PasswordEntry(content_frame)
        self.password_entry.grid(row=3, column=0, sticky="ew", pady=(0, 15))
        
        # Progress bar
        self.progress_bar = ModernProgressBar(content_frame, mode='determinate')
        self.progress_bar.grid(row=4, column=0, sticky="ew", pady=(0, 15))
        
        # Buttons frame
        buttons_frame = ModernFrame(content_frame)
        buttons_frame.grid(row=5, column=0, sticky="ew", pady=(0, 15))
        buttons_frame.grid_columnconfigure(0, weight=1)
        
        # Decode button
        self.decode_btn = ModernButton(
            buttons_frame, 
            text="Extract Message", 
            command=self.start_decoding,
            style='Accent.TButton'
        )
        self.decode_btn.grid(row=0, column=1, padx=(10, 0))
        
        # Message output section
        ModernLabel(content_frame, text="Extracted Message:", 
                   style='Card.TLabel').grid(row=6, column=0, sticky="w", pady=(15, 5))
        
        # Message display frame
        message_frame = ModernFrame(content_frame)
        message_frame.grid(row=7, column=0, sticky="ew", pady=(0, 15))
        message_frame.grid_columnconfigure(0, weight=1)
        
        self.message_text = ModernText(message_frame, height=8, state='disabled')
        self.message_text.grid(row=0, column=0, sticky="ew")
        
        # Copy button
        self.copy_btn = ModernButton(
            message_frame, 
            text="Copy to Clipboard", 
            command=self.copy_message,
            state='disabled'
        )
        self.copy_btn.grid(row=0, column=1, padx=(10, 0), sticky="n")
        
        # Status bar
        self.status_bar = StatusBar(content_frame)
        self.status_bar.grid(row=8, column=0, sticky="ew", pady=(15, 0))
        
    def start_decoding(self):
        """Start the decoding process"""
        if self.decoding:
            return
            
        # Validate inputs
        file_path = self.file_selector.get()
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Error", "Please select a valid audio file")
            return
            
        password = self.password_entry.get()
        if not password:
            messagebox.showerror("Error", "Please enter the password")
            return
            
        # Clear previous message
        self.message_text.configure(state='normal')
        self.message_text.delete("1.0", tk.END)
        self.message_text.configure(state='disabled')
        self.copy_btn.configure(state='disabled')
        
        # Start decoding in background thread
        self.decoding = True
        self.decode_btn.configure(state='disabled', text="Extracting...")
        self.progress_bar.configure(mode='indeterminate')
        self.progress_bar.start()
        self.status_bar.set_status("Extracting message...")
        
        thread = threading.Thread(
            target=self.decode_worker,
            args=(file_path, password),
            daemon=True
        )
        thread.start()
        
    def decode_worker(self, input_file, password):
        """Worker thread for decoding"""
        try:
            # Load audio
            self.frame.after(0, lambda: self.status_bar.set_status("Loading audio file..."))
            audio_data, sample_rate = self.audio_service.load_audio(input_file)
            
            # Extract encrypted data
            self.frame.after(0, lambda: self.status_bar.set_status("Extracting hidden data..."))
            encrypted_data, salt, nonce = self.stego_service.extract_message(audio_data)
            
            # Decrypt message
            self.frame.after(0, lambda: self.status_bar.set_status("Decrypting message..."))
            message = self.crypto_service.decrypt_message(encrypted_data, password, salt, nonce)
            
            # Success
            self.frame.after(0, lambda: self.decoding_complete(message, None))
            
        except Exception as e:
            self.frame.after(0, lambda: self.decoding_complete(None, str(e)))
            
    def decoding_complete(self, message, error):
        """Handle decoding completion"""
        self.decoding = False
        self.decode_btn.configure(state='normal', text="Extract Message")
        self.progress_bar.stop()
        self.progress_bar.configure(mode='determinate', value=0)
        
        if error:
            self.status_bar.set_status(f"Decoding failed: {error}")
            
            # Check for common errors and provide helpful messages
            if "decrypt" in error.lower() or "invalid" in error.lower():
                messagebox.showerror(
                    "Decoding Failed", 
                    "Failed to decrypt the message. This could be due to:\n\n"
                    "• Incorrect password\n"
                    "• File is not encoded with this tool\n"
                    "• File has been corrupted or modified\n"
                    "• Wrong file selected"
                )
            else:
                messagebox.showerror("Decoding Failed", f"Failed to extract message:\n{error}")
        else:
            self.status_bar.set_status("Message extracted successfully!")
            
            # Display the message
            self.message_text.configure(state='normal')
            self.message_text.delete("1.0", tk.END)
            self.message_text.insert("1.0", message)
            self.message_text.configure(state='disabled')
            self.copy_btn.configure(state='normal')
            
            messagebox.showinfo("Success", "Message successfully extracted!")
            
    def copy_message(self):
        """Copy message to clipboard"""
        try:
            message = self.message_text.get("1.0", tk.END).strip()
            if message:
                self.frame.clipboard_clear()
                self.frame.clipboard_append(message)
                self.status_bar.set_status("Message copied to clipboard")
                
                # Optional: Show confirmation dialog for clearing clipboard
                if messagebox.askyesno(
                    "Security", 
                    "Message copied to clipboard.\n\n"
                    "For security, would you like to clear the clipboard after 30 seconds?"
                ):
                    self.frame.after(30000, self.clear_clipboard)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy message: {str(e)}")
            
    def clear_clipboard(self):
        """Clear the clipboard for security"""
        try:
            self.frame.clipboard_clear()
            self.status_bar.set_status("Clipboard cleared for security")
        except:
            pass
