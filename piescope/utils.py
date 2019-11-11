import skimage.io as io
from autoscript_sdb_microscope_client.structures import AdornedImage
import os.path as p


def save_image(image, dest):
    if type(image) is AdornedImage:
        image.save(dest)
    else:
        io.imsave(dest, image)
