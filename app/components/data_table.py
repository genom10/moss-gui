"""
Reusable scrollable data table component using CustomTkinter.
"""
import customtkinter as ctk
from tkinter import ttk


class ScrollableTable(ctk.CTkFrame):
    """A scrollable table widget with customizable columns."""
    
    def __init__(self, master, columns: list, height: int = 200, **kwargs):
        super().__init__(master, **kwargs)
        
        self.columns = columns
        self.rows = []
        self.checkboxes = []
        
        # Create scrollable frame
        self.scroll_frame = ctk.CTkScrollableFrame(self, height=height)
        self.scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create header
        self._create_header()
    
    def _create_header(self):
        """Create table header row."""
        header_frame = ctk.CTkFrame(self.scroll_frame)
        header_frame.pack(fill="x", pady=(0, 2))
        
        for i, col in enumerate(self.columns):
            label = ctk.CTkLabel(
                header_frame,
                text=col,
                font=ctk.CTkFont(weight="bold"),
                width=120 if i > 0 else 40
            )
            label.pack(side="left", padx=2, pady=5)
    
    def add_row(self, values: list, checkbox: bool = False):
        """Add a row to the table."""
        row_frame = ctk.CTkFrame(self.scroll_frame)
        row_frame.pack(fill="x", pady=1)
        
        row_data = {}
        
        if checkbox:
            cb = ctk.CTkCheckBox(row_frame, text="")
            cb.pack(side="left", padx=5, pady=5)
            self.checkboxes.append((cb, values))
        
        for i, (col, val) in enumerate(zip(self.columns, values)):
            label = ctk.CTkLabel(row_frame, text=str(val), width=120 if i > 0 else 40)
            label.pack(side="left", padx=2, pady=5)
            row_data[col] = val
        
        self.rows.append(row_frame)
        self.rows[-1].data = row_data
    
    def clear_rows(self):
        """Remove all rows from the table."""
        for row in self.rows:
            row.destroy()
        self.rows = []
        self.checkboxes = []
    
    def get_selected_rows(self) -> list:
        """Get data from rows with checked checkboxes."""
        selected = []
        for cb, data in self.checkboxes:
            if cb.get():
                selected.append(data)
        return selected
    
    def get_all_rows(self) -> list:
        """Get all row data."""
        return [row.data for row in self.rows if hasattr(row, 'data')]


class DataTable(ctk.CTkFrame):
    """
    Enhanced data table with sorting and selection.
    Uses ttk.Treeview for better table functionality.
    """

    def __init__(self, master, columns: list, height: int = 200,
                 show_select: bool = False, **kwargs):
        super().__init__(master, **kwargs)

        self.columns = columns
        self.show_select = show_select
        self.data = []

        # Create style
        style = ttk.Style()
        style.theme_use('default')

        # Configure grid for this frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create Treeview with scrollbar
        self.tree = ttk.Treeview(
            self,
            columns=columns if not show_select else ['select'] + list(columns),
            show='headings',
            height=25  # Height in rows
        )

        # Configure columns
        if show_select:
            self.tree.heading('select', text='✓')
            self.tree.column('select', width=40, anchor='center')

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor='w')

        # Add scrollbar
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        # Place widgets using grid
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        # Enable mouse wheel scrolling - bind to all child widgets
        self._bind_scroll()

        # Auto-scroll on selection
        self.tree.bind('<<TreeviewSelect>>', self._on_select)

    def _bind_scroll(self):
        """Bind mouse wheel scrolling to tree and all its children."""
        # Bind to treeview
        self.tree.bind('<MouseWheel>', self._on_mousewheel)
        self.tree.bind('<Button-4>', self._on_mousewheel)
        self.tree.bind('<Button-5>', self._on_mousewheel)
        
        # Also bind to scrollbar
        self.scrollbar.bind('<MouseWheel>', self._on_mousewheel)
        self.scrollbar.bind('<Button-4>', self._on_mousewheel)
        self.scrollbar.bind('<Button-5>', self._on_mousewheel)

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        if event.num == 4:  # Linux scroll up
            self.tree.yview_scroll(-1, 'units')
        elif event.num == 5:  # Linux scroll down
            self.tree.yview_scroll(1, 'units')
        elif event.delta > 0:  # Windows/Mac scroll up
            self.tree.yview_scroll(-1, 'units')
        elif event.delta < 0:  # Windows/Mac scroll down
            self.tree.yview_scroll(1, 'units')

    def _on_select(self, event):
        """Auto-scroll to selected row."""
        selection = self.tree.selection()
        if selection:
            self.tree.see(selection[0])
    
    def add_row(self, values: list, selected: bool = False):
        """Add a row to the table."""
        if self.show_select:
            row_values = ['✓' if selected else ''] + list(values)
        else:
            row_values = list(values)
        
        self.tree.insert('', 'end', values=row_values)
        self.data.append(values)
    
    def clear(self):
        """Clear all rows."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.data = []
    
    def get_selected_data(self) -> list:
        """Get data from selected rows."""
        selected = []
        for item in self.tree.selection():
            values = self.tree.item(item)['values']
            if self.show_select:
                values = values[1:]  # Skip checkbox column
            selected.append(values)
        return selected
    
    def bind_select(self, callback):
        """Bind selection change event."""
        self.tree.bind('<<TreeviewSelect>>', callback)
