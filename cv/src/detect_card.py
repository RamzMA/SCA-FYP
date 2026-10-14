"""
    cv2 - Used to detect image/video of card and process in order to access edges, faces and objects for recognition for attendance.
    numpy - For working with arrays and metrics
    pathlib - Folder work
"""
from pathlib import Path

import cv2
import numpy as np

"""
    IMAGE_PATH - Path for the input image (Currently test student card)
    OUTPUT_PATH - Path for where processed result should be saved
"""

PROJECT_ROOT = Path(__file__).resolve().parents[1]
IMAGE_PATH = PROJECT_ROOT / "data" / "raw" / "test_card.png"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "detected_card.jpg"

"""
    Order points in detect all the points of the card, in other words the corners.
"""

def order_points(points):
    rectangle = np.zeros((4,2), dtype=np.float32) # Create space for coordinates, basically 4 [0,0]s right now

    """
        Get the sum- The reason to get the sum is the smallest x+y can determine the top-left, while the largest can determine bottom-right.
        Get the differences- Opposite of the sum the smallest y-x is the top-right, while the largest is the bottom-left.
    """
    sums = points.sum(axis=1) #Add x+y to get full value of x and y added. Eg [100,100] = 200.
    differences = np.diff(points, axis=1).flatten() # Calculute the y-x, so [100, 100] = 0

    """
        Getting the sums largest and smallest for reference to top-left and bottom-right.
        Reference photo: 1
    """
    rectangle[0] = points[np.argmin(sums)]
    rectangle[2] = points[np.argmax(sums)]

    """
        Getting the differences largest and smallest for reference to top-right and bottom-left.
    """
    rectangle[1] = points[np.argmin(differences)]
    rectangle[3] = points[np.argmax(differences)]

    return rectangle

"""
    Transform card from distorted to normal view (normal rectangle), taking the camera frame, and points which is the 4 corners
"""
def perspective_transform(image,points):
    rect = order_points(points)

    top_left,top_right, bottom_right, bottom_left = rect

    """
        Calculate both widths of bottom-bottom and top-top using pythagorous in order to grab the biggest width and turn into a int.
        Do same for height
    """
    width_a = np.linalg.norm(bottom_right - bottom_left)
    width_b = np.linalg.norm(top_right - top_left)
    max_width = int(max(width_a, width_b))

    height_a = np.linalg.norm(top_right - bottom_right)
    height_b = np.linalg.norm(top_left - bottom_left)
    max_height = int(max(height_a, height_b))

    """
        Get the rectange coords,
        [0,0] is the top left,
        [max_width-1, 0] is the top right (-1 as we do not want coords to start at 1, we want it to start at 0 so if max_width is 500 it becomes 499)
        [max_width-1,max_height-1] is the bottom right
        [0, max_height-1] is the bottom left
    """
    destination = np.array(
        [
            [0,0],
            [max_width - 1, 0],
            [max_width -1, max_height-1],
            [0, max_height-1]
        ],
        dtype=np.float32,
    )

    #Figures out what points need to get to in order to transform to proper rectangle for later analysation 
    matrix = cv2.getPerspectiveTransform(rect, destination)

    """
        Actually transform the card to proper rectangle by taking original image, the points needed to be transformed to and finally the max_width and max_height. 
    """
    warped = cv2.warpPerspective(
        image,
        matrix,
        (max_width,max_height)
    )

    return warped

def detect_card(image):
    #Convert to grayscale 
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    #reduce unnecessary details from image such as hair by blurring slightly
    blurred = cv2.GaussianBlur(gray, (5,5), 0)

    """
        Find edges using range from 50-150 to seperate desk from card for example. 
        Card should be whiter and desk darker, so for example if 150 is detected strong indiactor its a card.
    """
    edges = cv2.Canny(blurred, 50, 150)

    """
        There may be many contours on the card due to the photo and other factors so we get the external with cv2.RETR_EXTERNAL for the whole card,
        Then we use cv2.CHAIN_APPROX_SIMPLE to reduce the number of points needed to represent contours 
    """
    contours, _ = cv2.findContours(
        edges,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    """
        Sort all contours according to size then reverse to ensure biggest is first as Card will be the most prominent object in the frame therefore get biggest contour
    """
    contours = sorted(
        contours,
        key=cv2.contourArea,
        reverse=True
    )

    image_area = image.shape[0] * image.shape[1]

    #Check for first 20 contours in sorted contours from earlier as there may be many and we only need the biggest
    for contour in contours[:20]:
        area = cv2.contourArea(contour)
        if area <= 10000 or area / image_area < 0.05:
            continue

        box = cv2.minAreaRect(contour)
        box_width, box_height = box[1]
        if min(box_width, box_height) == 0:
            continue

        aspect_ratio = max(box_width, box_height) / min(box_width, box_height)
        if not 1.3 <= aspect_ratio <= 2.2:
            continue

        perimeter = cv2.arcLength(contour, True)

        #Simplify contour into a polygon. The card edge may not be perfectly square in the image,
        #so accept contours that approximate to a rectangle rather than requiring exactly 4 points.
        approximate = cv2.approxPolyDP(
            contour,
            0.02 * perimeter,
            True
        )

        if len(approximate) >= 4:
            # Use the minimum-area box to get the true 4 corners of the card even when the contour is slightly irregular.
            points = cv2.boxPoints(box)
            return perspective_transform(image, points.astype(np.float32))
    return None

def main():
    #Read image from file
    image = cv2.imread(str(IMAGE_PATH))

    if image is None:
        raise FileNotFoundError(
            f"Could not load image: {IMAGE_PATH}"
        )

    card = detect_card(image)

    if card is None:
        if OUTPUT_PATH.exists():
            OUTPUT_PATH.unlink()
        print("No ID card detected.")
        return

    #Ensure output folder exists, if it already does exist_okay ensurtes no errors thrown
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    cv2.imwrite(str(OUTPUT_PATH), card)

    print('ID card detected.')
    print(f'Saved to {OUTPUT_PATH}')
    print(f'Card size: {card.shape[1]} x {card.shape[0]}')

if __name__ == "__main__":
    main()


    


