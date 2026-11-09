
from datetime import date
from pathlib import Path
import cv2
from attendance import CSV_PATH, get_connection, record_attendance, export_to_csv
from ocr import read_students

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VIDEO = PROJECT_ROOT / "data" / "raw" / "test_video.mp4"

#Frames less sharp than this are too blurry for OCR to read a card, so they are skipped to save time
MIN_SHARPNESS = 25

"""
Go through a video and yield the sharpest frame from each group of frames, as a moving camera leaves many frames too blurry to read.
"""
def sharpest_frames(capture, frame_interval):
    best_frame = None
    best_sharpness = -1.0
    frame_count = 0

    while True:
        success, frame = capture.read()
        if not success:
            break

        frame_count += 1
        #Variance of the Laplacian measures edge strength, which drops as an image gets blurrier
        sharpness = cv2.Laplacian(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()
        if sharpness > best_sharpness:
            best_frame, best_sharpness = frame, sharpness

        if frame_count % frame_interval == 0:
            yield best_frame, best_sharpness
            best_frame, best_sharpness = None, -1.0

    if best_frame is not None:
        yield best_frame, best_sharpness

"""
Process a video file to detect student attendance uploads.
The function takes the sharpest frame from each group of frames and reads any student numbers and names in it using OCR.
Each student is usually seen in several frames, so the most confident name is kept and attendance is only recorded once the whole video has been read.
It also generates a summary of the processing results.
"""
def process_video(video_path, lecture_date, frame_interval=10):
    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        raise FileNotFoundError(f"Could not open video: {video_path}")

    summary = {
        "frames_processed": 0,
        "frames_too_blurry": 0,
        "frames_without_student": 0,
        "attendance_recorded": [],
        "duplicate_records": 0,
    }

    #Best name found so far for each student number, stored as {number: (name, confidence)}
    students = {}

    for frame, sharpness in sharpest_frames(capture, frame_interval):
        if sharpness < MIN_SHARPNESS:
            summary["frames_too_blurry"] += 1
            continue

        summary["frames_processed"] += 1
        found = read_students(frame)
        if not found:
            summary["frames_without_student"] += 1

        for number, name, confidence in found:
            if number not in students or confidence > students[number][1]:
                students[number] = (name, confidence)

    capture.release()

    #Setup database connection for attendance records separately to ensure proper closure after processing
    conn = get_connection()
    for number, (name, _) in students.items():
        if record_attendance(conn, number, name, lecture_date):
            summary["attendance_recorded"].append({"student_number": number, "student_name": name})
        else:
            summary["duplicate_records"] += 1

    export_to_csv(conn, CSV_PATH)
    conn.close()
    return summary

def main():
    result = process_video(DEFAULT_VIDEO, date.today().isoformat())
    print(f'Summary: {result}')

if __name__ == "__main__":
    main()
