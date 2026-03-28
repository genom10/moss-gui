"""
Aliases Page - Manage email to Codeforces handle mappings.
"""
import customtkinter as ctk
import os
import csv
import re
from pathlib import Path
from tkinter import filedialog, messagebox

from utils.csv_handler import CSVHandler
from utils.codeforces_api import load_aliases_from_html, parse_html_handle
from components.form_inputs import LabeledEntry, StatusLabel, FilePicker


class UnmatchedHandlesDialog(ctk.CTkToplevel):
    """Dialog for reviewing and fixing unmatched HTML handles."""

    def __init__(self, parent, unmatched_files: list, on_confirm=None):
        super().__init__(parent)
        
        self.title("Review Unmatched Handles")
        self.geometry("700x500")
        self.transient(parent)
        self.grab_set()
        
        self.unmatched_files = unmatched_files
        self.on_confirm = on_confirm
        self.results = {}
        
        self._create_ui()
    
    def _create_ui(self):
        """Create dialog UI."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Title
        title = ctk.CTkLabel(
            self,
            text=f"Review {len(self.unmatched_files)} Unmatched Files",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.grid(row=0, column=0, pady=10, sticky="w")
        
        # Scrollable frame with file entries
        scroll_frame = ctk.CTkScrollableFrame(self)
        scroll_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        self.entries = {}
        for file_path in self.unmatched_files:
            self._create_file_entry(scroll_frame, file_path)
        
        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=2, column=0, pady=10)
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=self.destroy,
            width=100,
            fg_color="gray"
        )
        cancel_btn.pack(side="left", padx=5)
        
        confirm_btn = ctk.CTkButton(
            btn_frame,
            text="Add to Table",
            command=self._on_confirm,
            width=120
        )
        confirm_btn.pack(side="left", padx=5)
    
    def _create_file_entry(self, parent, file_path: Path):
        """Create entry row for a file."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=5)
        
        # Student name from filename
        name_part = file_path.stem.split('_assignsubmission')[0]
        name_parts = name_part.rsplit('_', 1)
        student_name = name_parts[0] if len(name_parts) == 2 else name_part
        student_id = name_parts[1] if len(name_parts) == 2 else ""
        
        # Read HTML content
        try:
            content = file_path.read_text(encoding='utf-8')
            # Extract text from <p> tag
            p_match = re.search(r'<p>(.*?)</p>', content, re.IGNORECASE | re.DOTALL)
            html_text = p_match.group(1) if p_match else content
            # Strip HTML tags for display and replace newlines
            display_text = re.sub(r'<[^>]+>', ' ', html_text).strip()
            display_text = display_text.replace('\n', ' ').replace('\r', ' ')
            display_text = display_text[:200]  # Show up to 200 characters
        except Exception:
            display_text = "(could not read file)"
        
        # Name label
        name_label = ctk.CTkLabel(
            frame,
            text=f"{student_name}",
            font=ctk.CTkFont(weight="bold"),
            width=150
        )
        name_label.pack(side="left", padx=5)
        
        # HTML content preview (selectable text box)
        content_text = ctk.CTkTextbox(frame, height=40, wrap="word")
        content_text.pack(side="left", padx=5, fill="x", expand=True)
        content_text.insert("0.0", display_text)
        content_text.configure(state="disabled")  # Read-only but selectable
        
        # Handle entry
        handle_entry = ctk.CTkEntry(frame, placeholder_text="Enter handle", width=150)
        handle_entry.pack(side="left", padx=5)
        
        self.entries[str(file_path)] = {
            'name': student_name,
            'id': student_id,
            'handle': handle_entry
        }
    
    def _on_confirm(self):
        """Collect results and close dialog."""
        for file_path, data in self.entries.items():
            handle = data['handle'].get().strip()
            if handle:
                self.results[data['name']] = {
                    'handle': handle,
                    'id': data['id'],
                    'file': file_path
                }
        self.destroy()
        if self.on_confirm:
            self.on_confirm(self.results)


class AliasesPage(ctk.CTkFrame):
    """Page 2: Manage student aliases (email to handle mapping)."""
    
    def __init__(self, master, on_next=None, on_back=None, **kwargs):
        super().__init__(master, **kwargs)

        self.on_next = on_next
        self.on_back = on_back
        self.aliases = []
        self.csv_handler = CSVHandler()

        self._create_ui()
        # Load aliases in background to avoid blocking UI
        self.after(100, self._load_existing_aliases_async)
    
    def _create_ui(self):
        """Create the page UI."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self._create_header(header_frame)
        
        # Main content - table with controls
        content_frame = ctk.CTkFrame(self)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self._create_content(content_frame)
    
    def _create_header(self, parent):
        """Create header with title and actions."""
        parent.grid_columnconfigure(0, weight=1)
        
        # Title
        title = ctk.CTkLabel(
            parent,
            text="Student Aliases",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.grid(row=0, column=0, sticky="w", pady=10)
        
        # Action buttons
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.grid(row=0, column=1, sticky="e", pady=10)
        
        self.import_btn = ctk.CTkButton(
            btn_frame,
            text="Import CSV",
            command=self._import_csv,
            width=100
        )
        self.import_btn.pack(side="left", padx=5)
        
        self.export_btn = ctk.CTkButton(
            btn_frame,
            text="Export CSV",
            command=self._export_csv,
            width=100
        )
        self.export_btn.pack(side="left", padx=5)
        
        self.extract_btn = ctk.CTkButton(
            btn_frame,
            text="Extract from HTML",
            command=self._extract_from_html,
            width=120
        )
        self.extract_btn.pack(side="left", padx=5)
    
    def _create_content(self, parent):
        """Create main content area."""
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)
        
        # Table container
        table_container = ctk.CTkFrame(parent)
        table_container.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        self._create_table(table_container)
        
        # Bottom controls
        controls_frame = ctk.CTkFrame(parent, fg_color="transparent")
        controls_frame.grid(row=1, column=0, sticky="ew")
        self._create_controls(controls_frame)
    
    def _create_table(self, parent):
        """Create the aliases table."""
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)
        
        # Create scrollable frame with table
        self.scroll_frame = ctk.CTkScrollableFrame(parent)
        self.scroll_frame.grid(row=0, column=0, sticky="nsew")
        
        # Table header
        self._create_table_header()
        
        # Table rows container
        self.rows_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.rows_frame.pack(fill="both", expand=True)
    
    def _create_table_header(self):
        """Create table header row."""
        header_frame = ctk.CTkFrame(self.scroll_frame)
        header_frame.pack(fill="x", pady=(0, 5))
        
        headers = [
            ("Student Name", 150),
            ("Student ID", 80),
            ("Email", 200),
            ("Codeforces Handle", 150),
            ("Actions", 100)
        ]
        
        for text, width in headers:
            label = ctk.CTkLabel(
                header_frame,
                text=text,
                font=ctk.CTkFont(weight="bold"),
                width=width
            )
            label.pack(side="left", padx=5, pady=5)
    
    def _create_controls(self, parent):
        """Create bottom control buttons."""
        parent.grid_columnconfigure(0, weight=1)
        
        # Add row form
        form_frame = ctk.CTkFrame(parent)
        form_frame.grid(row=0, column=0, sticky="ew", pady=10)
        
        # Name
        self.new_name_entry = LabeledEntry(form_frame, label="Name", placeholder="John")
        self.new_name_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        # Surname
        self.new_surname_entry = LabeledEntry(form_frame, label="Surname", placeholder="Doe")
        self.new_surname_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        # ID
        self.new_id_entry = LabeledEntry(form_frame, label="ID", placeholder="490000")
        self.new_id_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        # Email
        self.new_email_entry = LabeledEntry(form_frame, label="Email", placeholder="email@university.edu")
        self.new_email_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        # Handle
        self.new_handle_entry = LabeledEntry(form_frame, label="Handle", placeholder="codeforces_handle")
        self.new_handle_entry.pack(side="left", padx=5, expand=True, fill="x")
        
        # Add button
        add_btn = ctk.CTkButton(
            form_frame,
            text="Add",
            command=self._add_row,
            width=60
        )
        add_btn.pack(side="left", padx=10)
        
        # Navigation buttons
        nav_frame = ctk.CTkFrame(parent, fg_color="transparent")
        nav_frame.grid(row=1, column=0, sticky="e", pady=10)
        
        self.back_btn = ctk.CTkButton(
            nav_frame,
            text="← Back",
            command=self._on_back,
            width=100,
            fg_color="gray"
        )
        self.back_btn.pack(side="left", padx=5)
        
        self.save_btn = ctk.CTkButton(
            nav_frame,
            text="Save Aliases",
            command=self._save_aliases,
            width=120
        )
        self.save_btn.pack(side="left", padx=5)
        
        self.next_btn = ctk.CTkButton(
            nav_frame,
            text="Proceed to Grading →",
            command=self._on_next,
            width=160
        )
        self.next_btn.pack(side="left", padx=5)
        
        # Status label
        self.status_label = StatusLabel(parent, anchor="w")
        self.status_label.grid(row=2, column=0, sticky="w", pady=(0, 10))
    
    def _add_row(self, name=None, surname=None, id_=None, email=None, alias=None):
        """Add a row to the table."""
        row_frame = ctk.CTkFrame(self.rows_frame, fg_color="transparent")
        row_frame.pack(fill="x", pady=2)
        
        # Name
        name_entry = ctk.CTkEntry(row_frame, placeholder_text="Name", width=150)
        name_entry.pack(side="left", padx=5)
        if name:
            name_entry.insert(0, name)
        
        # Surname
        surname_entry = ctk.CTkEntry(row_frame, placeholder_text="Surname", width=120)
        surname_entry.pack(side="left", padx=5)
        if surname:
            surname_entry.insert(0, surname)
        
        # ID
        id_entry = ctk.CTkEntry(row_frame, placeholder_text="ID", width=80)
        id_entry.pack(side="left", padx=5)
        if id_:
            id_entry.insert(0, id_)
        
        # Email
        email_entry = ctk.CTkEntry(row_frame, placeholder_text="Email", width=200)
        email_entry.pack(side="left", padx=5)
        if email:
            email_entry.insert(0, email)
        
        # Handle
        handle_entry = ctk.CTkEntry(row_frame, placeholder_text="Handle", width=150)
        handle_entry.pack(side="left", padx=5)
        if alias:
            handle_entry.insert(0, alias)
        
        # Delete button
        delete_btn = ctk.CTkButton(
            row_frame,
            text="Delete",
            command=lambda: self._delete_row(row_frame),
            width=60,
            fg_color="#e74c3c"
        )
        delete_btn.pack(side="left", padx=5)
        
        # Store references
        row_frame.entries = {
            'name': name_entry,
            'surname': surname_entry,
            'id': id_entry,
            'email': email_entry,
            'alias': handle_entry
        }
    
    def _delete_row(self, row_frame):
        """Delete a row from the table."""
        row_frame.destroy()

    def _load_existing_aliases_async(self):
        """Load aliases from CSV in background to avoid blocking UI."""
        import threading
        
        def load_thread():
            csv_path = "students_aliases.csv"
            if os.path.exists(csv_path):
                self.aliases = self.csv_handler.load_aliases(csv_path)
                # Update UI on main thread
                self.after(0, self._populate_table_from_aliases)
        
        thread = threading.Thread(target=load_thread, daemon=True)
        thread.start()

    def _populate_table_from_aliases(self):
        """Populate table with loaded aliases."""
        for alias in self.aliases:
            self._add_row(
                name=alias.get('name', ''),
                surname=alias.get('surname', ''),
                id_=alias.get('id', ''),
                email=alias.get('email', ''),
                alias=alias.get('alias', '')
            )

    def _load_existing_aliases(self):
        """Load aliases from existing CSV file (synchronous version)."""
        csv_path = "students_aliases.csv"
        if os.path.exists(csv_path):
            self.aliases = self.csv_handler.load_aliases(csv_path)
            for alias in self.aliases:
                self._add_row(
                    name=alias.get('name', ''),
                    surname=alias.get('surname', ''),
                    id_=alias.get('id', ''),
                    email=alias.get('email', ''),
                    alias=alias.get('alias', '')
                )
    
    def _import_csv(self):
        """Import aliases from CSV file."""
        file_path = filedialog.askopenfilename(
            title="Import Aliases CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            aliases = self.csv_handler.load_aliases(file_path)
            for alias in aliases:
                self._add_row(
                    name=alias.get('name', ''),
                    surname=alias.get('surname', ''),
                    id_=alias.get('id', ''),
                    email=alias.get('email', ''),
                    alias=alias.get('alias', '')
                )
            self.status_label.success(f"Imported {len(aliases)} aliases")
    
    def _export_csv(self):
        """Export aliases to CSV file."""
        file_path = filedialog.asksaveasfilename(
            title="Export Aliases CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            aliases = self._get_aliases_from_table()
            if self.csv_handler.save_aliases(file_path, aliases):
                self.status_label.success(f"Exported {len(aliases)} aliases to {file_path}")
            else:
                self.status_label.error("Failed to export aliases")
    
    def _extract_from_html(self):
        """Extract handles from HTML files in aliases folder."""
        aliases_folder = "aliases"
        if not os.path.exists(aliases_folder):
            self.status_label.error(f"Aliases folder not found: {aliases_folder}")
            return

        # Find all HTML files and parse them
        aliases_path = Path(aliases_folder)
        html_files = [f for f in aliases_path.glob("*.html") if not f.name.startswith('.')]
        
        # Parse handles and track unmatched files
        html_aliases = {}
        unmatched_files = []
        
        for html_file in html_files:
            try:
                content = html_file.read_text(encoding='utf-8')
                handle = parse_html_handle(content)
                
                # Extract student name from filename
                name_part = html_file.stem.split('_assignsubmission')[0]
                name_parts = name_part.rsplit('_', 1)
                student_name = name_parts[0] if len(name_parts) == 2 else name_part
                student_id = name_parts[1] if len(name_parts) == 2 else ""
                
                if handle:
                    html_aliases[student_name] = {
                        'handle': handle,
                        'id': student_id,
                        'source': 'HTML'
                    }
                else:
                    unmatched_files.append(html_file)
            except Exception as e:
                print(f"Error parsing {html_file.name}: {e}")
                unmatched_files.append(html_file)

        if not html_aliases and not unmatched_files:
            self.status_label.warning("No HTML files found")
            return

        # Load existing student names from CSV
        students_csv = "students_aliases.csv"
        students = self.csv_handler.load_students(students_csv) if os.path.exists(students_csv) else []

        # Match HTML aliases with students
        added_count = 0
        for student in students:
            name = student.get('name', '')
            if name in html_aliases:
                handle_data = html_aliases[name]
                self._add_row(
                    name=name,
                    surname=student.get('surname', ''),
                    id_=student.get('id', ''),
                    email=student.get('email', ''),
                    alias=handle_data.get('handle', '')
                )
                added_count += 1

        # Also add any unmatched HTML aliases (no student record)
        for name, handle_data in html_aliases.items():
            if name not in [s.get('name', '') for s in students]:
                self._add_row(
                    name=name,
                    alias=handle_data.get('handle', '')
                )
                added_count += 1

        # Show dialog for unmatched files
        if unmatched_files:
            self._show_unmatched_dialog(unmatched_files)

        self.status_label.success(f"Extracted {added_count} handles from HTML files ({len(unmatched_files)} need manual review)")

    def _show_unmatched_dialog(self, unmatched_files: list):
        """Show dialog to manually enter handles for unmatched files."""
        def on_confirm(results):
            for name, data in results.items():
                self._add_row(
                    name=name,
                    id_=data.get('id', ''),
                    alias=data['handle']
                )
            if results:
                self.status_label.success(f"Added {len(results)} handles from review")
        
        dialog = UnmatchedHandlesDialog(self, unmatched_files, on_confirm=on_confirm)
    
    def _get_aliases_from_table(self) -> list:
        """Get aliases data from table entries."""
        aliases = []
        for child in self.rows_frame.winfo_children():
            if hasattr(child, 'entries'):
                entries = child.entries
                aliases.append({
                    'name': entries['name'].get(),
                    'surname': entries['surname'].get(),
                    'id': entries['id'].get(),
                    'email': entries['email'].get(),
                    'alias': entries['alias'].get()
                })
        return aliases
    
    def _save_aliases(self):
        """Save aliases to CSV file."""
        aliases = self._get_aliases_from_table()
        csv_path = "students_aliases.csv"
        
        if self.csv_handler.save_aliases(csv_path, aliases):
            self.status_label.success(f"Saved {len(aliases)} aliases to {csv_path}")
        else:
            self.status_label.error("Failed to save aliases")
    
    def _on_next(self):
        """Handle next button click."""
        self._save_aliases()  # Auto-save before proceeding
        if self.on_next:
            self.on_next()
    
    def _on_back(self):
        """Handle back button click."""
        if self.on_back:
            self.on_back()
    
    def get_aliases(self) -> list:
        """Get current aliases data."""
        return self._get_aliases_from_table()
