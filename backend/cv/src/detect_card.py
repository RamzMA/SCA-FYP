from pathlib import Path

import cv2
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]
IMAGE_PATH = PROJECT_ROOT / "data" / "processed" / "frames" / "frame_0002.jpg"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"


def detect_card(image):
    #As image.shape comes with (height, width, channels) we only need the first two values height and width for further calculations
    height, width = image.shape[:2]

    #Convert BGR to HSV (So blue, green, red to hue, saturation, value) for better detection of card
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    """
        Extract saturation as 1 in hsv
        Extract brightness as 2 in hsv
        In other words hsv 0-2 is hue, saturation, brightness and we are taking 1 for saturation and 2 for brightness.
    """
    saturation = hsv[:, :, 1]
    brightness = hsv[:, :, 2]

    """
        Find coloured pixels by checking if saturation is greater than 38 and brightness is less than 245
        Find dark pixels by checking if brightness is less than 165
        Create a mask by combining coloured and dark pixels, the thought behind this np.unit8 takes the TRUE output from dark or coloured and then
        it turns it to a number for example 1 for true 0 for faklse and multiple by 255 so 0 * 255 = 0 and 1 * 255 = 255.
    """
    coloured = (saturation > 38) & (brightness < 245)
    dark = brightness < 165
    mask = np.uint8(coloured | dark) * 255 

    close_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (31, 21)
    )
    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        close_kernel
    )

    dilate_kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (13, 13)
    )
    mask = cv2.dilate(mask, dilate_kernel)

    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    best_candidate = None
    best_area = 0

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)

        if h == 0:
            continue

        area = cv2.contourArea(contour)
        coverage = area / (width * height)
        ratio = w / h

        if not 0.005 <= coverage <= 0.40:
            continue

        if not 1.3 <= ratio <= 2.4:
            continue

        if area > best_area:
            best_area = area
            best_candidate = (x, y, w, h)

    if best_candidate is None:
        return None, mask, None

    x, y, w, h = best_candidate

    pad_x = int(w * 0.08)
    pad_y = int(h * 0.12)

    x1 = max(0, x - pad_x)
    y1 = max(0, y - pad_y)
    x2 = min(width, x + w + pad_x)
    y2 = min(height, y + h + pad_y)

    card = image[y1:y2, x1:x2]

    return card, mask, (x1, y1, x2, y2)


def main():
    image = cv2.imread(str(IMAGE_PATH))

    if image is None:
        raise FileNotFoundError(
            f"Could not load image: {IMAGE_PATH}"
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    card, mask, bounds = detect_card(image)

    cv2.imwrite(
        str(OUTPUT_DIR / "detection_mask.jpg"),
        mask
    )

    if card is None:
        print("No ID card detected.")
        return

    cv2.imwrite(
        str(OUTPUT_DIR / "detected_card.jpg"),
        card
    )

    debug_image = image.copy()
    x1, y1, x2, y2 = bounds

    cv2.rectangle(
        debug_image,
        (x1, y1),
        (x2, y2),
        (0, 255, 0),
        3
    )

    cv2.imwrite(
        str(OUTPUT_DIR / "detection_debug.jpg"),
        debug_image
    )

    print("ID card candidate detected.")
    print(f"Card size: {card.shape[1]} x {card.shape[0]}")
    print(f"Saved results to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
