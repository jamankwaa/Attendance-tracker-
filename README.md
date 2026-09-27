# Attendance Tracker

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)

A simple offline desktop app built with Python, Tkinter, and SQLite for tracking attendance. Teachers and group leaders can manage students, take daily attendance, check each student's attendance rate, and export reports to CSV. It needs no internet connection, accounts, or extra packages.

---

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [How Attendance Rate Is Calculated](#how-attendance-rate-is-calculated)
- [Project Structure](#project-structure)
- [Running Tests](#running-tests)
- [Data Storage](#data-storage)
- [License](#license)

---

## Features

| Area | What you can do |
| --- | --- |
| **Dashboard** | See today's Present, Late, Absent, and Excused totals, plus recent activity |
| **Take Attendance** | Pick a date, set each student's status, add notes, or mark everyone present in one click |
| **Students** | Add, edit, and archive students with a unique ID and an optional group or class |
| **Reports** | Filter by date range and group, see each student's attendance rate, and export to CSV |

- Four attendance statuses: **Present**, **Absent**, **Late**, and **Excused**
- Saving attendance again for the same date updates it instead of duplicating it
- Archived students keep their attendance history
- Students below **75%** attendance are highlighted in red
- Dates are checked, and invalid input shows a clear error message

## Requirements

- **Python 3.10 or newer**
- Tkinter, which comes with the standard Python installers for Windows and macOS. On Linux, install it with `sudo apt install python3-tk`.

No third-party packages are required.

## Installation

```bash
git clone https://github.com/jamankwaa/Attendance-tracker-.git
cd Attendance-tracker-
```

## Usage

Start the application:

```bash
python app.py
```

A typical workflow:

1. **Add students** in the **Students** tab. Each student needs a name and a unique student ID. The group is optional.
2. **Take attendance** in the **Take Attendance** tab. Choose a date in `YYYY-MM-DD` format, set each student's status, and click **Save attendance**.
3. **Review progress** on the **Dashboard** for today's summary.
4. **Generate reports** in the **Reports** tab. Filter by date range or group, review attendance rates, and click **Export CSV** to share or archive the results.

## How Attendance Rate Is Calculated

```
Attendance rate = (Present + Late) / (Total sessions − Excused) × 100
```

Excused sessions don't count toward the rate, so an approved absence doesn't lower a student's percentage.

## Project Structure

```
Attendance-tracker-/
├── app.py                  # Tkinter user interface
├── database.py             # SQLite data layer, validation, reporting, and CSV export
├── tests/
│   └── test_database.py    # Unit tests for the data layer
├── LICENSE
└── README.md
```

## Running Tests

```bash
python -m unittest discover -s tests -v
```

## Data Storage

All data is stored locally in `attendance.db`, a SQLite file created automatically in the application folder on first run. To back up your data, copy this file. To start fresh, delete it. The file is listed in `.gitignore`, so student records are never committed to version control.

## License

This project is licensed under the [MIT License](LICENSE).
