from typing import Any, Callable, Dict, Tuple, cast
from PIL import Image, ImageOps
from functools import reduce
import numpy as np


def set_array(arr: np.ndarray, value: int) -> Callable[[Any], None]:
    def __inner(index: Any) -> None:
        arr[index] = value

    return __inner

def analyze_colors(image: Image.Image, TOTAL_PIXELS : int, THRESHOLDS: Tuple[float, float, float]):
    def __inner(i: int) -> Tuple[Image.Image, float, int]:
        clamped = image.convert(  # type:ignore
            "P", colors=i, palette=Image.Palette.ADAPTIVE
        )

        colors = list(
            cast(Dict[Tuple[int, int, int], int], clamped.palette.colors).keys()
        )

        brightness = max(
            map(
                lambda c: (c[0], colors[c[1]], c[1]),
                clamped.getcolors(i)
            ),
            # https://alienryderflex.com/hsp.html
            key=lambda t: ((0.299 * t[1][0] ** 2 + 0.587 * t[1][1] ** 2 + 0.114 * t[1][2] ** 2) ** 0.5)
        )

        return (clamped, abs(brightness[0] - THRESHOLDS[2]), brightness[2])

    return __inner


def load_food(filename: str, FOOD_POINT_RATIO=0.10, ACCEPTABLE_DELTA=0.05) -> Image.Image:
    """
    Gets food points from the bright spots of an image.

    :param filename -- Source image.

    :return List of (int, int) (x, y)-tuples
    """

    with Image.open(filename) as image:

        TOTAL_PIXELS = reduce(lambda x, y: x * y, image.size)
        COUNT_THRESHOLDS = (TOTAL_PIXELS * (FOOD_POINT_RATIO - ACCEPTABLE_DELTA), TOTAL_PIXELS * (FOOD_POINT_RATIO + ACCEPTABLE_DELTA), TOTAL_PIXELS * FOOD_POINT_RATIO)

        elem = min(map(analyze_colors(image, TOTAL_PIXELS=TOTAL_PIXELS, THRESHOLDS=COUNT_THRESHOLDS), range(2, 16)), key=lambda t: t[1]) # type: ignore
        print(f"DEBUG: {elem[1] / TOTAL_PIXELS * 100}% off target ratio.")

        return clamp_image(image, elem[0], elem[2])


def clamp_image(original_image: Image.Image, image: Image.Image, pallete_color: int) -> Image.Image:

    for index, pixel in np.ndenumerate(image):
        original_image.putpixel((index[1], index[0]), (255, 255, 255) if (pixel == pallete_color) else (0, 0, 0))

    return original_image.rotate(180)


if __name__ == "__main__":
    import sys
    load_food(f"{sys.argv[1]}").save(f"clamped-{sys.argv[1]}")
