import tempfile
import unittest
from pathlib import Path

from database import AttendanceDatabase


class AttendanceDatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database = AttendanceDatabase(Path(self.temp_dir.name) / "test.db")

    def tearDown(self):
        self.database.close()
        self.temp_dir.cleanup()

    def test_student_and_attendance_lifecycle(self):
        student_id = self.database.add_student("Avery Stone", "ST-001", "Year 10")
        self.assertEqual(len(self.database.students()), 1)
        self.database.save_attendance("2026-09-27", [(student_id, "Present", "On time")])
        self.assertEqual(self.database.summary(), {"Present": 1, "Absent": 0, "Late": 0, "Excused": 0, "Total": 1})
        record = self.database.records()[0]
        self.assertEqual(record.student_name, "Avery Stone")
        self.assertEqual(record.note, "On time")

    def test_saving_same_date_updates_existing_record(self):
        student_id = self.database.add_student("Avery Stone", "ST-001")
        self.database.save_attendance("2026-09-27", [(student_id, "Absent", "")])
        self.database.save_attendance("2026-09-27", [(student_id, "Late", "Bus delay")])
        self.assertEqual(self.database.summary()["Late"], 1)
        self.assertEqual(self.database.summary()["Absent"], 0)

    def test_duplicate_student_ids_are_rejected(self):
        self.database.add_student("Avery Stone", "ST-001")
        with self.assertRaises(ValueError):
            self.database.add_student("Jordan Reed", "ST-001")

    def test_student_stats_rate_ignores_excused(self):
        student_id = self.database.add_student("Avery Stone", "ST-001")
        self.database.save_attendance("2026-09-21", [(student_id, "Present", "")])
        self.database.save_attendance("2026-09-22", [(student_id, "Late", "")])
        self.database.save_attendance("2026-09-23", [(student_id, "Absent", "")])
        self.database.save_attendance("2026-09-24", [(student_id, "Excused", "")])
        stats = self.database.student_stats()[0]
        self.assertEqual((stats.present, stats.late, stats.absent, stats.excused), (1, 1, 1, 1))
        self.assertAlmostEqual(stats.rate, 200 / 3)

    def test_invalid_report_dates_are_rejected(self):
        with self.assertRaises(ValueError):
            self.database.records(start_date="27/09/2026")


if __name__ == "__main__":
    unittest.main()
