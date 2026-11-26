"""
Time each stage of the pipeline on a few frames to see where processing time goes.
Usage command: python time_stages.py path/to/video.mp4 [number_of_frames]
"""
import sys
import time

import cv2

import detect_card as detect_module
from pipeline import sharpest_frames, MIN_SHARPNESS
from ocr import read_students

#Stop detect_card printing a line for every candidate as printing would be included in the timings
detect_module.DEBUG_CANDIDATES = False

video_path = sys.argv[1]
limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10

capture = cv2.VideoCapture(video_path)
detect_total = full_total = crop_total = 0.0
tested = with_card = 0

for frame, sharpness in sharpest_frames(capture, 10):
    if sharpness < MIN_SHARPNESS:
        continue
    if tested >= limit:
        break
    tested += 1

    start = time.perf_counter()
    card, _, _ = detect_module.detect_card(frame)
    detect_total += time.perf_counter() - start

    start = time.perf_counter()
    read_students(frame)
    full_total += time.perf_counter() - start

    if card is not None:
        with_card += 1
        start = time.perf_counter()
        read_students(card)
        crop_total += time.perf_counter() - start

capture.release()
print(f"Frames tested: {tested} (card found in {with_card})")
print(f"detect_card:             {detect_total / max(tested, 1):.2f} s per frame")
print(f"OCR on the whole frame:  {full_total / max(tested, 1):.2f} s per frame")
print(f"OCR on the card crop:    {crop_total / max(with_card, 1):.2f} s per frame with a card")
