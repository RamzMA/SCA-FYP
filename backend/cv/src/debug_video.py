from pathlib import Path

import cv2

from detect_card import detect_card

PROJECT_ROOT = Path(__file__).resolve().parents[1]
VIDEO_PATH = PROJECT_ROOT / "data" / "uploads"  # folder holding uploaded videos
OUT_DIR = PROJECT_ROOT / "data" / "processed" / "debug_video"
FRAME_INTERVAL = 10
MAX_FRAMES = 15

def sharpness(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(gray, cv2.CV_64F).var()  # higher = sharper

def resize_to_height(img, height):
    h, w = img.shape[:2]
    return cv2.resize(img, (int(w * height / h), height))


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    videos = sorted(VIDEO_PATH.glob("*.*"), key=lambda p: p.stat().st_mtime)
    if not videos:
        raise FileNotFoundError(f"No uploaded videos in {VIDEO_PATH}")
    video = videos[-1]  # the most recent upload
    print(f"Using video: {video.name}")

    capture = cv2.VideoCapture(str(video))
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Video: {width}x{height}, {total} frames, {capture.get(cv2.CAP_PROP_FPS):.1f} fps")

    frame_count = 0
    saved = 0
    while saved < MAX_FRAMES:
        success, frame = capture.read()
        if not success:
            break
        frame_count += 1
        if (frame_count - 1) % FRAME_INTERVAL != 0:
            continue

        card, _, bounds = detect_card(frame)
        overlay = frame.copy()
        if bounds is not None:
            x1, y1, x2, y2 = bounds
            cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 255, 0), max(3, frame.shape[1] // 200))
            print(f"frame {frame_count}: box {x2 - x1}x{y2 - y1}, sharpness {sharpness(frame):.0f}")
        else:
            print(f"frame {frame_count}: no candidate, sharpness {sharpness(frame):.0f}")

        cv2.imwrite(str(OUT_DIR / f"frame_{saved}_box.jpg"), resize_to_height(overlay, 800))
        if card is not None:
            cv2.imwrite(str(OUT_DIR / f"frame_{saved}_crop.jpg"), card)
        saved += 1

    capture.release()
    print(f"Saved to {OUT_DIR}")


if __name__ == "__main__":
    main()