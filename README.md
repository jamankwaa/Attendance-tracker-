# Attendance Tracker

A local desktop attendance tracker built with Python, Tkinter, and SQLite. It works offline and stores data in `attendance.db` beside the application.

## Run

```powershell
python app.py
```

## Test

```powershell
python -m unittest discover -s tests -v
```

## Features

- Add, edit, and archive students with IDs and groups.
- Mark Present, Absent, Late, or Excused attendance for any date.
- Add notes to individual attendance records.
- View dashboard totals and recent attendance history.
- Filter reports by date range and group.
- See each student's attendance rate (Present + Late; excused sessions not counted). Students below 75% are highlighted in red.
- Export filtered reports as CSV.

No third-party packages are required. Python 3.10+ is recommended.
