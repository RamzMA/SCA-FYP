from pathlib import Path
import re
import easyocr

PROJECT_ROOT = Path(__file__).resolve().parents[1]
IMAGE_PATH = PROJECT_ROOT / 'data' / 'processed' / "manual_card.jpg"

def extract_student_details(image_path):
    """
    Initialize and use EasyOCR to extract student number and name
    """
    reader = easyocr.Reader(['en'], gpu=False)
    result = reader.readtext(str(image_path)) 

    student_number = None
    student_name = None

    for box,text,confidence in result:
        cleaned = text.strip()

        print(f"Detected text: {cleaned} | confidence: {confidence:.2f}")

        if re.match(r'^\d{8}$', cleaned):
            student_number = cleaned
        elif (
            len(cleaned.split()) >= 2
            and cleaned.isupper()
            and cleaned.replace(" ", "").isalpha()
            and 'UNIVERSITY' not in cleaned
            and 'DEGREE' not in cleaned
        ):
            student_name = cleaned

    return student_number, student_name

def main():
    if not IMAGE_PATH.exists():
        raise FileNotFoundError(
            f"Could not load image: {IMAGE_PATH}"
        )

    student_number, student_name = extract_student_details(IMAGE_PATH)

    print("ATTENDENCE RESULT:")
    print(f"Student number: {student_number}")
    print(f"Student name: {student_name}")

if __name__ == "__main__":
    main()

