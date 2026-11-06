
import tempfile
from datetime import date
from pathlib import Path
import cv2
from detect_card import detect_card
from attendance import CSV_PATH, get_connection, record_attendance, export_to_csv
from ocr import extract_student_details

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VIDEO = PROJECT_ROOT / "data" / "raw" / "test_video.mp4"

"""
Process a video file to detect student attendance uploads. 
The function reads frames from the video at specified intervals, detects student cards, extracts student details using OCR, and records attendance in a database. 
It also generates a summary of the processing results.
"""
def process_video(video_path, lecture_date, frame_interval=30):
    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        raise FileNotFoundError(f"Could not open video: {video_path}")

    #Setup database connection for attendance records separately to ensure proper closure after processing
    conn = get_connection()

    summary = {
        "frames_processed": 0,
        "no_card_detected": 0,
        "unreadable_text": 0,
        "attendance_recorded": [],
        "duplicate_records": 0,
    }

    #Use a temporary directory to store cropped card images for OCR processing.
    with tempfile.TemporaryDirectory() as temp:
        crop_path = Path(temp) / "crop.jpg"
        frame_count = 0

        while True:
            success, frame = capture.read()
            if not success:
                break

            """
            Increment frame count and check if the current frame is at the specified interval for processing.
            If it is which it should be if modulus is 0, attempt to detect a card in the frame. 
            If a card is detected, save it to a temporary file and extract student details using OCR. 
            """
            frame_count += 1
            if (frame_count - 1) % frame_interval != 0:
                continue

            summary["frames_processed"] += 1
            card, _, _ = detect_card(frame)

            if card is None:
                summary["no_card_detected"] += 1
                continue

            cv2.imwrite(str(crop_path), card)
            number, name = extract_student_details(crop_path)

            if number is None:
                summary["unreadable_text"] += 1
                continue

            if record_attendance(conn, number, name, lecture_date):
                summary["attendance_recorded"].append({"student_number": number, "student_name": name})
            else:
                summary["duplicate_records"] += 1

    capture.release()
    export_to_csv(conn, CSV_PATH)
    conn.close()
    return summary

def main():
    result = process_video(DEFAULT_VIDEO, date.today().isoformat())
    print(f'Summary: {result}')

if __name__ == "__main__":
    main()
