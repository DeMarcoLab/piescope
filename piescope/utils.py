import skimage.io as io
from autoscript_sdb_microscope_client.structures import AdornedImage


def save_image(image, destination):
    """Save image to file.

    Parameters
    ----------
    image : ndarray or AdornedImage
        Image array to save.
    destination : str
        Filename of saved image.
    """
    if type(image) is AdornedImage:
        image.save(destination)
    else:
        io.imsave(destination, image)
