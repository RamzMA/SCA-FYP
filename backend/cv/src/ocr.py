from pathlib import Path
import re

import cv2
import numpy as np

"""
Encountered numerous issues with EasyOCR and loading ocr.py so included a try-except block to provide a clear error message if EasyOCR is not installed and functional
"""
try:
    import easyocr
except ModuleNotFoundError as error:
    raise SystemExit(
        "EasyOCR is not installed for this Python interpreter. "
    ) from error

PROJECT_ROOT = Path(__file__).resolve().parents[1]
IMAGE_PATH = PROJECT_ROOT / 'data' / 'processed' / "detected_card.jpg"
MIN_CONFIDENCE = 0.5
MIN_NAME_CONFIDENCE = 0.4
UPSCALE = 2
MAX_SKEW_DEGREES = 25
NAME_CHARACTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ "

#Terms that appear on the line below the name, so a line containing them is not a name
EXCLUDED_TERMS = {
    'BACHELOR', 'MASTER', 'PHD', 'SCIENCE', 'DEGREE', 'UNIVERSITY',
    'MAYNOOTH', 'DATE', 'BIRTH', 'VALID', 'UNTIL', 'STUDENT', 'CARD',
    'OF', 'NATIONAL', 'IRELAND'
}

# Initialize EasyOCR reader with English language and GPU disabled
reader = easyocr.Reader(['en'], gpu=False)

"""
Find how far the text in a greyscale image is tilted.
Each angle is tested by rotating the image and adding up the dark pixels in each row. The rows are most uneven when the
text lines are level, as rows then fall either fully on a line of text or fully between two lines.
"""
def find_skew_angle(gray):
    small = cv2.resize(gray, None, fx=0.5, fy=0.5)
    binary = cv2.adaptiveThreshold(small, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 31, 12)
    height, width = binary.shape

    best_angle, best_score = 0.0, -1.0
    for angle in np.arange(-MAX_SKEW_DEGREES, MAX_SKEW_DEGREES + 1, 1.0):
        matrix = cv2.getRotationMatrix2D((width / 2, height / 2), float(angle), 1.0)
        rows = cv2.warpAffine(binary, matrix, (width, height)).sum(axis=1).astype(float)
        score = float(np.var(rows))
        if score > best_score:
            best_angle, best_score = float(angle), score
    return best_angle

"""
Read the name printed under a student number.
The number's position is used to crop the area around it, which is then straightened and enlarged before a second OCR pass limited to capital letters.
Returns (name, confidence), or (None, 0.0) if the line under the number is not a readable name.
"""
def read_name_below_number(image, number_box):
    xs = [p[0] for p in number_box]
    ys = [p[1] for p in number_box]
    left, right, top, bottom = min(xs), max(xs), min(ys), max(ys)
    number_width, number_height = right - left, bottom - top

    #The name starts under the number and runs further right, so the crop extends mostly to the right and downwards
    image_height, image_width = image.shape[:2]
    x1 = int(max(0, left - 0.4 * number_width))
    x2 = int(min(image_width, right + 3.2 * number_width))
    y1 = int(max(0, top - 1.2 * number_height))
    y2 = int(min(image_height, bottom + 2.5 * number_height))
    gray = cv2.cvtColor(image[y1:y2, x1:x2], cv2.COLOR_BGR2GRAY)

    crop_height, crop_width = gray.shape
    matrix = cv2.getRotationMatrix2D((crop_width / 2, crop_height / 2), find_skew_angle(gray), 1.0)
    straight = cv2.warpAffine(gray, matrix, (crop_width, crop_height), flags=cv2.INTER_CUBIC, borderValue=255)
    enlarged = cv2.resize(straight, None, fx=UPSCALE, fy=UPSCALE, interpolation=cv2.INTER_CUBIC)

    #Work out where the centre of the number ended up after cropping, rotating and enlarging
    centre = np.array([(left + right) / 2 - x1, (top + bottom) / 2 - y1, 1.0])
    number_x, number_y = (matrix @ centre) * UPSCALE
    number_left = number_x - number_width * UPSCALE / 2

    #Group the words below the number into lines of text
    lines = []
    words = []
    for box, text, confidence in reader.readtext(enlarged, allowlist=NAME_CHARACTERS):
        word_top = min(p[1] for p in box)
        word_height = max(p[1] for p in box) - word_top
        if word_top > number_y and text.strip():
            words.append((word_top, min(p[0] for p in box), word_height, text.strip(), confidence))

    for word in sorted(words):
        if lines and word[0] - lines[-1][0][0] < 0.5 * word[2]:
            lines[-1].append(word)
        else:
            lines.append([word])

    #The name is the first line below the number that lines up with its left edge
    for line in lines:
        line.sort(key=lambda word: word[1])
        if abs(line[0][1] - number_left) > number_width * UPSCALE * 0.5:
            continue

        name = " ".join(word[3] for word in line)
        confidence = min(word[4] for word in line)
        words_in_name = name.split()
        if (
            len(words_in_name) >= 2
            and not set(words_in_name).intersection(EXCLUDED_TERMS)
            and confidence >= MIN_NAME_CONFIDENCE
        ):
            return name, float(confidence)
        break

    return None, 0.0

"""
Find every student in an image (BGR array) by looking for 8 digit student numbers and reading the name under each one.
Returns a list of (student_number, student_name, name_confidence).
"""
def read_students(image):
    students = []
    for box, text, confidence in reader.readtext(image):
        cleaned = text.strip()
        if re.fullmatch(r"\d{8}", cleaned) and confidence >= MIN_CONFIDENCE:
            name, name_confidence = read_name_below_number(image, box)
            students.append((cleaned, name, name_confidence))
    return students

#Extract the first student's details from an image file
def extract_student_details(image_path):
    image = cv2.imread(str(image_path))
    if image is None:
        raise FileNotFoundError(f"Could not load image: {image_path}")

    students = read_students(image)
    if not students:
        return None, None
    return students[0][0], students[0][1]

def main():
    if not IMAGE_PATH.exists():
        raise FileNotFoundError(f"Could not load image: {IMAGE_PATH}")

    student_number, student_name = extract_student_details(IMAGE_PATH)

    print("\nATTENDANCE RESULT:")
    print(f"Student number: {student_number}")
    print(f"Student name: {student_name}")

if __name__ == "__main__":
    main()