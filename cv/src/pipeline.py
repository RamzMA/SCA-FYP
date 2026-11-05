from datetime import date
from pathlib import Path
import cv2
from detect_card import detect_card
from attendance import get_connection, record_attendance, export_to_csv
from ocr import extract_student_details

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FRAME_DIR = PROJECT_ROOT / "data" / "processed" / "frames"
CROP_PATH = PROJECT_ROOT / "data" / "processed" / "current_crop.jpg"

def main():
    lecture_date = date.today().isoformat()
    conn = get_connection()

    for path in sorted(FRAME_DIR.glob("frame_*.jpg")):
        image = cv2.imread(str(path))
        card, _, _ = detect_card(image)

        if card is None:
            print("No ID card detected in frame:", path.name)
            continue

        cv2.imwrite(str(CROP_PATH), card)
        number, name = extract_student_details(CROP_PATH)

        if number is None:
            print("No student number detected in frame:", path.name)
            continue

        is_new_record = record_attendance(conn, number, name, lecture_date)
        status = "New record" if is_new_record else "Duplicate record"
        print(f"Summary: {path.name} - {number}: {name} / {status} -> {lecture_date}")

    csv_path = export_to_csv(conn)
    print(f"Attendance records saved to: {csv_path}")

if __name__ == "__main__":
    main()

