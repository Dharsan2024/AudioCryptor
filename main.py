"""
Audio Steganography Desktop Application
Main entry point for the application

"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from theme import setup_theme
from tabs_encode import EncodeTab
from tabs_decode import DecodeTab
from tabs_settings import SettingsTab


class AudioStegoApp:
    """Main application class"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Audio Cryptor 🎵")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)
        
        # Setup theme and styles
        setup_theme(self.root)
        
        # Configure grid weights for responsive design
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Initialize tabs
        self.setup_tabs()
        
        # Set initial focus
        self.notebook.select(0)
        
    def setup_tabs(self):
        """Initialize all application tabs"""
        # Encode tab
        self.encode_tab = EncodeTab(self.notebook)
        self.notebook.add(self.encode_tab.frame, text="Encode")
        
        # Decode tab
        self.decode_tab = DecodeTab(self.notebook)
        self.notebook.add(self.decode_tab.frame, text="Decode")
        
        # Settings tab
        self.settings_tab = SettingsTab(self.notebook)
        self.notebook.add(self.settings_tab.frame, text="Settings")
        
    def run(self):
        """Start the application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.cleanup_and_exit()
        except Exception as e:
            messagebox.showerror("Application Error", f"An unexpected error occurred: {str(e)}")
            
    def cleanup_and_exit(self):
        """Clean up resources and exit"""
        try:
            # Stop any audio playback
            if hasattr(self.encode_tab, 'stop_playback'):
                self.encode_tab.stop_playback()
        except:
            pass
        finally:
            self.root.quit()


def main():
    """Main entry point"""
    try:
        app = AudioStegoApp()
        app.run()
    except Exception as e:
        print(f"Failed to start application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
