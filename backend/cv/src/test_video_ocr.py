import tempfile
from pathlib import Path

import cv2

import detect_card as dc
from ocr import extract_student_details  # loads the EasyOCR model on import

PROJECT_ROOT = Path(__file__).resolve().parents[1]
UPLOAD_DIR = PROJECT_ROOT / "data" / "uploads"
FRAME_INTERVAL = 10

dc.DEBUG_CANDIDATES = False  # silence the candidate printout


def main():
    video = max(UPLOAD_DIR.glob("*.*"), key=lambda p: p.stat().st_mtime)
    print(f"RESULT using video: {video.name}")

    capture = cv2.VideoCapture(str(video))
    frame_count = 0

    with tempfile.TemporaryDirectory() as tmp:
        crop_path = Path(tmp) / "crop.jpg"

        while True:
            success, frame = capture.read()
            if not success:
                break
            frame_count += 1
            if (frame_count - 1) % FRAME_INTERVAL != 0:
                continue

            card, _, _ = dc.detect_card(frame)
            if card is None:
                print(f"RESULT frame {frame_count}: no card detected")
                continue

            cv2.imwrite(str(crop_path), card)
            number, name = extract_student_details(crop_path)
            print(
                f"RESULT frame {frame_count}: crop {card.shape[1]}x{card.shape[0]} "
                f"-> number={number}, name={name}"
            )

    capture.release()


if __name__ == "__main__":
    main()