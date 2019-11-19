import numpy as np
import skimage.io as io

from autoscript_sdb_microscope_client.structures import AdornedImage


def save_image(image, destination):
    """Save image to file.

    Parameters
    ----------
    image : ndarray or AdornedImage
        Image array to save. Pixel values must have integer type.
    destination : str
        Filename of saved image, with .tif extension.
        Only the .tif file format is reliably supported.
    """
    if type(image) is AdornedImage:
        image.save(destination)
    else:
        io.imsave(destination, image)


def max_intensity_projection(image, start_slice=0, end_slice=None):
    """Returns maximum intensity projection of fluorescence image volume.

    Parameters
    ----------
    image : expecting numpy array with dimensions (pln, row, col, ch)
    start_slice : expecting integer.  First image index of z sub-stack
    end_slice : expecting integer.  Last image index of z sub-stack, not incl.

    Returns
    -------
    projected_max_intensity
        numpy array
    """
    # Check input validity
    if image.ndim != 4:
        raise ValueError("expecting numpy.array with dimensions "
                         "(pln, row, col, ch)")
    # Slice image stack
    if end_slice is None:
        image = image[start_slice:, ...]
    else:
        image = image[start_slice:end_slice, ...]
    image = np.moveaxis(image, -1, 0)
    results = []
    for channel_image in image:
        max_intensity = np.max(channel_image, axis=0)
        results.append(max_intensity)
    projected_max_intensity = np.stack(results, axis=-1)
    return projected_max_intensity
