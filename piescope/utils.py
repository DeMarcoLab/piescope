import skimage.io as io
from PIL import Image
import numpy as np


def save_image(image, dest):
    io.imsave(dest, image)


def tif_conversion(image):
    tif_image = Image.open(image)
    rgba_image = np.array(np.flipud(tif_image.convert("RGBA")))

    return rgba_image
