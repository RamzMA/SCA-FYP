from pathlib import Path
import cv2

PROJECT_ROOT = Path(__file__).resolve().parents[1]
VIDEO_PATH = PROJECT_ROOT / "data" / "raw" / "test_video.mp4"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "frames"

def extract_frames(video_path, output_dir, frame_interval=30):
    capture = cv2.VideoCapture(str(video_path))

    if not capture.isOpened():
        raise FileNotFoundError(f"Could not open video: {video_path}")

    output_dir.mkdir(parents=True, exist_ok=True)

    frame_count = 0
    saved_count = 0

    while True:
        success, frame = capture.read()

        if not success:
            break
        if frame_count % frame_interval == 0:
            output_path = output_dir / f"frame_{saved_count:04d}.jpg"
            cv2.imwrite(str(output_path), frame)
            saved_count += 1
        frame_count += 1
    capture.release()

    print(f"Total frames processed: {frame_count}")
    print(f"Total frames saved: {saved_count}")

def main():
    if not VIDEO_PATH.exists():
        raise FileNotFoundError(f"Could not load video: {VIDEO_PATH}")

    extract_frames(VIDEO_PATH, OUTPUT_DIR)

if __name__ == "__main__":
    main()