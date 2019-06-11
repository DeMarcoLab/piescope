import os
import skimage.io

data_dir = os.path.abspath(os.path.dirname(__file__))

__all__ = ['autoscript_image',
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
