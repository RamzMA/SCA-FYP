from pathlib import Path
import re

try:
    import easyocr
except ModuleNotFoundError as error:
    raise SystemExit(
        "EasyOCR is not installed for this Python interpreter. "
        "Run: python -m pip install easyocr"
    ) from error

PROJECT_ROOT = Path(__file__).resolve().parents[1]
IMAGE_PATH = PROJECT_ROOT / 'data' / 'processed' / "detected_card.jpg"

print("1. Starting script...")
print("2. Initializing EasyOCR Reader (this might download models if first time)...")

# Initialize reader with verbose=False to keep logs clean
reader = easyocr.Reader(['en'], gpu=False)

print("3. EasyOCR Reader initialized successfully!")

def extract_student_details(image_path):
    print(f"4. Reading image from: {image_path}")
    results = reader.readtext(str(image_path)) 
    print(f"5. OCR complete. Found {len(results)} text boxes.")
    
    student_number = None
    student_name = None
    number_box = None

    excluded_terms = {
        'BACHELOR', 'MASTER', 'PHD', 'SCIENCE', 'DEGREE', 'UNIVERSITY',
        'MAYNOOTH', 'DATE', 'BIRTH', 'VALID', 'UNTIL', 'STUDENT', 'CARD'
    }

    # 1. Find student number
    for box, text, confidence in results:
        cleaned = text.strip()
        print(f"   -> Detected: {cleaned} | confidence: {confidence:.2f}")

        if re.fullmatch(r"\d{8}", cleaned):
            student_number = cleaned
            number_box = box

    # 2. Find the name relative to the student number
    if number_box is not None:
        number_top = min(p[1] for p in number_box)
        number_bottom = max(p[1] for p in number_box)
        number_height = number_bottom - number_top

        candidates = []

        for box, text, confidence in results:
            cleaned = text.strip()
            words = cleaned.split()

            top = min(p[1] for p in box)
            left = min(p[0] for p in box)

            if top < number_top - (0.5 * number_height):
                continue

            if cleaned == student_number:
                continue

            if (
                cleaned.isupper()
                and cleaned.replace(" ", "").isalpha()
                and not set(words).intersection(excluded_terms)
                and confidence >= 0.4
            ):
                candidates.append((top, left, cleaned))

        if candidates:
            candidates.sort(key=lambda x: (round(x[0] / 20), x[1]))
            student_name = " ".join(candidate[2] for candidate in candidates)

    return student_number, student_name

def main():
    if not IMAGE_PATH.exists():
        raise FileNotFoundError(f"Could not load image: {IMAGE_PATH}")

    print("6. Extracting details...")
    student_number, student_name = extract_student_details(IMAGE_PATH)

    print("\nATTENDANCE RESULT:")
    print(f"Student number: {student_number}")
    print(f"Student name: {student_name}")

if __name__ == "__main__":
    main()