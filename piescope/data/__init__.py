import os

import numpy as np
import skimage.io

data_dir = os.path.abspath(os.path.dirname(__file__))

__all__ = ['autoscript_image',
           'basler_image',
           'data_dir',
           'embryo',
           'embryo_mask',
           'load_image',
           ]


def autoscript_image():
    """Load a copy of the Autoscript offline emulated image."""
    filename = os.path.join(data_dir, 'autoscript.png')
    img = skimage.io.imread(filename)
    return img


def basler_image():
    """Load a copy of the Basler Fluorescence detector emulator image."""
    filename = os.path.join(data_dir, 'basler.png')
    img = skimage.io.imread(filename)
    img = np.flipud(img)
    # Note: we vertically flip the fluorescence detector images
    # so they match the view of the FIBSEM images,
    # because of how our fluorescence detector is installed (tight space!)
    return img


def embryo():
    """Load the embryo.png file."""
    filename = os.path.join(data_dir, 'embryo.png')
    img = skimage.io.imread(filename)
    return img


def embryo_mask():
    """Load the embryo_mask.png file."""
    filename = os.path.join(data_dir, 'embryo_mask.png')
    img = skimage.io.imread(filename)
    return img


def load_image(filename):
    """Open example image from filename."""
    return skimage.io.imread(filename)
