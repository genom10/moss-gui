"""
MOSS GUI Application - Main Entry Point

A simple GUI for managing student assignment submissions:
1. Download submissions from Codeforces
2. Manage student aliases (email to handle mapping)
3. Run MOSS plagiarism detection
"""
import customtkinter as ctk
import os
import sys

# Add project root and app directory to path for imports
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

app_dir = os.path.join(project_root, "app")
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

# Now import pages
from pages.download_page import DownloadPage
from pages.aliases_page import AliasesPage
from pages.grading_page import GradingPage
from pages.analysis_page import AnalysisPage


class MossGUIApp(ctk.CTk):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("MOSS Assignment Grading")
        self.geometry("1200x700")
        self.minsize(1000, 600)
        
        # Set appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Store page data
        self.page_data = {}

        # Create navigation
        self._create_navigation()

        # Create pages container
        self.pages_frame = ctk.CTkFrame(self)
        self.pages_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Initialize page references (lazy loading)
        self.download_page = None
        self.aliases_page = None
        self.grading_page = None
        self.analysis_page = None

        # Show download page by default (lazy load it)
        self.show_page("download")
    
    def _create_navigation(self):
        """Create top navigation bar."""
        nav_frame = ctk.CTkFrame(self, height=50)
        nav_frame.pack(fill="x", padx=10, pady=(10, 0))
        nav_frame.pack_propagate(False)
        
        # Title
        title = ctk.CTkLabel(
            nav_frame,
            text="🎓 MOSS Assignment Grading",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(side="left", padx=20, pady=10)
        
        # Navigation buttons
        btn_frame = ctk.CTkFrame(nav_frame, fg_color="transparent")
        btn_frame.pack(side="right", padx=20, pady=10)
        
        self.nav_buttons = {}
        
        self.nav_buttons["download"] = ctk.CTkButton(
            btn_frame,
            text="1. Download",
            command=lambda: self.show_page("download"),
            width=100
        )
        self.nav_buttons["download"].pack(side="left", padx=5)

        self.nav_buttons["aliases"] = ctk.CTkButton(
            btn_frame,
            text="2. Aliases",
            command=lambda: self.show_page("aliases"),
            width=100
        )
        self.nav_buttons["aliases"].pack(side="left", padx=5)

        self.nav_buttons["grading"] = ctk.CTkButton(
            btn_frame,
            text="3. Grading",
            command=lambda: self.show_page("grading"),
            width=100
        )
        self.nav_buttons["grading"].pack(side="left", padx=5)

        self.nav_buttons["analysis"] = ctk.CTkButton(
            btn_frame,
            text="4. Analysis",
            command=lambda: self.show_page("analysis"),
            width=100
        )
        self.nav_buttons["analysis"].pack(side="left", padx=5)
    
    def _get_page(self, page_name: str):
        """Lazy-load a page when first accessed."""
        if page_name == "download" and self.download_page is None:
            self.download_page = DownloadPage(
                self.pages_frame,
                on_next=self.go_to_aliases
            )
        elif page_name == "aliases" and self.aliases_page is None:
            self.aliases_page = AliasesPage(
                self.pages_frame,
                on_next=self.go_to_grading,
                on_back=self.go_to_download
            )
        elif page_name == "grading" and self.grading_page is None:
            self.grading_page = GradingPage(
                self.pages_frame,
                on_back=self.go_to_aliases
            )
        elif page_name == "analysis" and self.analysis_page is None:
            self.analysis_page = AnalysisPage(
                self.pages_frame,
                on_back=self.go_to_grading
            )
        return getattr(self, f"{page_name}_page")

    def show_page(self, page_name: str):
        """Show a specific page."""
        # Lazy-load the page if needed
        page = self._get_page(page_name)
        
        # Hide all existing pages
        for p in [self.download_page, self.aliases_page, self.grading_page, self.analysis_page]:
            if p is not None:
                p.pack_forget()

        # Show requested page
        page.pack(fill="both", expand=True)

    def go_to_download(self):
        """Navigate to download page."""
        self.show_page("download")
    
    def go_to_aliases(self):
        """Navigate to aliases page."""
        # Get data from download page
        download_data = self.download_page.get_data()
        self.page_data.update(download_data)
        
        # Pass info to grading page
        if download_data.get('assignment_num') and download_data.get('contest_id'):
            self.grading_page.set_assignment_info(
                download_data['assignment_num'],
                download_data['contest_id']
            )
        
        self.show_page("aliases")
    
    def go_to_grading(self):
        """Navigate to grading page."""
        self.show_page("grading")


def main():
    """Application entry point."""
    # Verify we're in the moss-gui directory
    if not os.path.exists("aliases") and not os.path.exists("Assignment1"):
        print("Please run this application from the moss-gui directory.")
        print("Usage: cd /path/to/moss-gui && python main.py")
        sys.exit(1)

    # Start application
    app = MossGUIApp()
    app.mainloop()


if __name__ == "__main__":
    main()
