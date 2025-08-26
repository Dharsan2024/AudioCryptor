"""
Custom modern widgets for the Audio Steganography application
"""

import tkinter as tk
from tkinter import ttk
from theme import get_color


class ModernFrame(ttk.Frame):
    """Modern styled frame"""
    
    def __init__(self, parent, style='Modern.TFrame', **kwargs):
        super().__init__(parent, style=style, **kwargs)


class ModernButton(ttk.Button):
    """Modern styled button"""
    
    def __init__(self, parent, text="", command=None, style='Modern.TButton', **kwargs):
        if command is None:
            command = lambda: None
        super().__init__(parent, text=text, command=command, style=style, **kwargs)


class ModernEntry(ttk.Entry):
    """Modern styled entry widget"""
    
    def __init__(self, parent, style='Modern.TEntry', **kwargs):
        super().__init__(parent, style=style, **kwargs)


class ModernLabel(ttk.Label):
    """Modern styled label"""
    
    def __init__(self, parent, text="", style='Modern.TLabel', **kwargs):
        super().__init__(parent, text=text, style=style, **kwargs)


class ModernProgressBar(ttk.Progressbar):
    """Modern styled progress bar"""
    
    def __init__(self, parent, style='Modern.Horizontal.TProgressbar', **kwargs):
        super().__init__(parent, style=style, **kwargs)


class ModernText(tk.Text):
    """Modern styled text widget"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        # Apply modern styling
        self.configure(
            bg=get_color('bg_light'),
            fg=get_color('text_light'),
            insertbackground=get_color('text_light'),
            selectbackground=get_color('primary'),
            selectforeground=get_color('text_light'),
            font=('Segoe UI', 10),
            relief='flat',
            borderwidth=1,
            highlightthickness=1,
            highlightcolor=get_color('accent'),
            highlightbackground=get_color('border'),
            wrap=tk.WORD
        )


class ModernScale(ttk.Scale):
    """Modern styled scale (slider)"""
    
    def __init__(self, parent, style='Modern.Horizontal.TScale', **kwargs):
        super().__init__(parent, style=style, **kwargs)


class ModernCheckbutton(ttk.Checkbutton):
    """Modern styled checkbutton"""
    
    def __init__(self, parent, text="", style='Modern.TCheckbutton', **kwargs):
        super().__init__(parent, text=text, style=style, **kwargs)


class CardFrame(ModernFrame):
    """Card-style frame with background"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, style='Card.TFrame', **kwargs)
        self.configure(padding=15)


class PasswordEntry(ModernFrame):
    """Password entry with show/hide toggle"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Create entry widget
        self.entry = ModernEntry(self)
        self.entry.configure(show='*')
        self.entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        # Create show/hide button
        self.show_var = tk.BooleanVar()
        self.toggle_btn = ModernButton(self, text="👁", command=self.toggle_visibility)
        self.toggle_btn.grid(row=0, column=1)
        
        # Configure grid weights
        self.grid_columnconfigure(0, weight=1)
        
    def toggle_visibility(self):
        """Toggle password visibility"""
        if self.show_var.get():
            self.entry.configure(show='')
            self.toggle_btn.configure(text="🙈")
        else:
            self.entry.configure(show='*')
            self.toggle_btn.configure(text="👁")
        self.show_var.set(not self.show_var.get())
        
    def get(self):
        """Get the entry value"""
        return self.entry.get()
        
    def set(self, value):
        """Set the entry value"""
        self.entry.delete(0, tk.END)
        self.entry.insert(0, value)
        
    def delete(self, first, last=None):
        """Delete text from entry"""
        self.entry.delete(first, last)
        
    def insert(self, index, string):
        """Insert text into entry"""
        self.entry.insert(index, string)


class FileSelector(ModernFrame):
    """File selector with browse button"""
    
    def __init__(self, parent, title="Select File", filetypes=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.title = title
        self.filetypes = filetypes or [("All files", "*.*")]
        
        # Create entry for file path
        self.path_var = tk.StringVar()
        self.entry = ModernEntry(self, textvariable=self.path_var, state='readonly')
        self.entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        # Create browse button
        self.browse_btn = ModernButton(self, text="Browse", command=self.browse_file)
        self.browse_btn.grid(row=0, column=1)
        
        # Configure grid weights
        self.grid_columnconfigure(0, weight=1)
        
    def browse_file(self):
        """Open file dialog to select file"""
        from tkinter import filedialog
        filename = filedialog.askopenfilename(
            title=self.title,
            filetypes=self.filetypes
        )
        if filename:
            self.path_var.set(filename)
            
    def get(self):
        """Get selected file path"""
        return self.path_var.get()
        
    def set(self, path):
        """Set file path"""
        self.path_var.set(path)


class StatusBar(ModernFrame):
    """Status bar for displaying messages"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        self.label = ModernLabel(self, textvariable=self.status_var)
        self.label.grid(row=0, column=0, sticky="w")
        
    def set_status(self, message, color=None):
        """Set status message"""
        self.status_var.set(message)
        if color:
            self.label.configure(foreground=color)
        else:
            self.label.configure(style='Modern.TLabel')
