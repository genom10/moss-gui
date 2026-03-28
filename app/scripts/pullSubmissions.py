"""
Sanitized version of pullSubmissions.py - Copies and renames submissions to student names.
"""
import csv
import os
import shutil
from glob import glob


def copy_latest_submissions(assignment_num, contest_id, output_folder=None):
    """
    Copy latest submissions and rename them by handle.
    
    Args:
        assignment_num: Assignment number
        contest_id: Codeforces contest ID
        output_folder: Optional custom output folder path
    
    Returns:
        list: List of copied file paths
    """
    csv_file = f"Assignment{assignment_num}/submissions.csv"
    input_folder = f"Assignment{assignment_num}/{contest_id}"
    
    if output_folder is None:
        output_folder = f"Assignment{assignment_num}/latest_submissions"
    
    os.makedirs(output_folder, exist_ok=True)
    
    # Read CSV
    submissions = []
    with open(csv_file, newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            handle = row["Handle"]
            submission_id = row["latest submission id"]
            submissions.append((handle, submission_id))
    
    copied_files = []
    
    for handle, submission_id in submissions:
        # Match any extension
        pattern = os.path.join(input_folder, f"{submission_id}.*")
        matches = glob(pattern)
        
        if not matches:
            print(f"[WARNING] File for submission {submission_id} not found.")
            continue
        
        source_path = matches[0]
        ext = os.path.splitext(source_path)[1]
        
        # Sanitize handle for filename
        safe_handle = "".join(c if c.isalnum() or c in '._-' else '_' for c in handle)
        dest_path = os.path.join(output_folder, f"{safe_handle}{ext}")
        
        shutil.copy2(source_path, dest_path)
        copied_files.append(dest_path)
        print(f"Copied {source_path} -> {dest_path}")
    
    print(f"\nAll available files copied to: {output_folder}")
    return copied_files


if __name__ == "__main__":
    print("Usage: Provide assignment number and contest ID")
    # copy_latest_submissions(1, "656462")
