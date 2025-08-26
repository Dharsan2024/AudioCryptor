"""
Encode tab for hiding messages in audio files
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os

from widgets import (ModernFrame, ModernButton, ModernLabel, ModernText, 
                    PasswordEntry, FileSelector, ModernProgressBar, CardFrame,
                    ModernCheckbutton, StatusBar, ModernScale)
from services.audio import AudioService
from services.crypto import CryptoService
from services.stego import StegoService
from utils.errors import StegoError
from utils.password_generator import generate_secure_password


class EncodeTab:
    """Tab for encoding messages into audio files"""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = ModernFrame(parent)
        
        # Services
        self.audio_service = AudioService()
        self.crypto_service = CryptoService()
        self.stego_service = StegoService()
        
        # Variables
        self.encoding = False
        self.current_capacity = 0
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the encode tab UI"""
        # Configure grid weights
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        
        # Main container
        main_container = ModernFrame(self.frame)
        main_container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_container.grid_rowconfigure(1, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        
        # Title
        title = ModernLabel(main_container, text="Hide Message in Audio", 
                           style='Heading.TLabel')
        title.grid(row=0, column=0, sticky="w", pady=(0, 20))
        
        # Content frame
        content_frame = CardFrame(main_container)
        content_frame.grid(row=1, column=0, sticky="nsew")
        content_frame.grid_rowconfigure(2, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Input file selection
        ModernLabel(content_frame, text="Select Audio File:", 
                   style='Card.TLabel').grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.file_selector = FileSelector(
            content_frame,
            title="Select Audio File",
            filetypes=[
                ("Audio files", "*.wav *.mp3 *.flac *.m4a *.ogg"),
                ("WAV files", "*.wav"),
                ("MP3 files", "*.mp3"),
                ("All files", "*.*")
            ]
        )
        self.file_selector.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        self.file_selector.entry.bind('<KeyRelease>', self.on_file_changed)
        
        # Message input
        ModernLabel(content_frame, text="Secret Message:", 
                   style='Card.TLabel').grid(row=2, column=0, sticky="nw", pady=(0, 5))
        
        self.message_text = ModernText(content_frame, height=8)
        self.message_text.grid(row=3, column=0, sticky="nsew", pady=(0, 15))
        self.message_text.bind('<KeyRelease>', self.on_message_changed)
        
        # Auto-generated password section
        password_frame = ModernFrame(content_frame)
        password_frame.grid(row=4, column=0, sticky="ew", pady=(0, 15))
        password_frame.grid_columnconfigure(0, weight=1)
        
        ModernLabel(password_frame, text="Auto-Generated Password:", 
                   style='Card.TLabel').grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        # Password display and controls
        pwd_controls_frame = ModernFrame(password_frame)
        pwd_controls_frame.grid(row=1, column=0, sticky="ew")
        pwd_controls_frame.grid_columnconfigure(0, weight=1)
        
        self.password_entry = PasswordEntry(pwd_controls_frame)
        self.password_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        # Generate new password button
        self.generate_pwd_btn = ModernButton(
            pwd_controls_frame, 
            text="🔄 New", 
            command=self.generate_new_password
        )
        self.generate_pwd_btn.grid(row=0, column=1, padx=(0, 5))
        
        # Copy password button
        self.copy_pwd_btn = ModernButton(
            pwd_controls_frame, 
            text="📋 Copy", 
            command=self.copy_password
        )
        self.copy_pwd_btn.grid(row=0, column=2)
        
        # Will generate initial password after UI setup
        
        # Audio player section
        player_frame = CardFrame(content_frame)
        player_frame.grid(row=5, column=0, sticky="ew", pady=(0, 15))
        player_frame.grid_columnconfigure(1, weight=1)
        
        ModernLabel(player_frame, text="Audio Preview:", 
                   style='Card.TLabel').grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))
        
        # Player controls
        self.play_btn = ModernButton(
            player_frame, 
            text="▶ Play", 
            command=self.toggle_playback,
            state='disabled'
        )
        self.play_btn.grid(row=1, column=0, padx=(0, 10))
        
        self.stop_btn = ModernButton(
            player_frame, 
            text="⏹ Stop", 
            command=self.stop_playback,
            state='disabled'
        )
        self.stop_btn.grid(row=1, column=1)
        
        # Volume control
        ModernLabel(player_frame, text="Volume:", 
                   style='Card.TLabel').grid(row=2, column=0, sticky="w", pady=(10, 5))
        
        self.volume_var = tk.DoubleVar(value=70)
        self.volume_scale = ModernScale(
            player_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.volume_var,
            length=200
        )
        self.volume_scale.grid(row=2, column=1, sticky="ew", pady=(10, 0))
        
        # Player variables
        self.current_audio = None
        self.is_playing = False
        
        # Options frame
        options_frame = ModernFrame(content_frame)
        options_frame.grid(row=6, column=0, sticky="ew", pady=(0, 15))
        options_frame.grid_columnconfigure(1, weight=1)
        
        # Scatter option
        self.scatter_var = tk.BooleanVar(value=True)
        self.scatter_check = ModernCheckbutton(
            options_frame, 
            text="Scatter bits (recommended for security)",
            variable=self.scatter_var
        )
        self.scatter_check.grid(row=0, column=0, sticky="w")
        
        # Capacity display
        self.capacity_label = ModernLabel(options_frame, text="Capacity: Unknown", 
                                        style='Card.TLabel')
        self.capacity_label.grid(row=0, column=1, sticky="e")
        
        # Progress bar
        self.progress_bar = ModernProgressBar(content_frame, mode='determinate')
        self.progress_bar.grid(row=7, column=0, sticky="ew", pady=(0, 15))
        
        # Buttons frame
        buttons_frame = ModernFrame(content_frame)
        buttons_frame.grid(row=8, column=0, sticky="ew")
        buttons_frame.grid_columnconfigure(0, weight=1)
        
        # Encode button
        self.encode_btn = ModernButton(
            buttons_frame, 
            text="Hide Message", 
            command=self.start_encoding,
            style='Accent.TButton'
        )
        self.encode_btn.grid(row=0, column=1, padx=(10, 0))
        
        # Status bar
        self.status_bar = StatusBar(content_frame)
        self.status_bar.grid(row=9, column=0, sticky="ew", pady=(15, 0))
        
        # Generate initial password after UI is complete
        self.generate_new_password()
        
    def on_file_changed(self, event=None):
        """Handle file selection change"""
        file_path = self.file_selector.get()
        if file_path and os.path.exists(file_path):
            try:
                # Calculate capacity
                self.current_capacity = self.stego_service.calculate_capacity(file_path)
                self.update_capacity_display()
                
                # Load audio for playback
                self.load_audio_for_playback(file_path)
                self.status_bar.set_status("Audio file loaded successfully")
            except Exception as e:
                self.current_capacity = 0
                self.capacity_label.configure(text="Capacity: Error")
                self.disable_playback()
                self.status_bar.set_status(f"Error loading file: {str(e)}")
        else:
            self.current_capacity = 0
            self.capacity_label.configure(text="Capacity: Unknown")
            self.disable_playback()
            
    def on_message_changed(self, event=None):
        """Handle message text change"""
        self.update_capacity_display()
        
    def update_capacity_display(self):
        """Update the capacity display"""
        if self.current_capacity > 0:
            message = self.message_text.get("1.0", tk.END).strip()
            message_size = len(message.encode('utf-8'))
            
            # Add overhead for encryption and header
            encrypted_size = message_size + 32  # Approximate overhead
            header_size = 42  # Header size from spec
            total_needed = encrypted_size + header_size
            
            if total_needed <= self.current_capacity:
                color = "green"
                status = "✓"
            else:
                color = "red"
                status = "✗"
                
            self.capacity_label.configure(
                text=f"{status} Capacity: {total_needed}/{self.current_capacity} bytes",
                foreground=color
            )
        else:
            self.capacity_label.configure(text="Capacity: Unknown")
            
    def start_encoding(self):
        """Start the encoding process"""
        if self.encoding:
            return
            
        # Validate inputs
        file_path = self.file_selector.get()
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("Error", "Please select a valid audio file")
            return
            
        message = self.message_text.get("1.0", tk.END).strip()
        if not message:
            messagebox.showerror("Error", "Please enter a message to hide")
            return
            
        password = self.password_entry.get()
        if not password:
            messagebox.showerror("Error", "Please enter a password")
            return
            
        # Check capacity
        message_size = len(message.encode('utf-8'))
        if self.current_capacity > 0:
            encrypted_size = message_size + 32
            header_size = 42
            total_needed = encrypted_size + header_size
            
            if total_needed > self.current_capacity:
                messagebox.showerror(
                    "Error", 
                    f"Message too large. Need {total_needed} bytes, "
                    f"but only {self.current_capacity} bytes available."
                )
                return
                
        # Choose output file
        output_file = filedialog.asksaveasfilename(
            title="Save Encoded Audio As",
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")]
        )
        
        if not output_file:
            return
            
        # Start encoding in background thread
        self.encoding = True
        self.encode_btn.configure(state='disabled', text="Encoding...")
        self.progress_bar.configure(mode='indeterminate')
        self.progress_bar.start()
        self.status_bar.set_status("Encoding message...")
        
        thread = threading.Thread(
            target=self.encode_worker,
            args=(file_path, message, password, output_file),
            daemon=True
        )
        thread.start()
        
    def encode_worker(self, input_file, message, password, output_file):
        """Worker thread for encoding"""
        try:
            # Load and convert audio
            self.frame.after(0, lambda: self.status_bar.set_status("Loading audio file..."))
            audio_data, sample_rate = self.audio_service.load_audio(input_file)
            
            # Encrypt message
            self.frame.after(0, lambda: self.status_bar.set_status("Encrypting message..."))
            encrypted_data, salt, nonce = self.crypto_service.encrypt_message(message, password)
            
            # Embed in audio
            self.frame.after(0, lambda: self.status_bar.set_status("Hiding message in audio..."))
            encoded_audio = self.stego_service.embed_message(
                audio_data, 
                encrypted_data, 
                salt, 
                nonce,
                scatter=self.scatter_var.get()
            )
            
            # Save output
            self.frame.after(0, lambda: self.status_bar.set_status("Saving encoded audio..."))
            self.audio_service.save_audio(encoded_audio, sample_rate, output_file)
            
            # Success
            self.frame.after(0, lambda: self.encoding_complete(output_file, None))
            
        except Exception as e:
            self.frame.after(0, lambda: self.encoding_complete(None, str(e)))
            
    def encoding_complete(self, output_file, error):
        """Handle encoding completion"""
        self.encoding = False
        self.encode_btn.configure(state='normal', text="Hide Message")
        self.progress_bar.stop()
        self.progress_bar.configure(mode='determinate', value=0)
        
        if error:
            self.status_bar.set_status(f"Encoding failed: {error}")
            messagebox.showerror("Encoding Failed", f"Failed to encode message:\n{error}")
        else:
            self.status_bar.set_status("Message encoded successfully!")
            result = messagebox.showinfo(
                "Success", 
                f"Message successfully hidden in audio!\n\nSaved to: {output_file}\n\n"
                "Would you like to open the output folder?"
            )
            
            # Optionally open output folder
            if messagebox.askyesno("Open Folder", "Open the output folder?"):
                import subprocess
                import platform
                
                folder_path = os.path.dirname(output_file)
                if platform.system() == "Windows":
                    subprocess.run(["explorer", folder_path])
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", folder_path])
                else:  # Linux
                    subprocess.run(["xdg-open", folder_path])
                    
    def generate_new_password(self):
        """Generate a new secure password"""
        try:
            new_password = generate_secure_password(16)
            self.password_entry.delete(0, tk.END)
            self.password_entry.insert(0, new_password)
            if hasattr(self, 'status_bar'):
                self.status_bar.set_status("New password generated")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate password: {str(e)}")
            
    def copy_password(self):
        """Copy password to clipboard"""
        try:
            password = self.password_entry.get()
            if password:
                self.frame.clipboard_clear()
                self.frame.clipboard_append(password)
                if hasattr(self, 'status_bar'):
                    self.status_bar.set_status("Password copied to clipboard")
                messagebox.showinfo("Copied", "Password copied to clipboard!")
            else:
                messagebox.showwarning("Warning", "No password to copy")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy password: {str(e)}")
            
    def load_audio_for_playback(self, file_path):
        """Load audio file for playback"""
        try:
            audio_data, sample_rate = self.audio_service.load_audio(file_path)
            self.current_audio = (audio_data, sample_rate)
            self.enable_playback()
        except Exception as e:
            self.disable_playback()
            raise e
            
    def enable_playback(self):
        """Enable audio playback controls"""
        self.play_btn.configure(state='normal')
        self.stop_btn.configure(state='normal')
        
    def disable_playback(self):
        """Disable audio playback controls"""
        self.stop_playback()
        self.play_btn.configure(state='disabled', text="▶ Play")
        self.stop_btn.configure(state='disabled')
        self.current_audio = None
        self.is_playing = False
        
    def toggle_playback(self):
        """Toggle audio playback"""
        if not self.current_audio:
            return
            
        if self.is_playing:
            self.pause_playback()
        else:
            self.start_playback()
            
    def start_playback(self):
        """Start audio playback"""
        try:
            if not self.current_audio:
                return
                
            audio_data, sample_rate = self.current_audio
            volume = self.volume_var.get() / 100.0
            
            self.audio_service.start_playback(audio_data, sample_rate, volume)
            
            self.is_playing = True
            self.play_btn.configure(text="⏸ Pause")
            self.status_bar.set_status("Playing audio...")
            
        except Exception as e:
            messagebox.showerror("Playback Error", f"Failed to start playback:\n{str(e)}")
            
    def pause_playback(self):
        """Pause audio playback"""
        try:
            self.audio_service.stop_playback()
            self.is_playing = False
            self.play_btn.configure(text="▶ Play")
            self.status_bar.set_status("Playback paused")
        except Exception as e:
            print(f"Error pausing playback: {e}")
            
    def stop_playback(self):
        """Stop audio playback"""
        try:
            self.audio_service.stop_playback()
            self.is_playing = False
            self.play_btn.configure(text="▶ Play")
            self.status_bar.set_status("Playback stopped")
        except Exception as e:
            print(f"Error stopping playback: {e}")
