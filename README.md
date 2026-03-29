# MOSS Assignment Grading GUI

A simple GUI application for managing student assignment submissions and plagiarism detection.

## Features

1. **Download Submissions** - Fetch latest submissions from Codeforces contest
2. **Manage Aliases** - Map student emails to Codeforces handles
3. **Run MOSS** - Check submissions for plagiarism using MOSS
4. **Analysis** - Visualize MOSS results as an interactive plagiarism network graph

## Installation

### Using uv (recommended)

**1. Install tkinter (system dependency):**

tkinter is required for the GUI but is not installed by uv/pip. Install it first:

- **Ubuntu/Debian:** `sudo apt-get install python3-tk`
- **Fedora:** `sudo dnf install python3-tkinter`
- **Arch Linux:** `sudo pacman -S tk`
- **Windows:** Included with Python (ensure "tcl/tk and IDLE" is checked during install)
- **macOS:** `brew install python-tk`

**2. Install uv and dependencies:**

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Navigate to project directory and install dependencies
cd moss-gui
uv sync
```

After syncing, you can run the app in several ways:

```bash
# Option 1: Run directly with uv (from project root)
uv run python main.py

# Option 2: Activate the virtual environment
source .venv/bin/activate
python main.py
```

### Using pip (alternative)

```bash
pip install -r requirements.txt
python main.py
```

## Page 1: Download Submissions

- Enter Codeforces Contest ID
- Enter Assignment Number
- Provide Codeforces API Key and Secret
- Click "Download" to fetch submissions list
- **Note:** Source code files must be placed manually in `Assignment{N}/{contestId}/` folder
- View submissions table with status indicator

## Page 2: Aliases

- Import/export aliases from CSV
- Extract handles from HTML files (from LMS exports)
- Manually add/edit email:handle mappings
- Save to `students_aliases.csv`

## Page 3: Grading (MOSS)

- Enter MOSS User ID
- Select programming language
- Set max matches threshold
- Optionally provide base file (skeleton code)
- Select submission files to check
- Run MOSS and view results URL

## Page 4: Analysis (Plagiarism Graph)

- Enter MOSS report URL (or import from Grading page)
- Visualize plagiarism matches as a force-directed network graph
- Nodes represent students, edges show plagiarism matches
- Edge thickness and color indicate match percentage (green → yellow → red)
- **Field caching:** MOSS URL is cached to `moss_result.txt` for quick re-import
- Adjust cutoff slider to filter low-percentage matches
- Scroll to zoom, drag to pan the graph
- Reset view button to return to default zoom/pan

## Getting Codeforces API Credentials

1. Visit https://codeforces.com/settings/api
2. Generate a new API key
3. Copy the key and secret to the Download page

## Getting MOSS User ID

1. Register at http://moss.stanford.edu/
2. Your user ID will be provided via email
3. Enter it in the Grading page

## Project Structure

```
moss-gui/
├── main.py                 # Application entry point (project root)
├── requirements.txt        # Python dependencies (pip)
├── pyproject.toml          # Project configuration (uv)
├── README.md               # This file
├── app/
│   ├── pages/
│   │   ├── download_page.py    # Page 1: Download submissions
│   │   ├── aliases_page.py     # Page 2: Manage aliases
│   │   ├── grading_page.py     # Page 3: MOSS grading
│   │   └── analysis_page.py    # Page 4: Plagiarism graph visualization
│   ├── components/
│   │   ├── data_table.py       # Reusable table component
│   │   └── form_inputs.py      # Reusable form components
│   ├── utils/
│   │   ├── codeforces_api.py   # Codeforces API wrapper
│   │   ├── moss_runner.py      # MOSS execution wrapper
│   │   └── csv_handler.py      # CSV import/export
│   └── scripts/
│       ├── pull.py             # Sanitized pull script
│       ├── getLastSubmission.py # Sanitized parsing script
│       ├── pullSubmissions.py  # Sanitized copy script
│       └── moss                # MOSS perl script (modified)
└── aliases/                # LMS HTML exports for alias extraction
```
