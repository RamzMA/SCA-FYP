from pathlib import Path
import re
import easyocr

PROJECT_ROOT = Path(__file__).resolve().parents[1]
IMAGE_PATH = PROJECT_ROOT / 'data' / 'processed' / "manual_card.jpg"
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
    student_name_confidence = 0.0
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
        else:
            words = cleaned.split()
            #Uppercase all words and check if any word in exlcuded terms
            normalized_words = {word.upper() for word in words}
            is_name_candidate = (
                len(words) >= 2
                and cleaned.isupper()
                #check word is alphabetical and no spaces
                and cleaned.replace(" ", "").isalpha()
                and not normalized_words.intersection(excluded_name_terms)
            )

            # If the text is a name candidate and has a higher confidence than the previous name, update the student name and confidence
            if is_name_candidate and confidence > student_name_confidence:
                student_name = cleaned
                student_name_confidence = confidence

    return student_number, student_name

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

