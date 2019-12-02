import numpy as np
import skimage.color
import skimage.io

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
        skimage.io.imsave(destination, image)


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


def rgb_image(image):
    """Converts input image to RGB output image.

    Parameters
    ----------
    image : ndarray
        Input image array to convert to an RGB image.
        Must have 2 (grayscale) or 3 (color) image dimensions.
        The number of color channels must be less than 3.

    Returns
    -------
    ndarray (M, N, 3)
        RGB numpy image array.

    Raises
    ------
    ValueError
        Raised if the image dimensions or channels is not allowed.
    """
    if not (image.ndim == 2 or image.ndim == 3):
        raise ValueError("Wrong number of dimensions in input image! "
                         "Expected an image with 2 or 3 dimensions, "
                         "but found {} dimensions".format(image.ndim))
    if image.ndim == 2:
        rgb_image = skimage.color.gray2rgb(image)
        return rgb_image
    elif image.ndim == 3:
        if image.shape[-1] == 1:
            rgb_image = skimage.color.gray2rgb(image[:, :])
            return rgb_image
        elif image.shape[-1] == 2:
            rgb_image = np.zeros(shape=(image.shape[0], image.shape[1], 3),
                                dtype=np.uint8)
            rgb_image[:, :, 0] = image[:, :, 0]
            rgb_image[:, :, 1] = image[:, :, 1]
            return rgb_image
        elif image.shape[-1] == 3:
            rgb_image = image
            return rgb_image
        else:
             raise ValueError("Wrong number of image channels! "
                              "Expected up to 3 image channels, "
                              "but found {} channels.".format(image.shape[-1]))
