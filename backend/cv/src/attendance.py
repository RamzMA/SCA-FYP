import csv
import sqlite3
from datetime import datetime
from pathlib import Path
"""
Project path for root and csv and database files for attendance records
"""
project_root = Path(__file__).resolve().parents[1]
DB_PATH = project_root / "data" / "attendance.db"
CSV_PATH = project_root / "data" / "attendance.csv"

"""
Setup a connection and create attendance table if it doesn't exist.
Table contains student_number, student_name, lecture_date, and recorded_at timestamp with a unique constraint on student_number and lecture_date 
    to prevent duplicate records for the same student on the same date.
"""
def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    #Table schema for attendance records
    conn.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            student_number TEXT NOT NULL,
            student_name TEXT,
            lecture_date TEXT NOT NULL,
            recorded_at TEXT NOT NULL,
            UNIQUE(student_number, lecture_date)
        )
    ''')
    return conn

"""
Record attendance for a student by inserting their details into the database, 
if the record is new return True otherwise return False.
"""
def record_attendance(conn, student_number, student_name, lecture_date):
    cursor = conn.execute(
        "INSERT OR IGNORE INTO attendance VALUES (?, ?, ?, ?)",
        (student_number, student_name, lecture_date, datetime.now().isoformat(timespec='seconds')),
    )
    conn.commit()
    #row count is 1 if new record inserted otherwise ignored due to duplicate
    return cursor.rowcount == 1

"""
Export attendance records to a CSV file for lecture to use for reference on attendance.
Operates by fetching all records from the database, sorting them by date and student number, and writing them to a CSV file with headers.
"""
def export_to_csv(conn, csv_path):
    rows = conn.execute(
        "SELECT student_number, student_name, lecture_date FROM attendance"
    ).fetchall()

    dates = sorted({date for _, _, date in rows})
    students = {}
    for number, name, date in rows:
        entry = students.setdefault(number, {"name": name, "dates": set()})
        entry["dates"].add(date)

    with open(csv_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Student Number", "Student Name"] + dates)
        for number, entry in students.items():
            writer.writerow(
                [number, entry["name"]] + ['present' if date in entry["dates"] else '' for date in dates]
            )
    return csv_path


    

