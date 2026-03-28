"""
Download Page - Fetch submissions from Codeforces.
"""
import customtkinter as ctk
import os
import webbrowser
import threading
import json
from pathlib import Path
from tkinter import filedialog

from utils.codeforces_api import CodeforcesAPI
from components.form_inputs import LabeledEntry, StatusLabel
from components.data_table import DataTable

# Config file path for storing form data
CONFIG_FILE = Path("download_config.json")


class DownloadPage(ctk.CTkFrame):
    """Page 1: Download submissions from Codeforces."""

    def __init__(self, master, on_next=None, **kwargs):
        super().__init__(master, **kwargs)

        self.on_next = on_next
        self.api = None
        self.submissions_data = []

        self._create_ui()
        self._load_saved_data()

    def _create_ui(self):
        """Create the page UI."""
        # Main container with two columns
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        
        # Left column - Form inputs
        form_frame = ctk.CTkFrame(self)
        form_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self._create_form(form_frame)
        
        # Right column - Data table
        table_frame = ctk.CTkFrame(self)
        table_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self._create_table(table_frame)
    
    def _create_form(self, parent):
        """Create form inputs."""
        parent.grid_rowconfigure(7, weight=1)

        # Title
        title = ctk.CTkLabel(
            parent,
            text="Download Submissions",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.grid(row=0, column=0, pady=(10, 20), sticky="w")

        # Contest ID
        self.contest_id_entry = LabeledEntry(
            parent,
            label="Contest ID",
            placeholder="e.g., 656462"
        )
        self.contest_id_entry.grid(row=1, column=0, sticky="ew", pady=5)

        # Assignment Number
        self.assignment_entry = LabeledEntry(
            parent,
            label="Assignment Number",
            placeholder="e.g., 3"
        )
        self.assignment_entry.set("1")
        self.assignment_entry.grid(row=2, column=0, sticky="ew", pady=5)

        # API Key
        self.api_key_entry = LabeledEntry(
            parent,
            label="Codeforces API Key",
            placeholder="Enter your API key",
            password=True
        )
        self.api_key_entry.grid(row=3, column=0, sticky="ew", pady=5)

        # API Secret
        self.api_secret_entry = LabeledEntry(
            parent,
            label="Codeforces API Secret",
            placeholder="Enter your API secret",
            password=True
        )
        self.api_secret_entry.grid(row=4, column=0, sticky="ew", pady=5)

        # Source files indicator
        self.source_files_label = ctk.CTkLabel(
            parent,
            text="",
            font=ctk.CTkFont(size=11),
            anchor="w"
        )
        self.source_files_label.grid(row=5, column=0, sticky="ew", pady=5)

        # Buttons
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.grid(row=6, column=0, sticky="ew", pady=20)

        self.download_btn = ctk.CTkButton(
            btn_frame,
            text="Download",
            command=self._download,
            width=120
        )
        self.download_btn.pack(side="left", padx=5)

        self.open_folder_btn = ctk.CTkButton(
            btn_frame,
            text="Open Folder",
            command=self._open_folder,
            width=120,
            state="disabled"
        )
        self.open_folder_btn.pack(side="left", padx=5)

        # Status label
        self.status_label = StatusLabel(parent, anchor="w")
        self.status_label.grid(row=7, column=0, sticky="ew", pady=10)

        # Next button (bottom right)
        self.next_btn = ctk.CTkButton(
            parent,
            text="Proceed to Aliases →",
            command=self._on_next,
            state="disabled",
            width=200
        )
        self.next_btn.grid(row=8, column=0, sticky="se", pady=10)
    
    def _create_table(self, parent):
        """Create submissions data table."""
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        # Title
        title = ctk.CTkLabel(
            parent,
            text="Submissions",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.grid(row=0, column=0, pady=(10, 5), sticky="w")

        # Table - use grid and sticky to fill space
        columns = ["Handle", "Submission ID", "Passed Tests", "Verdict", "Status"]
        self.table = DataTable(parent, columns=columns)
        self.table.grid(row=1, column=0, sticky="nsew")
    
    def _download(self):
        """Handle download button click."""
        contest_id = self.contest_id_entry.get().strip()
        assignment_num = self.assignment_entry.get().strip()
        api_key = self.api_key_entry.get().strip()
        api_secret = self.api_secret_entry.get().strip()

        # Validate inputs
        if not contest_id:
            self.status_label.error("Please enter Contest ID")
            return
        if not assignment_num or not assignment_num.isdigit():
            self.status_label.error("Please enter a valid Assignment Number")
            return
        if not api_key:
            self.status_label.error("Please enter API Key")
            return
        if not api_secret:
            self.status_label.error("Please enter API Secret")
            return

        # Disable button during download
        self.download_btn.configure(state="disabled", text="Downloading...")
        self.status_label.info("Fetching submissions from Codeforces...")
        self.table.clear()

        # Run download in separate thread to avoid blocking UI
        thread = threading.Thread(
            target=self._run_download,
            args=(contest_id, assignment_num, api_key, api_secret),
            daemon=True
        )
        thread.start()

    def _run_download(self, contest_id, assignment_num, api_key, api_secret):
        """Run the download process."""
        try:
            self.api = CodeforcesAPI(api_key, api_secret)
            success, message, submissions = self.api.download_all(
                contest_id, int(assignment_num)
            )

            if success:
                self.status_label.success(message)
                self.submissions_data = submissions

                # Check source files status
                files_exist, file_count, files_msg = self.api.check_source_files_exist(
                    int(assignment_num), contest_id
                )
                
                # Update source files indicator
                if files_exist:
                    self.source_files_label.configure(
                        text=f"✓ {files_msg} in Assignment{assignment_num}/{contest_id}/",
                        text_color="#2ecc71"
                    )
                else:
                    self.source_files_label.configure(
                        text=f"⚠ Source files not found. Place them in: Assignment{assignment_num}/{contest_id}/",
                        text_color="#f39c12"
                    )

                # Populate table
                for sub in submissions:
                    handle = sub[0]
                    submission_id = sub[1]
                    passed = sub[2]
                    verdict = "OK" if int(passed) > 0 else "—"
                    status = "✓ Downloaded" if files_exist else "⚠ Missing source"
                    self.table.add_row([
                        handle,
                        submission_id,
                        f"{passed}/—",
                        verdict,
                        status
                    ])

                # Enable buttons
                self.open_folder_btn.configure(state="normal")
                self.next_btn.configure(state="normal")
                
                # Save form data for next launch
                self._save_data()
            else:
                self.status_label.error(message)

        except Exception as e:
            self.status_label.error(f"Error: {str(e)}")
        finally:
            # Re-enable download button
            self.after(0, lambda: self.download_btn.configure(state="normal", text="Download"))
    
    def _open_folder(self):
        """Open the assignment folder in file explorer."""
        assignment_num = self.assignment_entry.get().strip()
        contest_id = self.contest_id_entry.get().strip()
        
        if not assignment_num or not contest_id:
            return
        
        folder_path = Path(f"Assignment{assignment_num}/{contest_id}")
        if folder_path.exists():
            webbrowser.open(str(folder_path.absolute()))
        else:
            self.status_label.warning(f"Folder not found: {folder_path}")
    
    def _on_next(self):
        """Handle next button click."""
        if self.on_next:
            self.on_next()
    
    def get_data(self) -> dict:
        """Get page data for other pages."""
        return {
            'contest_id': self.contest_id_entry.get().strip(),
            'assignment_num': self.assignment_entry.get().strip(),
            'submissions': self.submissions_data
        }

    def _save_data(self):
        """Save form data to config file."""
        data = {
            'contest_id': self.contest_id_entry.get().strip(),
            'assignment_num': self.assignment_entry.get().strip(),
            'api_key': self.api_key_entry.get().strip(),
            'api_secret': self.api_secret_entry.get().strip()
        }
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Failed to save config: {e}")

    def _load_saved_data(self):
        """Load saved form data from config file."""
        if not CONFIG_FILE.exists():
            return
        
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
            
            if data.get('contest_id'):
                self.contest_id_entry.set(data['contest_id'])
            if data.get('assignment_num'):
                self.assignment_entry.set(data['assignment_num'])
            if data.get('api_key'):
                self.api_key_entry.set(data['api_key'])
            if data.get('api_secret'):
                self.api_secret_entry.set(data['api_secret'])
        except Exception as e:
            print(f"Failed to load config: {e}")
