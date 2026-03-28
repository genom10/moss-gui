"""
MOSS (Measure Of Software Similarity) runner utility.
"""
import subprocess
import os
from pathlib import Path


class MossRunner:
    """Wrapper for running MOSS plagiarism detection."""
    
    SUPPORTED_LANGUAGES = [
        "c", "cc", "java", "ml", "pascal", "ada", "lisp", "scheme",
        "haskell", "fortran", "ascii", "vhdl", "perl", "matlab",
        "python", "mips", "prolog", "spice", "vb", "csharp",
        "modula2", "a8086", "javascript", "plsql", "verilog"
    ]
    
    def __init__(self, user_id: str, moss_script_path: str = None):
        """
        Initialize MOSS runner.
        
        Args:
            user_id: MOSS user ID
            moss_script_path: Path to moss perl script (default: app/scripts/moss)
        """
        self.user_id = user_id
        if moss_script_path is None:
            script_dir = Path(__file__).parent.parent / "scripts"
            moss_script_path = script_dir / "moss"
        self.moss_script = str(moss_script_path)
    
    def run_moss(self, 
                 files: list,
                 language: str = "cc",
                 max_matches: int = 10,
                 comment: str = "",
                 base_file: str = None,
                 directory_mode: bool = False) -> tuple:
        """
        Run MOSS plagiarism detection.
        
        Args:
            files: List of file paths to check
            language: Programming language code
            max_matches: Maximum matches threshold (-m option)
            comment: Comment string for report (-c option)
            base_file: Optional base file path (-b option)
            directory_mode: Enable directory mode (-d option)
        
        Returns:
            (success: bool, message: str, result_url: str)
        """
        if not files:
            return False, "No files to check", ""
        
        if language not in self.SUPPORTED_LANGUAGES:
            return False, f"Unsupported language: {language}", ""
        
        # Verify moss script exists
        if not os.path.exists(self.moss_script):
            return False, f"MOSS script not found: {self.moss_script}", ""
        
        # Build command
        cmd = [
            "perl", self.moss_script,
            "-u", self.user_id,  # Pass user ID
            "-l", language,
            "-m", str(max_matches),
        ]
        
        if directory_mode:
            cmd.append("-d")
        
        if base_file and os.path.exists(base_file):
            cmd.extend(["-b", base_file])
        
        if comment:
            cmd.extend(["-c", comment])
        
        # Add files
        cmd.extend(files)
        
        try:
            # Run MOSS
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            output = result.stdout + result.stderr
            
            # Extract result URL from output
            result_url = ""
            for line in output.split('\n'):
                if 'http' in line and 'moss.stanford.edu' in line:
                    result_url = line.strip()
                    break
            
            if result.returncode == 0 and result_url:
                return True, "MOSS check completed", result_url
            elif result_url:
                return True, f"MOSS completed with warnings: {result.stderr}", result_url
            else:
                return False, f"MOSS error: {output}", ""
                
        except subprocess.TimeoutExpired:
            return False, "MOSS timed out", ""
        except Exception as e:
            return False, f"Error running MOSS: {str(e)}", ""
    
    def get_language_for_extension(self, extension: str) -> str:
        """Guess MOSS language from file extension."""
        ext_map = {
            '.c': 'c',
            '.cpp': 'cc',
            '.cc': 'cc',
            '.cxx': 'cc',
            '.h': 'c',
            '.hpp': 'cc',
            '.java': 'java',
            '.py': 'python',
            '.py3': 'python',
            '.js': 'javascript',
            '.ts': 'javascript',
            '.rb': 'perl',  # Closest available
            '.go': 'cc',    # Closest available
            '.rs': 'cc',    # Closest available
            '.cs': 'csharp',
            '.php': 'perl',  # Closest available
            '.swift': 'cc',  # Closest available
            '.kt': 'java',   # Closest available
            '.scala': 'java',  # Closest available
        }
        return ext_map.get(extension.lower(), 'cc')
