"""
Settings tab for application configuration
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os

from widgets import (ModernFrame, ModernButton, ModernLabel, ModernEntry,
                    ModernCheckbutton, CardFrame, StatusBar)


class SettingsTab:
    """Tab for application settings"""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = ModernFrame(parent)
        
        # Settings file path
        self.settings_file = "audio_stego_settings.json"
        
        # Default settings
        self.default_settings = {
            "default_output_folder": "",
            "lsb_bits": 1,
            "scatter_enabled": True,
            "auto_clear_clipboard": True,
            "clipboard_clear_delay": 30,
            "email_server": "smtp.gmail.com",
            "email_port": 587,
            "email_address": "",
            "email_use_tls": True
        }
        
        # Load settings
        self.settings = self.load_settings()
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the settings tab UI"""
        # Configure grid weights
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        
        # Main container with scrollable content
        main_container = ModernFrame(self.frame)
        main_container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_container.grid_rowconfigure(1, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        
        # Title
        title = ModernLabel(main_container, text="Application Settings", 
                           style='Heading.TLabel')
        title.grid(row=0, column=0, sticky="w", pady=(0, 20))
        
        # Scrollable content frame
        canvas = tk.Canvas(main_container, bg='#1a1a1a', 
                          highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ModernFrame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=1, column=0, sticky="nsew")
        scrollbar.grid(row=1, column=1, sticky="ns")
        
        # General settings section
        self.setup_general_settings(scrollable_frame, 0)
        
        # Steganography settings section
        self.setup_stego_settings(scrollable_frame, 1)
        
        # Email settings section
        self.setup_email_settings(scrollable_frame, 2)
        
        # About section
        self.setup_about_section(scrollable_frame, 3)
        
        # Save/Reset buttons
        self.setup_action_buttons(scrollable_frame, 4)
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
    def setup_general_settings(self, parent, row):
        """Setup general settings section"""
        # General settings card
        general_card = CardFrame(parent)
        general_card.grid(row=row, column=0, sticky="ew", pady=(0, 20))
        general_card.grid_columnconfigure(1, weight=1)
        
        ModernLabel(general_card, text="General Settings", 
                   style='Heading.TLabel').grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))
        
        # Default output folder
        ModernLabel(general_card, text="Default Output Folder:", 
                   style='Card.TLabel').grid(row=1, column=0, sticky="w", pady=(0, 10))
        
        folder_frame = ModernFrame(general_card)
        folder_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        folder_frame.grid_columnconfigure(0, weight=1)
        
        self.output_folder_var = tk.StringVar(value=self.settings.get("default_output_folder", ""))
        self.output_folder_entry = ModernEntry(folder_frame, textvariable=self.output_folder_var)
        self.output_folder_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        ModernButton(folder_frame, text="Browse", 
                    command=self.browse_output_folder).grid(row=0, column=1)
        
        # Auto-clear clipboard
        self.auto_clear_var = tk.BooleanVar(value=self.settings.get("auto_clear_clipboard", True))
        ModernCheckbutton(general_card, text="Auto-clear clipboard after copying messages",
                         variable=self.auto_clear_var).grid(row=3, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        # Clipboard clear delay
        ModernLabel(general_card, text="Clipboard clear delay (seconds):", 
                   style='Card.TLabel').grid(row=4, column=0, sticky="w", pady=(0, 5))
        
        self.clipboard_delay_var = tk.StringVar(value=str(self.settings.get("clipboard_clear_delay", 30)))
        delay_entry = ModernEntry(general_card, textvariable=self.clipboard_delay_var, width=10)
        delay_entry.grid(row=5, column=0, sticky="w", pady=(0, 10))
        
    def setup_stego_settings(self, parent, row):
        """Setup steganography settings section"""
        # Steganography settings card
        stego_card = CardFrame(parent)
        stego_card.grid(row=row, column=0, sticky="ew", pady=(0, 20))
        stego_card.grid_columnconfigure(1, weight=1)
        
        ModernLabel(stego_card, text="Steganography Settings", 
                   style='Heading.TLabel').grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))
        
        # LSB bits setting
        ModernLabel(stego_card, text="Default LSB bits (1-2):", 
                   style='Card.TLabel').grid(row=1, column=0, sticky="w", pady=(0, 5))
        
        self.lsb_bits_var = tk.StringVar(value=str(self.settings.get("lsb_bits", 1)))
        lsb_entry = ModernEntry(stego_card, textvariable=self.lsb_bits_var, width=10)
        lsb_entry.grid(row=2, column=0, sticky="w", pady=(0, 10))
        
        ModernLabel(stego_card, text="Note: 1 LSB is recommended for best quality", 
                   style='Card.TLabel').grid(row=3, column=0, columnspan=2, sticky="w", pady=(0, 15))
        
        # Scatter enabled
        self.scatter_var = tk.BooleanVar(value=self.settings.get("scatter_enabled", True))
        ModernCheckbutton(stego_card, text="Enable bit scattering by default (recommended for security)",
                         variable=self.scatter_var).grid(row=4, column=0, columnspan=2, sticky="w")
        
    def setup_email_settings(self, parent, row):
        """Setup email settings section"""
        # Email settings card
        email_card = CardFrame(parent)
        email_card.grid(row=row, column=0, sticky="ew", pady=(0, 20))
        email_card.grid_columnconfigure(1, weight=1)
        
        ModernLabel(email_card, text="Email Settings (Optional)", 
                   style='Heading.TLabel').grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))
        
        # SMTP server
        ModernLabel(email_card, text="SMTP Server:", 
                   style='Card.TLabel').grid(row=1, column=0, sticky="w", pady=(0, 5))
        
        self.email_server_var = tk.StringVar(value=self.settings.get("email_server", "smtp.gmail.com"))
        server_entry = ModernEntry(email_card, textvariable=self.email_server_var)
        server_entry.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        # SMTP port
        ModernLabel(email_card, text="SMTP Port:", 
                   style='Card.TLabel').grid(row=3, column=0, sticky="w", pady=(0, 5))
        
        self.email_port_var = tk.StringVar(value=str(self.settings.get("email_port", 587)))
        port_entry = ModernEntry(email_card, textvariable=self.email_port_var, width=10)
        port_entry.grid(row=4, column=0, sticky="w", pady=(0, 10))
        
        # Email address
        ModernLabel(email_card, text="Email Address:", 
                   style='Card.TLabel').grid(row=5, column=0, sticky="w", pady=(0, 5))
        
        self.email_address_var = tk.StringVar(value=self.settings.get("email_address", ""))
        address_entry = ModernEntry(email_card, textvariable=self.email_address_var)
        address_entry.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        # Use TLS
        self.email_tls_var = tk.BooleanVar(value=self.settings.get("email_use_tls", True))
        ModernCheckbutton(email_card, text="Use TLS encryption",
                         variable=self.email_tls_var).grid(row=7, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        ModernLabel(email_card, 
                   text="Note: For Gmail, use an App Password instead of your regular password",
                   style='Card.TLabel').grid(row=8, column=0, columnspan=2, sticky="w")
        
    def setup_about_section(self, parent, row):
        """Setup about section"""
        # About card
        about_card = CardFrame(parent)
        about_card.grid(row=row, column=0, sticky="ew", pady=(0, 20))
        
        ModernLabel(about_card, text="About", 
                   style='Heading.TLabel').grid(row=0, column=0, sticky="w", pady=(0, 15))
        
        about_text = """Audio Steganography Tool v1.0

This application allows you to hide encrypted messages inside audio files using LSB (Least Significant Bit) steganography. Messages are encrypted with AES-GCM before being hidden, ensuring both confidentiality and integrity.

Features:
• Support for WAV, MP3, FLAC, M4A, and OGG audio formats
• Strong AES-GCM encryption with PBKDF2 key derivation
• Bit scattering for enhanced security
• Built-in audio player
• Modern, user-friendly interface

Developed with Python, Tkinter, and industry-standard cryptography libraries."""
        
        about_label = ModernLabel(about_card, text=about_text, style='Card.TLabel')
        about_label.grid(row=1, column=0, sticky="w")
        
    def setup_action_buttons(self, parent, row):
        """Setup save/reset action buttons"""
        # Action buttons frame
        buttons_frame = ModernFrame(parent)
        buttons_frame.grid(row=row, column=0, sticky="ew", pady=(20, 0))
        buttons_frame.grid_columnconfigure(0, weight=1)
        
        button_container = ModernFrame(buttons_frame)
        button_container.grid(row=0, column=0)
        
        # Save settings button
        ModernButton(button_container, text="Save Settings", 
                    command=self.save_settings,
                    style='Accent.TButton').grid(row=0, column=0, padx=(0, 10))
        
        # Reset to defaults button
        ModernButton(button_container, text="Reset to Defaults", 
                    command=self.reset_to_defaults).grid(row=0, column=1, padx=(10, 0))
        
        # Status bar
        self.status_bar = StatusBar(buttons_frame)
        self.status_bar.grid(row=1, column=0, sticky="ew", pady=(15, 0))
        
    def browse_output_folder(self):
        """Browse for default output folder"""
        folder = filedialog.askdirectory(title="Select Default Output Folder")
        if folder:
            self.output_folder_var.set(folder)
            
    def load_settings(self):
        """Load settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                # Merge with defaults to ensure all keys exist
                merged_settings = self.default_settings.copy()
                merged_settings.update(settings)
                return merged_settings
        except Exception as e:
            print(f"Error loading settings: {e}")
            
        return self.default_settings.copy()
        
    def save_settings(self):
        """Save current settings to file"""
        try:
            # Validate LSB bits
            try:
                lsb_bits = int(self.lsb_bits_var.get())
                if lsb_bits < 1 or lsb_bits > 2:
                    raise ValueError("LSB bits must be 1 or 2")
            except ValueError:
                messagebox.showerror("Invalid Setting", "LSB bits must be 1 or 2")
                return
                
            # Validate clipboard delay
            try:
                delay = int(self.clipboard_delay_var.get())
                if delay < 1:
                    raise ValueError("Delay must be positive")
            except ValueError:
                messagebox.showerror("Invalid Setting", "Clipboard clear delay must be a positive number")
                return
                
            # Validate email port
            try:
                port = int(self.email_port_var.get())
                if port < 1 or port > 65535:
                    raise ValueError("Invalid port")
            except ValueError:
                messagebox.showerror("Invalid Setting", "Email port must be between 1 and 65535")
                return
                
            # Collect settings
            self.settings = {
                "default_output_folder": self.output_folder_var.get(),
                "lsb_bits": lsb_bits,
                "scatter_enabled": self.scatter_var.get(),
                "auto_clear_clipboard": self.auto_clear_var.get(),
                "clipboard_clear_delay": delay,
                "email_server": self.email_server_var.get(),
                "email_port": port,
                "email_address": self.email_address_var.get(),
                "email_use_tls": self.email_tls_var.get()
            }
            
            # Save to file
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
                
            self.status_bar.set_status("Settings saved successfully!")
            messagebox.showinfo("Success", "Settings saved successfully!")
            
        except Exception as e:
            self.status_bar.set_status(f"Error saving settings: {str(e)}")
            messagebox.showerror("Error", f"Failed to save settings:\n{str(e)}")
            
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        if messagebox.askyesno("Reset Settings", "Are you sure you want to reset all settings to defaults?"):
            self.settings = self.default_settings.copy()
            self.update_ui_from_settings()
            self.status_bar.set_status("Settings reset to defaults")
            
    def update_ui_from_settings(self):
        """Update UI controls from current settings"""
        self.output_folder_var.set(self.settings.get("default_output_folder", ""))
        self.lsb_bits_var.set(str(self.settings.get("lsb_bits", 1)))
        self.scatter_var.set(self.settings.get("scatter_enabled", True))
        self.auto_clear_var.set(self.settings.get("auto_clear_clipboard", True))
        self.clipboard_delay_var.set(str(self.settings.get("clipboard_clear_delay", 30)))
        self.email_server_var.set(self.settings.get("email_server", "smtp.gmail.com"))
        self.email_port_var.set(str(self.settings.get("email_port", 587)))
        self.email_address_var.set(self.settings.get("email_address", ""))
        self.email_tls_var.set(self.settings.get("email_use_tls", True))
        
    def get_setting(self, key, default=None):
        """Get a setting value"""
        return self.settings.get(key, default)
