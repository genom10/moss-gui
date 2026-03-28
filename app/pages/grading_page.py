"""
Grading Page - Run MOSS plagiarism detection.
"""
import customtkinter as ctk
import os
import json
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox

from utils.moss_runner import MossRunner
from components.form_inputs import LabeledEntry, LabeledComboBox, LabeledSlider, FilePicker, StatusLabel

# Config file path for storing MOSS settings
MOSS_CONFIG_FILE = Path("moss_config.json")


class GradingPage(ctk.CTkFrame):
    """Page 3: Run MOSS plagiarism detection."""

    def __init__(self, master, on_back=None, **kwargs):
        super().__init__(master, **kwargs)

        self.on_back = on_back
        self.moss_runner = None
        self.selected_files = []

        self._create_ui()
        self._load_saved_settings()
    
    def _create_ui(self):
        """Create the page UI."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self._create_header(header_frame)
        
        # Main content
        content_frame = ctk.CTkFrame(self)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self._create_content(content_frame)
    
    def _create_header(self, parent):
        """Create header with title."""
        parent.grid_columnconfigure(0, weight=1)
        
        title = ctk.CTkLabel(
            parent,
            text="MOSS Plagiarism Detection",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.grid(row=0, column=0, sticky="w", pady=10)
    
    def _create_content(self, parent):
        """Create main content area."""
        parent.grid_columnconfigure(0, weight=2)
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_rowconfigure(0, weight=1)
        
        # Left column - Settings
        settings_frame = ctk.CTkFrame(parent)
        settings_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self._create_settings(settings_frame)
        
        # Right column - File list and results
        files_frame = ctk.CTkFrame(parent)
        files_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        self._create_files_panel(files_frame)
    
    def _create_settings(self, parent):
        """Create MOSS settings panel."""
        parent.grid_rowconfigure(5, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        # Title
        title = ctk.CTkLabel(
            parent,
            text="MOSS Settings",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.grid(row=0, column=0, sticky="w", pady=(10, 20))
        
        # MOSS User ID
        self.user_id_entry = LabeledEntry(
            parent,
            label="MOSS User ID",
            placeholder="Enter your MOSS user ID"
        )
        self.user_id_entry.grid(row=1, column=0, sticky="ew", pady=5)
        
        # Language
        languages = MossRunner.SUPPORTED_LANGUAGES
        self.language_combo = LabeledComboBox(
            parent,
            label="Programming Language",
            values=languages
        )
        self.language_combo.set("cc")  # Default to C++
        self.language_combo.grid(row=2, column=0, sticky="ew", pady=5)
        
        # Max Matches slider
        self.max_matches_slider = LabeledSlider(
            parent,
            label="Max Matches (-m)",
            from_=1,
            to=100,
            initial=10
        )
        self.max_matches_slider.grid(row=3, column=0, sticky="ew", pady=5)
        
        # Comment
        self.comment_entry = LabeledEntry(
            parent,
            label="Comment (for report)",
            placeholder="e.g., Assignment 3 2025"
        )
        self.comment_entry.grid(row=4, column=0, sticky="ew", pady=5)
        
        # Base file
        self.base_file_picker = FilePicker(
            parent,
            label="Base File (optional)",
            filetypes={
                "All files": "*.*",
                "C/C++ files": "*.c *.cpp *.h *.hpp *.cc",
                "Python files": "*.py",
                "Java files": "*.java",
            }
        )
        self.base_file_picker.grid(row=5, column=0, sticky="ew", pady=5)
        
        # Action buttons
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.grid(row=6, column=0, sticky="ew", pady=20)
        
        self.select_files_btn = ctk.CTkButton(
            btn_frame,
            text="Select Files",
            command=self._select_files,
            width=120
        )
        self.select_files_btn.pack(side="left", padx=5)
        
        self.run_moss_btn = ctk.CTkButton(
            btn_frame,
            text="Run MOSS",
            command=self._run_moss,
            width=120,
            fg_color="#27ae60"
        )
        self.run_moss_btn.pack(side="left", padx=5)
        
        # Status label
        self.status_label = StatusLabel(parent, anchor="w", justify="left")
        self.status_label.grid(row=7, column=0, sticky="ew", pady=10)
        
        # Navigation
        nav_frame = ctk.CTkFrame(parent, fg_color="transparent")
        nav_frame.grid(row=8, column=0, sticky="e", pady=10)
        
        self.back_btn = ctk.CTkButton(
            nav_frame,
            text="← Back",
            command=self._on_back,
            width=100,
            fg_color="gray"
        )
        self.back_btn.pack(side="left", padx=5)
    
    def _create_files_panel(self, parent):
        """Create files list and results panel."""
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_rowconfigure(2, weight=0)
        parent.grid_columnconfigure(0, weight=1)
        
        # Files title
        files_title = ctk.CTkLabel(
            parent,
            text="Selected Files",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        files_title.grid(row=0, column=0, sticky="w", pady=(10, 5))
        
        # Files list (scrollable)
        self.files_scroll = ctk.CTkScrollableFrame(parent, height=200)
        self.files_scroll.grid(row=1, column=0, sticky="ew", pady=5)
        
        # Result section
        result_frame = ctk.CTkFrame(parent)
        result_frame.grid(row=2, column=0, sticky="ew", pady=(20, 10))
        self._create_result_section(result_frame)
    
    def _create_result_section(self, parent):
        """Create MOSS result section."""
        parent.grid_columnconfigure(0, weight=1)
        
        result_title = ctk.CTkLabel(
            parent,
            text="Result",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        result_title.grid(row=0, column=0, sticky="w", pady=(10, 5))
        
        # Result URL display
        self.result_frame = ctk.CTkFrame(parent, fg_color="#34495e")
        self.result_frame.grid(row=1, column=0, sticky="ew", pady=5)
        
        self.result_label = ctk.CTkLabel(
            self.result_frame,
            text="No results yet",
            font=ctk.CTkFont(size=12)
        )
        self.result_label.pack(pady=15, padx=10)
        
        self.open_report_btn = ctk.CTkButton(
            self.result_frame,
            text="Open Report in Browser",
            command=self._open_report,
            state="disabled",
            width=200
        )
        self.open_report_btn.pack(pady=(0, 15))
        
        self.result_url = ""
    
    def _select_files(self):
        """Open file dialog to select submission files."""
        # Default to latest_submissions folder
        initial_dir = "Assignment1/latest_submissions"
        
        # Try to find the most recent assignment folder
        for i in range(10, 0, -1):
            test_dir = f"Assignment{i}/latest_submissions"
            if os.path.exists(test_dir):
                initial_dir = test_dir
                break
        
        files = filedialog.askopenfilenames(
            title="Select Submission Files",
            initialdir=initial_dir,
            filetypes=[
                ("Source code", "*.c *.cpp *.cc *.h *.hpp *.java *.py *.js"),
                ("All files", "*.*")
            ]
        )
        
        if files:
            self.selected_files = list(files)
            self._update_files_list()
            self.status_label.info(f"Selected {len(files)} files")
    
    def _update_files_list(self):
        """Update the files list display."""
        # Clear existing
        for widget in self.files_scroll.winfo_children():
            widget.destroy()
        
        # Add files
        for file_path in self.selected_files:
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            size_str = self._format_size(file_size)
            
            file_frame = ctk.CTkFrame(self.files_scroll)
            file_frame.pack(fill="x", pady=2)
            
            name_label = ctk.CTkLabel(file_frame, text=file_name, width=200, anchor="w")
            name_label.pack(side="left", padx=5, fill="x", expand=True)
            
            size_label = ctk.CTkLabel(file_frame, text=size_str, width=60, anchor="e")
            size_label.pack(side="right", padx=5)
    
    def _format_size(self, size: int) -> str:
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    def _run_moss(self):
        """Run MOSS plagiarism detection."""
        user_id = self.user_id_entry.get().strip()

        # Validate inputs
        if not user_id:
            self.status_label.error("Please enter MOSS User ID")
            return

        # Save settings before running
        self._save_settings()

        if not self.selected_files:
            self.status_label.error("Please select files to check")
            return

        # Disable button during processing
        self.run_moss_btn.configure(state="disabled", text="Running...")
        self.status_label.info("Running MOSS plagiarism detection...")

        # Run MOSS
        self.after(100, lambda: self._run_moss_process(user_id))
    
    def _run_moss_process(self, user_id: str):
        """Run MOSS process in background."""
        try:
            self.moss_runner = MossRunner(user_id)
            
            success, message, result_url = self.moss_runner.run_moss(
                files=self.selected_files,
                language=self.language_combo.get(),
                max_matches=self.max_matches_slider.get(),
                comment=self.comment_entry.get(),
                base_file=self.base_file_picker.get() if self.base_file_picker.get() else None
            )
            
            if success:
                self.status_label.success(message)
                self.result_url = result_url
                self.result_label.configure(text=result_url)
                self.open_report_btn.configure(state="normal")
                # Save settings for next time
                self._save_settings()
                # Save result URL for analysis page
                self._save_result_url(result_url)
            else:
                self.status_label.error(message)
                self.result_label.configure(text="Failed to run MOSS")
                
        except Exception as e:
            self.status_label.error(f"Error: {str(e)}")
            self.result_label.configure(text="Error occurred")
        finally:
            self.run_moss_btn.configure(state="normal", text="Run MOSS")
    
    def _open_report(self):
        """Open MOSS report in browser."""
        if self.result_url:
            webbrowser.open(self.result_url)
    
    def _on_back(self):
        """Handle back button click."""
        if self.on_back:
            self.on_back()
    
    def set_assignment_info(self, assignment_num: str, contest_id: str):
        """Set assignment info from download page."""
        if assignment_num and contest_id:
            default_comment = f"Assignment {assignment_num} - Contest {contest_id}"
            self.comment_entry.set(default_comment)

    def _save_settings(self):
        """Save MOSS settings to config file."""
        data = {
            'user_id': self.user_id_entry.get().strip(),
            'language': self.language_combo.get(),
            'max_matches': self.max_matches_slider.get(),
            'comment': self.comment_entry.get().strip(),
            'base_file': self.base_file_picker.get().strip()
        }
        try:
            with open(MOSS_CONFIG_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Failed to save MOSS config: {e}")

    def _save_result_url(self, url: str):
        """Save result URL for analysis page."""
        try:
            result_file = Path("moss_result.txt")
            result_file.write_text(url)
        except Exception as e:
            print(f"Failed to save result URL: {e}")

    def _load_saved_settings(self):
        """Load saved MOSS settings from config file."""
        if not MOSS_CONFIG_FILE.exists():
            print(f"MOSS config file not found: {MOSS_CONFIG_FILE.absolute()}")
            return
        
        try:
            with open(MOSS_CONFIG_FILE, 'r') as f:
                data = json.load(f)
            
            print(f"Loaded MOSS config: {data}")
            
            if data.get('user_id'):
                self.user_id_entry.set(data['user_id'])
                print(f"Set user_id to: {data['user_id']}")
            if data.get('language'):
                self.language_combo.set(data['language'])
            if data.get('max_matches'):
                self.max_matches_slider.set(data['max_matches'])
            if data.get('comment'):
                self.comment_entry.set(data['comment'])
            if data.get('base_file'):
                self.base_file_picker.set(data['base_file'])
        except Exception as e:
            print(f"Failed to load MOSS config: {e}")
