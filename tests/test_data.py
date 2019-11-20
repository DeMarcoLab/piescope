import os

import numpy as np

import piescope.data
import piescope.data.mocktypes


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


def test_MockPixelSize():
    output = piescope.data.mocktypes.MockPixelSize()
    assert np.isclose(output.x, 6.5104167e-09)
    assert np.isclose(output.y, 6.5104167e-09)


def test_MockAdornedImage():
    image = piescope.data.autoscript_image()
    assert image.shape == (884, 1024)
    output = piescope.data.mocktypes.MockAdornedImage(image)
    assert output.data.shape ==  (884, 1024)
    assert np.allclose(output.data, image)
    assert np.isclose(output.metadata.binary_result.pixel_size.x, 9.765625e-09)
    assert np.isclose(output.metadata.binary_result.pixel_size.y, 9.765625e-09)


def test_MockStagePosition():
    output = piescope.data.mocktypes.MockStagePosition()
    assert output.x == 0
    assert output.y == 0
    assert output.z == 0
    assert output.t == 0
    assert output.r == 0
