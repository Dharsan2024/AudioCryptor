"""
Theme and styling configuration for the Audio Steganography application
"""

import tkinter as tk
from tkinter import ttk


# Color scheme
COLORS = {
    'primary': '#106EBE',      # Blue
    'accent': '#0FFCBE',       # Mint
    'bg_dark': '#1a1a1a',      # Dark background
    'bg_medium': '#2d2d2d',    # Medium background
    'bg_light': '#404040',     # Light background
    'text_light': '#ffffff',   # White text
    'text_medium': '#cccccc',  # Light gray text
    'text_dark': '#666666',    # Dark gray text
    'success': '#28a745',      # Green
    'warning': '#ffc107',      # Yellow
    'error': '#dc3545',        # Red
    'border': '#555555'        # Border color
}


def setup_theme(root):
    """Setup the application theme and ttk styles"""
    
    # Configure root window
    root.configure(bg=COLORS['bg_dark'])
    
    # Create style object
    style = ttk.Style()
    
    # Configure notebook (tabs)
    style.theme_use('clam')
    
    style.configure('TNotebook', 
                   background=COLORS['bg_dark'],
                   borderwidth=0)
    
    style.configure('TNotebook.Tab',
                   background=COLORS['bg_medium'],
                   foreground=COLORS['text_light'],
                   padding=[20, 10],
                   borderwidth=1)
    
    style.map('TNotebook.Tab',
             background=[('selected', COLORS['primary']),
                        ('active', COLORS['bg_light'])],
             foreground=[('selected', COLORS['text_light'])])
    
    # Configure frames
    style.configure('Modern.TFrame',
                   background=COLORS['bg_dark'],
                   relief='flat',
                   borderwidth=0)
    
    style.configure('Card.TFrame',
                   background=COLORS['bg_medium'],
                   relief='flat',
                   borderwidth=1)
    
    # Configure labels
    style.configure('Modern.TLabel',
                   background=COLORS['bg_dark'],
                   foreground=COLORS['text_light'],
                   font=('Segoe UI', 10))
    
    style.configure('Heading.TLabel',
                   background=COLORS['bg_dark'],
                   foreground=COLORS['text_light'],
                   font=('Segoe UI', 12, 'bold'))
    
    style.configure('Card.TLabel',
                   background=COLORS['bg_medium'],
                   foreground=COLORS['text_light'],
                   font=('Segoe UI', 10))
    
    # Configure buttons
    style.configure('Modern.TButton',
                   background=COLORS['primary'],
                   foreground=COLORS['text_light'],
                   font=('Segoe UI', 10),
                   padding=[20, 10],
                   relief='flat',
                   borderwidth=0)
    
    style.map('Modern.TButton',
             background=[('active', COLORS['accent']),
                        ('pressed', COLORS['bg_light'])])
    
    style.configure('Accent.TButton',
                   background=COLORS['accent'],
                   foreground=COLORS['bg_dark'],
                   font=('Segoe UI', 10, 'bold'),
                   padding=[20, 10],
                   relief='flat',
                   borderwidth=0)
    
    style.map('Accent.TButton',
             background=[('active', COLORS['primary']),
                        ('pressed', COLORS['bg_light'])],
             foreground=[('active', COLORS['text_light'])])
    
    # Configure entry widgets
    style.configure('Modern.TEntry',
                   fieldbackground=COLORS['bg_light'],
                   foreground=COLORS['text_light'],
                   borderwidth=1,
                   relief='solid',
                   insertcolor=COLORS['text_light'],
                   font=('Segoe UI', 10))
    
    style.map('Modern.TEntry',
             focuscolor=[('focus', COLORS['accent'])],
             bordercolor=[('focus', COLORS['accent'])])
    
    # Configure progress bars
    style.configure('Modern.Horizontal.TProgressbar',
                   background=COLORS['primary'],
                   troughcolor=COLORS['bg_light'],
                   borderwidth=0,
                   lightcolor=COLORS['primary'],
                   darkcolor=COLORS['primary'])
    
    # Configure scales (sliders)
    style.configure('Modern.Horizontal.TScale',
                   background=COLORS['bg_dark'],
                   troughcolor=COLORS['bg_light'],
                   slidercolor=COLORS['accent'],
                   borderwidth=0)
    
    # Configure checkbuttons
    style.configure('Modern.TCheckbutton',
                   background=COLORS['bg_dark'],
                   foreground=COLORS['text_light'],
                   font=('Segoe UI', 10),
                   focuscolor='none')
    
    style.map('Modern.TCheckbutton',
             background=[('active', COLORS['bg_dark'])],
             indicatorcolor=[('selected', COLORS['accent']),
                           ('pressed', COLORS['primary'])])
    
    # Configure text widgets (for message areas)
    def configure_text_widget(text_widget):
        """Configure a text widget with modern styling"""
        text_widget.configure(
            bg=COLORS['bg_light'],
            fg=COLORS['text_light'],
            insertbackground=COLORS['text_light'],
            selectbackground=COLORS['primary'],
            selectforeground=COLORS['text_light'],
            font=('Segoe UI', 10),
            relief='flat',
            borderwidth=1,
            highlightthickness=1,
            highlightcolor=COLORS['accent'],
            highlightbackground=COLORS['border']
        )
    
    # Make the text widget configurer globally accessible
    globals()['configure_text_widget'] = configure_text_widget


def get_color(color_name):
    """Get a color value by name"""
    return COLORS.get(color_name, '#000000')
