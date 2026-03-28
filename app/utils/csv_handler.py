"""
CSV handler utility for reading/writing aliases and submissions.
"""
import csv
import os
from pathlib import Path
from typing import Optional


class CSVHandler:
    """Handle CSV operations for aliases and submissions."""
    
    @staticmethod
    def load_aliases(csv_path: str) -> list:
        """
        Load aliases from CSV file.
        
        Expected format: name,surname,id,alias
        Returns list of dicts with keys: name, surname, id, alias, email
        """
        aliases = []
        
        if not os.path.exists(csv_path):
            return aliases
        
        try:
            with open(csv_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    aliases.append({
                        'name': row.get('name', ''),
                        'surname': row.get('surname', ''),
                        'id': row.get('id', ''),
                        'alias': row.get('alias', ''),
                        'email': row.get('email', '')
                    })
        except Exception as e:
            print(f"Error loading aliases: {e}")
        
        return aliases
    
    @staticmethod
    def save_aliases(csv_path: str, aliases: list) -> bool:
        """
        Save aliases to CSV file.
        
        Args:
            csv_path: Output file path
            aliases: List of dicts with keys: name, surname, id, alias, email
        """
        try:
            os.makedirs(os.path.dirname(csv_path) or '.', exist_ok=True)
            
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['name', 'surname', 'id', 'alias', 'email']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for alias in aliases:
                    writer.writerow({k: alias.get(k, '') for k in fieldnames})
            return True
        except Exception as e:
            print(f"Error saving aliases: {e}")
            return False
    
    @staticmethod
    def load_submissions(csv_path: str) -> list:
        """
        Load submissions from CSV file.
        
        Expected format: Handle,latest submission id,passedTestCount
        Returns list of dicts
        """
        submissions = []
        
        if not os.path.exists(csv_path):
            return submissions
        
        try:
            with open(csv_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    submissions.append({
                        'handle': row.get('Handle', ''),
                        'submission_id': row.get('latest submission id', ''),
                        'passed_test_count': row.get('passedTestCount', '')
                    })
        except Exception as e:
            print(f"Error loading submissions: {e}")
        
        return submissions
    
    @staticmethod
    def save_submissions(csv_path: str, submissions: list) -> bool:
        """Save submissions to CSV file."""
        try:
            os.makedirs(os.path.dirname(csv_path) or '.', exist_ok=True)
            
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['Handle', 'latest submission id', 'passedTestCount']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for sub in submissions:
                    writer.writerow({
                        'Handle': sub.get('handle', ''),
                        'latest submission id': sub.get('submission_id', ''),
                        'passedTestCount': sub.get('passed_test_count', '')
                    })
            return True
        except Exception as e:
            print(f"Error saving submissions: {e}")
            return False
    
    @staticmethod
    def load_students(csv_path: str) -> list:
        """
        Load student list from CSV.
        
        Expected: name,surname,id,email or similar format
        """
        students = []
        
        if not os.path.exists(csv_path):
            return students
        
        try:
            with open(csv_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    students.append(dict(row))
        except Exception as e:
            print(f"Error loading students: {e}")
        
        return students
    
    @staticmethod
    def export_aliases_with_handles(aliases: list, output_path: str) -> bool:
        """
        Export aliases table with email:handle mapping.
        
        Args:
            aliases: List of alias dicts
            output_path: Output CSV path
        """
        try:
            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['email', 'handle', 'name', 'surname']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for alias in aliases:
                    if alias.get('email') and alias.get('alias'):
                        writer.writerow({
                            'email': alias['email'],
                            'handle': alias['alias'],
                            'name': alias.get('name', ''),
                            'surname': alias.get('surname', '')
                        })
            return True
        except Exception as e:
            print(f"Error exporting aliases: {e}")
            return False
