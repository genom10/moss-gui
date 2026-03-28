"""
Reusable form input components using CustomTkinter.
"""
import customtkinter as ctk
from tkinter import filedialog
from pathlib import Path


class LabeledEntry(ctk.CTkFrame):
    """A labeled text entry field."""
    
    def __init__(self, master, label: str, placeholder: str = "", 
                 password: bool = False, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.label = ctk.CTkLabel(self, text=label, anchor="w")
        self.label.pack(fill="x", pady=(0, 2))
        
        self.entry = ctk.CTkEntry(self, placeholder_text=placeholder)
        if password:
            self.entry.configure(show="*")
        self.entry.pack(fill="x")
    
    def get(self) -> str:
        return self.entry.get()
    
    def set(self, value: str):
        self.entry.delete(0, 'end')
        self.entry.insert(0, value)
    
    def configure(self, **kwargs):
        if 'state' in kwargs:
            self.entry.configure(state=kwargs.pop('state'))
        super().configure(**kwargs)


class LabeledComboBox(ctk.CTkFrame):
    """A labeled combobox field."""
    
    def __init__(self, master, label: str, values: list, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.label = ctk.CTkLabel(self, text=label, anchor="w")
        self.label.pack(fill="x", pady=(0, 2))
        
        self.combobox = ctk.CTkComboBox(self, values=values)
        if values:
            self.combobox.set(values[0])
        self.combobox.pack(fill="x")
    
    def get(self) -> str:
        return self.combobox.get()
    
    def set(self, value: str):
        self.combobox.set(value)


class LabeledSlider(ctk.CTkFrame):
    """A labeled slider with value display."""

    def __init__(self, master, label: str, from_: int = 0, to: int = 100,
                 initial: int = 50, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.label_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.label_frame.pack(fill="x")

        self.label = ctk.CTkLabel(self.label_frame, text=label, anchor="w")
        self.label.pack(side="left")

        self.value_label = ctk.CTkLabel(
            self.label_frame,
            text=str(initial),
            width=40
        )
        self.value_label.pack(side="right")

        self.slider = ctk.CTkSlider(
            self,
            from_=from_,
            to=to,
            number_of_steps=int(to - from_),
            command=self._update_value
        )
        self.slider.set(initial)
        self.slider.pack(fill="x")

    def _update_value(self, value):
        self.value_label.configure(text=str(int(value)))

    def get(self) -> int:
        return int(self.slider.get())

    def set(self, value: int):
        self.slider.set(value)
        self.value_label.configure(text=str(int(value)))


class FilePicker(ctk.CTkFrame):
    """A file picker with text field and browse button."""
    
    def __init__(self, master, label: str, file_type: str = "all",
                 filetypes: dict = None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.file_type = file_type
        self.filetypes = filetypes or {
            "All files": "*.*",
            "Text files": "*.txt",
            "CSV files": "*.csv",
            "C/C++ files": "*.c *.cpp *.h *.hpp",
            "Python files": "*.py",
            "Java files": "*.java",
        }
        
        self.label = ctk.CTkLabel(self, text=label, anchor="w")
        self.label.pack(fill="x", pady=(0, 2))
        
        self.frame = ctk.CTkFrame(self, fg_color="transparent")
        self.frame.pack(fill="x")
        
        self.entry = ctk.CTkEntry(self.frame, placeholder_text="No file selected")
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.browse_btn = ctk.CTkButton(
            self.frame,
            text="Browse...",
            command=self._browse,
            width=80
        )
        self.browse_btn.pack(side="right")
    
    def _browse(self):
        if self.file_type == "directory":
            path = filedialog.askdirectory()
        else:
            filetypes = [(k, v) for k, v in self.filetypes.items()]
            path = filedialog.askopenfilename(filetypes=filetypes)
        
        if path:
            self.entry.delete(0, 'end')
            self.entry.insert(0, path)
    
    def get(self) -> str:
        return self.entry.get()
    
    def set(self, path: str):
        self.entry.delete(0, 'end')
        self.entry.insert(0, path)


class StatusLabel(ctk.CTkLabel):
    """A label that can show status with color coding."""
    
    STATUS_COLORS = {
        "success": "#2ecc71",   # Green
        "error": "#e74c3c",     # Red
        "warning": "#f39c12",   # Orange
        "info": "#3498db",      # Blue
        "default": "#95a5a6"    # Gray
    }
    
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            text="",
            font=ctk.CTkFont(size=12),
            **kwargs
        )
    
    def set_status(self, message: str, status: str = "default"):
        """Set status message with color."""
        self.configure(text=message)
        color = self.STATUS_COLORS.get(status, self.STATUS_COLORS["default"])
        self.configure(text_color=color)
    
    def success(self, message: str):
        self.set_status(message, "success")
    
    def error(self, message: str):
        self.set_status(message, "error")
    
    def warning(self, message: str):
        self.set_status(message, "warning")
    
    def info(self, message: str):
        self.set_status(message, "info")
