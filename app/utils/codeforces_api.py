"""
Codeforces API utility module.
Handles fetching and parsing contest submissions.
"""
import json
import csv
import os
import re
from pathlib import Path
from scripts import pull, getLastSubmission, pullSubmissions


class CodeforcesAPI:
    """Wrapper for Codeforces API operations."""

    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret

    def fetch_contest(self, contest_id: str, assignment_num: int) -> dict | None:
        """Fetch contest data from Codeforces API."""
        return pull.fetch_contest_data(
            contest_id, self.api_key, self.api_secret, assignment_num
        )

    def parse_submissions(self, assignment_num: int, contest_id: str) -> list:
        """Parse contest JSON and extract latest submissions."""
        json_path = f"Assignment{assignment_num}/{contest_id}.json"
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"Contest JSON not found: {json_path}")
        return getLastSubmission.parse_submissions(json_path, assignment_num)

    def copy_submissions(self, assignment_num: int, contest_id: str) -> list:
        """Copy and rename submissions to latest_submissions folder."""
        return pullSubmissions.copy_latest_submissions(assignment_num, contest_id)

    def check_source_files_exist(self, assignment_num: int, contest_id: str) -> tuple:
        """
        Check if source files exist in the contest folder.
        Returns: (exists: bool, count: int, message: str)
        """
        input_folder = f"Assignment{assignment_num}/{contest_id}"
        
        if not os.path.exists(input_folder):
            return False, 0, f"Folder not found: {input_folder}"
        
        # Count source files
        source_files = [f for f in os.listdir(input_folder) 
                       if os.path.isfile(os.path.join(input_folder, f))]
        
        if len(source_files) > 0:
            return True, len(source_files), f"Found {len(source_files)} source files"
        else:
            return False, 0, f"Folder empty: {input_folder}"

    def download_all(self, contest_id: str, assignment_num: int) -> tuple:
        """
        Complete download workflow.
        Returns: (success: bool, message: str, submissions: list)
        """
        try:
            # Step 1: Fetch from API
            print(f"Fetching contest {contest_id}...")
            data = self.fetch_contest(contest_id, assignment_num)

            if not data:
                return False, "Failed to fetch contest data", []

            if 'status' not in data or data['status'] != 'OK':
                return False, f"API error: {data.get('comment', 'Unknown error')}", []

            submissions_count = len(data.get('result', []))
            if submissions_count == 0:
                return False, "No submissions found in contest", []

            # Step 2: Parse to get latest submissions
            print("Parsing submissions...")
            submissions = self.parse_submissions(assignment_num, contest_id)

            # Step 3: Check if source files exist
            input_folder = f"Assignment{assignment_num}/{contest_id}"
            files_exist, file_count, files_msg = self.check_source_files_exist(
                assignment_num, contest_id
            )

            # Step 4: Copy files to latest_submissions folder
            if files_exist:
                print("Copying submission files...")
                self.copy_submissions(assignment_num, contest_id)
                msg = f"Downloaded {len(submissions)} submissions ({file_count} source files found)"
            else:
                msg = (f"Downloaded {len(submissions)} submissions - "
                      f"Source files not found. Please place them in: {input_folder}")

            return True, msg, submissions

        except Exception as e:
            return False, f"Error: {str(e)}", []


def parse_html_handle(html_content: str) -> str | None:
    """Extract Codeforces handle from HTML content."""
    # First try to find Codeforces profile links
    link_patterns = [
        r'href="https?://codeforces\.com/profile/([^"]+)"',
        r'profile/([^"]+)"',
    ]
    
    for pattern in link_patterns:
        match = re.search(pattern, html_content)
        if match:
            handle = match.group(1)
            handle = handle.replace('<p>', '').replace('</p>', '').strip()
            if handle and len(handle) > 1:
                return handle
    
    # Try to extract handle from <p> tag content
    # Pattern: <p>handle</p> or <p>CF-Хэндл: handle</p>
    p_match = re.search(r'<p>([^<]+)</p>', html_content, re.IGNORECASE)
    if p_match:
        text = p_match.group(1).strip()
        # Remove common prefixes like "CF-Хэндл:" or "CF-Handle:"
        text = re.sub(r'^CF[-\s]*(?:Хэндл|Handle)[:\s]*', '', text, flags=re.IGNORECASE)
        text = text.strip()
        # Validate it looks like a Codeforces handle (alphanumeric, underscores, hyphens)
        if text and re.match(r'^[a-zA-Z0-9_-]+$', text) and len(text) > 1:
            return text
    
    return None


def load_aliases_from_html(aliases_folder: str) -> dict:
    """
    Load aliases from HTML files in aliases folder.
    Returns: {student_name: handle}
    """
    aliases = {}
    aliases_path = Path(aliases_folder)
    
    if not aliases_path.exists():
        return aliases
    
    for html_file in aliases_path.glob("*.html"):
        if html_file.name.startswith('.'):
            continue
            
        try:
            content = html_file.read_text(encoding='utf-8')
            handle = parse_html_handle(content)
            
            # Extract student name from filename
            # Format: "Name Surname_ID_assignsubmission..."
            name_part = html_file.stem.split('_assignsubmission')[0]
            name_parts = name_part.rsplit('_', 1)
            if len(name_parts) == 2:
                student_name = name_parts[0]
                student_id = name_parts[1]
                if handle:
                    aliases[student_name] = {
                        'handle': handle,
                        'id': student_id,
                        'source': 'HTML'
                    }
        except Exception as e:
            print(f"Error parsing {html_file.name}: {e}")
    
    return aliases
