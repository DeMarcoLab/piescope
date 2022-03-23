
import logging
import numpy as np
import scipy.ndimage as ndi
import skimage
from skimage.transform import AffineTransform

import piescope.utils


def point_coords(matched_points_dict):
    """Create source & destination coordinate numpy arrays from cpselect dict.

    Matched points is an array where:
    * the number of rows is equal to the number of points selected.
    * the first column is the point index label.
    * the second and third columns are the source x, y coordinates.
    * the last two columns are the destination x, y coordinates.

    Parameters
    ----------
    matched_points_dict : dict
        Dictionary returned from cpselect containing matched point coordinates.

    Returns
    -------
    (src, dst)
        Row, column coordaintes of source and destination matched points.
        Tuple contains two N x 2 ndarrays, where N is the number of points.
    """

    matched_points = np.array([list(point.values())
                               for point in matched_points_dict])
    src = np.flip(matched_points[:, 1:3], axis=1)  # flip for row, column index
    dst = np.flip(matched_points[:, 3:], axis=1)   # flip for row, column index

    return src, dst


def calculate_transform(src, dst, model=AffineTransform()):
    """Calculate transformation matrix from matched coordinate pairs.

    Parameters
    ----------
    src : ndarray
        Matched row, column coordinates from source image.
    dst : ndarray
        Matched row, column coordinates from destination image.
    model : scikit-image transformation class, optional.
        By default, model=AffineTransform()


    Returns
    -------
    ndarray
        Transformation matrix.
    """

    model.estimate(src, dst)
    logging.info(f'Transformation matrix: {model.params}')

    return model.params


def apply_transform(image, transformation, inverse=True, multichannel=True):
    """Apply transformation to a 2D image.

    Parameters
    ----------
    image : ndarray
        Input image array. 2D grayscale image expected, or
        2D plus color channels if multichannel kwarg is set to True.
    transformation : ndarray
        Affine transformation matrix. 3 x 3 shape.
    inverse : bool, optional
        Inverse transformation, eg: aligning source image coords to destination
        By default `inverse=True`.
    multichannel : bool, optional
        Treat the last dimension as color, transform each color separately.
        By default `multichannel=True`.

    Returns
    -------
    ndarray
        Image warped by transformation matrix.
    """

    if inverse:
        transformation = np.linalg.inv(transformation)

    if not multichannel:
        if image.ndim == 2:
            image = skimage.color.gray2rgb(image)
        elif image.ndim != transformation.shape[0] - 1:
            raise ValueError('Unexpected number of image dimensions for the '
                             'input transformation. Did you need to use: '
                             'multichannel=True ?')

    # move channel axis to the front for easier iteration over array
    image = np.moveaxis(image, -1, 0)
    warped_img = np.array([ndi.affine_transform((img_channel), transformation)
                           for img_channel in image])
    warped_img = np.moveaxis(warped_img, 0, -1)

    return warped_img


def overlay_images(fluorescence_image, fibsem_image, transparency=0.5):
    """Blend two RGB images together.

    Parameters
    ----------
    fluorescence_image : ndarray
        2D RGB image.
    fibsem_image : ndarray
        2D RGB image.
    transparency : float, optional
        Transparency alpha parameter between 0 - 1, by default 0.5

    Returns
    -------
    ndarray
        Blended 2D RGB image.
    """

    fluorescence_image = skimage.img_as_float(fluorescence_image)
    fibsem_image = skimage.img_as_float(fibsem_image)
    blended = transparency * fluorescence_image + (1 - transparency) * fibsem_image
    blended = np.clip(blended, 0, 1)

    return blended


def correlate_images(fluorescence_image_rgb, fibsem_image, output_path, matched_points_dict, settings):
    """Correlates two images using points chosen by the user

    Parameters
    ----------
    fluorescence_image_rgb :
        umpy array with shape (cols, rows, channels)
    fibsem_image : AdornedImage.
        Expecting .data attribute of shape (cols, rows, channels)
    output : str
        Path to save location
    matched_points_dict : dict
    Dictionary of points selected in the correlation window
    """
    if matched_points_dict == []:
        logging.error('No control points selected, exiting.')
        return

    src, dst = point_coords(matched_points_dict)
    transformation = calculate_transform(src, dst)
    fluorescence_image_aligned = apply_transform(fluorescence_image_rgb, transformation)
    result = overlay_images(fluorescence_image_aligned, fibsem_image.data)
    result = skimage.util.img_as_ubyte(result)

    # plt.imsave(output_path, result)
    if settings['imaging']['correlation']['autosave']:
        piescope.utils.save_image(result, output_path)

    return result
