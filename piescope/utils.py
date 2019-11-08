import skimage.io as io
from autoscript_sdb_microscope_client.structures import AdornedImage
import os.path as p


def save_image(image, dest):
    if type(image) is AdornedImage:
        print("ADORNED")
        image.save(dest)
    else:
        print("Not Adorned")
        io.imsave(dest, image)
