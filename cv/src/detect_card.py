"""
    cv2 - Used to detect image/video of card and process in order to access edges, faces and objects for recognition for attendance.
    numpy - For working with arrays and metrics
    pathlib - Folder work
"""
import cv2
import numpy as np
import pathlib as Path


"""
    IMAGE_PATH - Path for the input image (Currently test student card)
    OUTPUT_PATH - Path for where processed result should be saved
"""

IMAGE_PATH = Path('data/raw/test_card.jpg')
OUTPUT_PATH = Path('data/processed/detected_card.jpg')

#def order_points(points):