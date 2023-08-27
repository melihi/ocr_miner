import cv2
import numpy as np
from datetime import datetime


def process_image(image_location: str):
    """image to Opencv grayscale converter

    Args:
        image_location (str): file path of image

    Returns:
        _type_: _description_
    """
    image = cv2.imread(image_location)

    image = get_grayscale(image)

    # now = datetime.now()
    # current_time = now.strftime("%H_%M_%S")
    # file_location = image_location.replace(".", current_time + ".")
    # cv2.imwrite(file_location, image)

    return image


# get grayscale image
def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


# template matching
def match_template(image, template):
    return cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
