# Assignment Grading GUI - Task Specification

## Overview

A simple GUI application to automate the student assignment grading workflow:
1. Download submissions from Codeforces
2. Map student emails to Codeforces handles (aliases)
3. Run MOSS plagiarism detection

---

## Page 1: Download Submissions

**Purpose:** Fetch latest submissions from Codeforces contest

### Inputs

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| Contest ID | Text | Codeforces contest ID | `656462` |
| Assignment Number | Number | Assignment identifier for folder organization | `3` |
| Language | Dropdown | Submission language filter | `ru`, `en` |
| API Key | Text (password) | Codeforces API key | `0a73f034...` |
| API Secret | Text (password) | Codeforces API secret | `fcd9f9be...` |

### Data Table (Scrollable)

| Handle | Submission ID | Passed Tests | Verdict | Status |
|--------|---------------|--------------|---------|--------|
| `mishel2007` | `341624823` | `10/10` | `OK` | ✅ Downloaded |
| `gustokashin` | `341624800` | `8/10` | `PARTIAL` | ✅ Downloaded |
| `student3` | `-` | `-` | `-` | ⚠️ No submission |

### Actions

- **Download** - Fetch all submissions from Codeforces API
- **Open Folder** - Open `Assignment{N}/{contestId}/` in file explorer
- **Proceed to Aliases** - Navigate to next page

### Output Files

```
Assignment{N}/
├── {contestId}.json          # Raw API response
├── submissions.csv           # Handle, submission_id, passedTestCount
└── {contestId}/              # Downloaded source files
    ├── 341624823.ru
    ├── 341624800.ru
    └── ...
```

---

## Page 2: Aliases Management

**Purpose:** Map university emails to Codeforces handles for MOSS

### Inputs

| Field | Type | Description |
|-------|------|-------------|
| Import CSV | File Upload | Load existing aliases from CSV |
| Export CSV | Button | Save current aliases to file |

### Data Table (Scrollable, Editable)

| Student Name | Student ID | University Email | Codeforces Handle | Source |
|--------------|------------|------------------|-------------------|--------|
| `Mikhail Veber` | `490508` | `m.veber@innopolis.university` | `mishaveber2007` | Manual |
| `Maksim Gustokashin` | `490541` | `m.gustokashin@...` | `gustokashinmm` | HTML |
| `...` | `...` | `...` | `...` | `...` |

### Features

- **Add Row** - Insert new email:handle mapping
- **Remove Row** - Delete selected mapping
- **Extract from HTML** - Parse handles from `aliases/*.html` files (existing workflow)
- **Auto-fill Students** - Load student list from `students_aliases.csv`

### Actions

- **Save Aliases** - Write to `students_aliases.csv`
- **Proceed to Grading** - Navigate to next page

### Data Source

Existing aliases stored in:
- `students_aliases.csv` - Primary storage
- `aliases/*.html` - Raw HTML exports from LMS

---

## Page 3: Grading (MOSS)

**Purpose:** Run plagiarism detection on downloaded submissions

### Inputs

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| MOSS User ID | Text | MOSS account identifier | `144593585` |
| Language | Dropdown | Programming language for MOSS | `c`, `cc`, `python`, `java` |
| Max Matches | Number | Passage match threshold (`-m`) | `10` |
| Comment | Text | Report identifier (`-c`) | `Assignment 3 2025` |
| Base File | File Upload | Instructor skeleton code (optional) | `skeleton.cc` |

### Data Table (Scrollable)

| File | Student | Handle | Size | Status |
|------|---------|--------|------|--------|
| `Veber_Mikhail.cpp` | `Mikhail Veber` | `mishaveber2007` | `2.4 KB` | ✅ Ready |
| `Gustokashin_Maksim.cpp` | `Maksim Gustokashin` | `gustokashinmm` | `1.8 KB` | ✅ Ready |
| `Ananin_Oleg.cpp` | `Oleg Ananin` | `-` | `0 KB` | ⚠️ Missing handle |

### Actions

- **Select Files** - Choose submission files from `Assignment{N}/latest_submissions/`
- **Run MOSS** - Execute plagiarism check with provided credentials
- **View Report** - Open MOSS results URL in browser
- **Export Results** - Save MOSS output to file

### MOSS Command Generated

```bash
./moss -l cc -m 10 -c "Assignment 3 2025" -b skeleton.cc \
  Veber_Mikhail.cpp Gustokashin_Maksim.cpp ...
```

### Output

- MOSS report URL (e.g., `http://moss.stanford.edu/results/...`)
- Optional: Save report HTML to `Assignment{N}/moss_report.html`

---

## Technical Requirements

### Framework Options

| Framework | Pros | Cons |
|-----------|------|------|
| **Tkinter** | Built-in, simple | Dated UI |
| **PyQt6** | Modern, feature-rich | Larger dependency |
| **CustomTkinter** | Modern look, easy | External package |

**Recommended:** CustomTkinter (modern UI, minimal learning curve)

### Project Structure

```
moss-gui/
├── main.py                 # Application entry point
├── pages/
│   ├── download_page.py    # Page 1
│   ├── aliases_page.py     # Page 2
│   └── grading_page.py     # Page 3
├── components/
│   ├── data_table.py       # Reusable scrollable table
│   └── form_inputs.py      # Reusable form components
├── utils/
│   ├── codeforces_api.py   # API wrapper
│   ├── moss_runner.py      # MOSS execution
│   └── csv_handler.py      # CSV import/export
└── config.py               # Settings, paths
```

### Integration Points

| Existing Script | Functionality | Integration |
|-----------------|---------------|-------------|
| `pull.py` | Codeforces API fetch | Page 1 backend |
| `getLastSubmission.py` | Parse submissions | Page 1 backend |
| `pullSubmissions.py` | Rename/copy files | Page 1 → Page 2 |
| `moss` | Plagiarism detection | Page 3 backend |
| `students_aliases.csv` | Alias storage | Page 2 data source |

---

## User Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   DOWNLOAD      │────▶│    ALIASES      │────▶│    GRADING      │
│                 │     │                 │     │                 │
│ • Contest ID    │     │ • Email:Handle  │     │ • MOSS User ID  │
│ • Assignment #  │     │ • Edit table    │     │ • Language      │
│ • API Keys      │     │ • Import/Export │     │ • Run MOSS      │
│                 │     │                 │     │                 │
│ [Download]      │     │ [Save Aliases]  │     │ [Run MOSS]      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## Future Enhancements (Optional)

- [ ] Auto-detect language from file extensions
- [ ] Schedule automatic downloads
- [ ] Email reports to students
- [ ] Historical comparison (compare with previous assignments)
- [ ] Dark mode theme
