from pathlib import Path
import re
import easyocr

PROJECT_ROOT = Path(__file__).resolve().parents[1]
IMAGE_PATH = PROJECT_ROOT / 'data' / 'processed' / "detected_card.jpg"
reader = easyocr.Reader(['en'], gpu=False)

def extract_student_details(image_path):
    """
    Initialize and use EasyOCR to extract student number and name
    """
    result = reader.readtext(str(image_path)) 

    """
    Initialize variables to store student number and name, as well as a confidence score for the name.
    Also defined a list of terms that should be excluded to ensure name is picked and not degree name
    """
    student_number = None
    student_name = None
    number_box = None

    excluded_name_terms = {
        'BACHELOR', 'MASTER', 'PHD', 'SCIENCE', 'DEGREE', 'UNIVERSITY',
        'DATE', 'BIRTH', 'VALID', 'UNTIL',
    }

    """
    Loop through box, text and confidence from result with easyocr, and check if the text is a student number or name based on regex and other conditions
    Clean text first and then print every detected text with confidence score
    """
    for box,text,confidence in result:
        cleaned = text.strip()

        print(f"Detected text: {cleaned} | confidence: {confidence:.2f}")

        # Check if the text is a student number if contains 8 digits
        if re.match(r'^\d{8}$', cleaned):
            student_number = cleaned
            number_box = box


    if number_box is not None:
        number_bottom = max(p[1] for p in number_box)
        number_height = (number_bottom - min(p[1] for p in number_box))

        canidates = []


            


def main():
    if not IMAGE_PATH.exists():
        raise FileNotFoundError(
            f"Could not load image: {IMAGE_PATH}"
        )

    #set student number and name to the result of extract_student_details function
    student_number, student_name = extract_student_details(IMAGE_PATH)

    print("ATTENDENCE RESULT:")
    print(f"Student number: {student_number}")
    print(f"Student name: {student_name}")

if __name__ == "__main__":
    main()

