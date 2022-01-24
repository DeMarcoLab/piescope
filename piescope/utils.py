from datetime import datetime
import logging
import os
import re

import numpy as np
import skimage.color
import skimage.io
import skimage.util
import tifffile


def save_image(image, destination, metadata={}, *, allow_overwrite=False,
               timestamp=True):
    """Save image to file.

    Parameters
    ----------
    image : ndarray or AdornedImage
        Image array to save. Pixel values must have integer type.
    destination : str
        Filename of saved image, with .tif extension.
        Only the .tif file format is reliably supported.
    metadata : dict, optional
        This kwarg is ignored for AdornedImage, used only for numpy arrays.
        Default value is an empty dictionary.
        There are no restrictions on what key-value pairs you can use here.
        You can access this metadata in Fiji/ImageJ by opening the saved image
        with the BioFormats importer and checking the box 'Display Metadata'.
    allow_overwrite : bool, optional
        Whether to allow overwriting existing files. Default is False.
    timestamp : bool, optional
        Time stamp appended to filename.
        Uses ISO 8601 standard format, YYYY-mm-ddTTHHmmsszz
        ISO 8601 reference: https://en.wikipedia.org/wiki/ISO_8601

    Notes
    -----
    https://www.lfd.uci.edu/~gohlke/code/tifffile.py.html

    Save a volume with xyz voxel size 2.6755x2.6755x3.9474 µm^3 to an ImageJ file:

    >>> volume = numpy.random.randn(57*256*256).astype('float32')
    >>> volume.shape = 1, 57, 1, 256, 256, 1  # dimensions in TZCYXS order
    >>> imwrite('temp.tif', volume, imagej=True, resolution=(1./2.6755, 1./2.6755),
    ...         metadata={'spacing': 3.947368, 'unit': 'um'})

    """
    destination = os.path.normpath(destination)
    # Make sure the output file format is acceptable
    SUPPORTED_IMAGE_TYPES = ('.tif')
    if not destination.endswith(SUPPORTED_IMAGE_TYPES):
        destination += '.tif'
    # Append timestamp string to filename, if needed
    if timestamp:
        timestamp_string = datetime.now().strftime("_%Y-%m-%dT%H%M%S%f")
        base, ext = os.path.splitext(destination)
        destination = base + timestamp_string + ext
    # Modify filename to prevent overwriting, if allow_overwrite is False
    # Appends filenames with "_(1)", "_(2)", etc.
    if allow_overwrite is False:
        while os.path.exists(destination):
            base, ext = os.path.splitext(destination)
            regex_match = re.search("_\\([0-9]*\\)$", base)
            if regex_match:
                current_idx = int(regex_match.group(0)[2:-1])  # strip "_(" ")"
                suffix_len = len(regex_match.group(0))
                destination = (
                    base[:-suffix_len] + "_({})".format(current_idx + 1) + ext
                )
            else:
                destination = base + "_(1)" + ext
    # If directory does not currently exist, create it
    directory_name = os.path.dirname(destination)
    if not directory_name == '' and not os.path.isdir(directory_name):
        os.makedirs(directory_name)
    try:
        image.save(destination)  # eg: for AutoScript AdornedImage datatypes
        logging.debug("Saved: {}".format(destination))
        # Metadata for AdornedImage types is saved in the OME-TIFF metadata.
        # You can load the image and metadata back in using .load(), eg:
        # from autoscript_sdb_microscope_client.structures import AdornedImage
        # returned_image = AdornedImage().load("autoscript_save_filename.tif")
    except AttributeError:
        # numpy array metadata is saved with regular metadata (not OME-TIFF)
        if isinstance(image, np.ndarray):
            # Make sure we have the right datatype to svae for ImageJ
            if image.dtype.char not in 'BHhf':  # uint8, uint16, int16, or ?
                image = skimage.util.img_as_uint(image)  # 16 bit unsigned int
            # If it's a volume image, must split channels and save individually
            if image.ndim == 5:  # (AZPYX)
                tifffile.imwrite(destination, image, bigtiff=True, metadata=metadata)

            elif image.ndim == 6:  #(CAZPYX) --> (AZPYX)
                volume_split = np.zeros(image.shape)
                for i in range(image.shape[1]):
                    volume_split[:, i] = image[:, i]
                    metadata.update({'axes': 'AZPYX'})
                    destination = destination.replace('.tif', '') + '_channel_' + str(i) + '.tif'
                    logging.debug("Saved: {}".format(destination))
                    tifffile.imwrite(destination, volume_split[:, i], bigtiff=True,
                                     metadata=metadata)

            elif image.ndim == 3:  # (YXC)
                image = np.moveaxis(image, -1, 0)  # move channel axis (CYX)
                metadata.update({'axes':'CYX'})
                skimage.io.imsave(destination, image, imagej=True,
                    metadata=metadata)
                logging.debug("Saved: {}".format(destination))
            else:  # Save all other images without changes
                skimage.io.imsave(destination, image, imagej=True,
                    metadata=metadata)
                logging.debug("Saved: {}".format(destination))
        else:
            raise ValueError(
                "Cannot save image! Expected a numpy array or AdornedImage, "
                "instead found image.dtype of {}".format(image.dtype)
                )


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
    results = []
    # TODO: make this consistent
    if image.ndim == 6:  #CAZPYX

        for channel_image in image:
            max_intensity = np.max(channel_image, axis=(0, 1, 2))
            results.append(max_intensity)
        projected_max_intensity = np.stack(results, axis=-1)

    # Check input validity
    else:
        if image.ndim != 4:
            raise ValueError("expecting numpy.array with dimensions "
                             "(pln, row, col, ch)")
            # Slice image stack
        if end_slice is None:
            image = image[start_slice:, ...]
        else:
            image = image[start_slice:end_slice, ...]
        image = np.moveaxis(image, -1, 0)

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
        rgb_image = image
        # rgb_image = skimage.color.gray2rgb(image)
        return rgb_image
    elif image.ndim == 3:
        if image.shape[-1] == 1:
            rgb_image = np.zeros(shape=(image.shape[0], image.shape[1], 3),
                                dtype=np.uint8)
            rgb_image[:, :, 0] = image[:, :, 0]
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
