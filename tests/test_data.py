import os

import piescope.data


def test_autoscript_image():
    img = piescope.data.autoscript_image()
    assert img.shape == (884, 1024)


def test_embryo_image():
    img = piescope.data.embryo()
    assert img.shape == (2188, 3072)


def test_embryo_mask_image():
    img = piescope.data.embryo_mask()
    assert img.shape == (2188, 3072)


def test_load_image():
    filename = os.path.join(piescope.data.data_dir, 'embryo.png')
    img = piescope.data.load_image(filename)
    assert img.shape == (2188, 3072)
