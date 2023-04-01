from typing import List, Tuple
from PIL import Image, ImageOps
import numpy as np


def food_points(filename: str, FOOD_POINT_RATIO=0.1) -> List[Tuple[int, int]]:
    """
    Gets food points from the bright spots of an image.

    :param filename -- Source image.

    :return List of (int, int) (x, y)-tuples
    """
    FOOD_POINT_RATIO = 0.1
    with Image.open(filename) as image:
        width, height = image.size

        food_points = (int)(width * height * FOOD_POINT_RATIO)

        image = ImageOps.grayscale(image)
        data = np.array(image)

        sorted_data = sorted(np.ndenumerate(data), key=lambda t: -t[1])
        return list(map(lambda t: t[0], sorted_data[:food_points]))
