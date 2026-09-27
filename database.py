from __future__ import annotations

import csv
import sqlite3
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable


DEFAULT_PATH = Path(__file__).resolve().parent / "attendance.db"


def validate_date(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value.strip()).isoformat()
    except ValueError as exc:
        raise ValueError(f"'{value}' is not a valid date. Use YYYY-MM-DD.") from exc


@dataclass(frozen=True)
class StudentStats:
    student_code: str
    student_name: str
    group_name: str
    present: int
    late: int
    absent: int
    excused: int

    @property
    def total(self) -> int:
        return self.present + self.late + self.absent + self.excused

    @property
    def rate(self) -> float:
        """Share of counted sessions attended (Present or Late); excused sessions are not counted."""
        counted = self.total - self.excused
        return (self.present + self.late) / counted * 100 if counted else 0.0


@dataclass(frozen=True)
class Student:
    id: int
    name: str
    student_id: str
    group_name: str
    active: bool = True


@dataclass(frozen=True)
class AttendanceRecord:
    student_id: int
    student_name: str
    student_code: str
    group_name: str
    attendance_date: str
    status: str
    note: str


class AttendanceDatabase:
    STATUSES = ("Present", "Absent", "Late", "Excused")

    def __init__(self, path: str | Path = DEFAULT_PATH) -> None:
        self.path = Path(path)
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self._create_schema()

    def close(self) -> None:
        self.connection.close()

    def _create_schema(self) -> None:
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                student_id TEXT NOT NULL UNIQUE,
                group_name TEXT NOT NULL DEFAULT '',
                active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
                attendance_date TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('Present', 'Absent', 'Late', 'Excused')),
                note TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(student_id, attendance_date)
            );
            """
        )
        self.connection.commit()

    def add_student(self, name: str, student_code: str, group_name: str = "") -> int:
        name = name.strip()
        student_code = student_code.strip()
        group_name = group_name.strip()
        if not name or not student_code:
            raise ValueError("Name and student ID are required")
        try:
            cursor = self.connection.execute(
                "INSERT INTO students(name, student_id, group_name) VALUES (?, ?, ?)",
                (name, student_code, group_name),
            )
            self.connection.commit()
        except sqlite3.IntegrityError as exc:
            raise ValueError("That student ID already exists") from exc
        return int(cursor.lastrowid)

    def update_student(self, student_database_id: int, name: str, student_code: str, group_name: str) -> None:
        name = name.strip()
        student_code = student_code.strip()
        group_name = group_name.strip()
        if not name or not student_code:
            raise ValueError("Name and student ID are required")
        try:
            self.connection.execute(
                "UPDATE students SET name = ?, student_id = ?, group_name = ? WHERE id = ?",
                (name, student_code, group_name, student_database_id),
            )
            self.connection.commit()
        except sqlite3.IntegrityError as exc:
            raise ValueError("That student ID already exists") from exc

    def deactivate_student(self, student_database_id: int) -> None:
        self.connection.execute("UPDATE students SET active = 0 WHERE id = ?", (student_database_id,))
        self.connection.commit()

    def students(self, include_inactive: bool = False) -> list[Student]:
        query = "SELECT id, name, student_id, group_name, active FROM students"
        if not include_inactive:
            query += " WHERE active = 1"
        query += " ORDER BY name COLLATE NOCASE"
        return [Student(row["id"], row["name"], row["student_id"], row["group_name"], bool(row["active"])) for row in self.connection.execute(query)]

    def get_student(self, student_database_id: int) -> Student | None:
        row = self.connection.execute(
            "SELECT id, name, student_id, group_name, active FROM students WHERE id = ?",
            (student_database_id,),
        ).fetchone()
        if row is None:
            return None
        return Student(row["id"], row["name"], row["student_id"], row["group_name"], bool(row["active"]))

    def save_attendance(self, attendance_date: str, records: Iterable[tuple[int, str, str]]) -> None:
        try:
            date.fromisoformat(attendance_date)
        except ValueError as exc:
            raise ValueError("Date must use YYYY-MM-DD") from exc
        rows = list(records)
        if any(status not in self.STATUSES for _, status, _ in rows):
            raise ValueError("Invalid attendance status")
        self.connection.executemany(
            """
            INSERT INTO attendance(student_id, attendance_date, status, note)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(student_id, attendance_date) DO UPDATE SET
                status = excluded.status,
                note = excluded.note,
                updated_at = CURRENT_TIMESTAMP
            """,
            [(student_id, attendance_date, status, note.strip()) for student_id, status, note in rows],
        )
        self.connection.commit()

    def attendance_for_date(self, attendance_date: str) -> dict[int, tuple[str, str]]:
        rows = self.connection.execute(
            "SELECT student_id, status, note FROM attendance WHERE attendance_date = ?",
            (attendance_date,),
        )
        return {row["student_id"]: (row["status"], row["note"]) for row in rows}

    def records(self, start_date: str | None = None, end_date: str | None = None, group_name: str | None = None) -> list[AttendanceRecord]:
        start_date, end_date = validate_date(start_date), validate_date(end_date)
        clauses = []
        parameters: list[str] = []
        if start_date:
            clauses.append("a.attendance_date >= ?")
            parameters.append(start_date)
        if end_date:
            clauses.append("a.attendance_date <= ?")
            parameters.append(end_date)
        if group_name:
            clauses.append("s.group_name = ?")
            parameters.append(group_name)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        rows = self.connection.execute(
            f"""
            SELECT s.id, s.name, s.student_id, s.group_name, a.attendance_date, a.status, a.note
            FROM attendance a JOIN students s ON s.id = a.student_id
            {where}
            ORDER BY a.attendance_date DESC, s.name COLLATE NOCASE
            """,
            parameters,
        )
        return [AttendanceRecord(row["id"], row["name"], row["student_id"], row["group_name"], row["attendance_date"], row["status"], row["note"]) for row in rows]

    def summary(self, start_date: str | None = None, end_date: str | None = None) -> dict[str, int]:
        start_date, end_date = validate_date(start_date), validate_date(end_date)
        clauses = []
        parameters: list[str] = []
        if start_date:
            clauses.append("attendance_date >= ?")
            parameters.append(start_date)
        if end_date:
            clauses.append("attendance_date <= ?")
            parameters.append(end_date)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        result = {status: 0 for status in self.STATUSES}
        for row in self.connection.execute(f"SELECT status, COUNT(*) AS count FROM attendance {where} GROUP BY status", parameters):
            result[row["status"]] = row["count"]
        result["Total"] = sum(result.values())
        return result

    def student_stats(self, start_date: str | None = None, end_date: str | None = None, group_name: str | None = None) -> list[StudentStats]:
        stats: dict[str, dict] = {}
        for record in self.records(start_date, end_date, group_name):
            entry = stats.setdefault(record.student_code, {"name": record.student_name, "group": record.group_name, **{status: 0 for status in self.STATUSES}})
            entry[record.status] += 1
        return sorted(
            (StudentStats(code, e["name"], e["group"], e["Present"], e["Late"], e["Absent"], e["Excused"]) for code, e in stats.items()),
            key=lambda item: item.student_name.lower(),
        )

    def export_csv(self, destination: str | Path, start_date: str | None = None, end_date: str | None = None, group_name: str | None = None) -> int:
        rows = self.records(start_date, end_date, group_name)
        with Path(destination).open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Student ID", "Student", "Group", "Status", "Note"])
            writer.writerows((row.attendance_date, row.student_code, row.student_name, row.group_name, row.status, row.note) for row in rows)
        return len(rows)
