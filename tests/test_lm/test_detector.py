import os

import numpy as np
import pytest
from skimage import io

pytest.importorskip('pypylon', reason="The pypylon library is not available.")


@pytest.fixture
def basler_detector(monkeypatch):
    import piescope.lm.detector
    monkeypatch.setenv("PYLON_CAMEMU", "1")
    basler_detector = piescope.lm.detector.Basler()
    return basler_detector


def test_camera_grab(basler_detector):
    output = basler_detector.camera_grab()
    assert output.shape == (1040, 1024)


def test_camera_grab_image(basler_detector):
    output = basler_detector.camera_grab()
    current_directory = os.path.abspath(os.path.dirname(__file__))
    filename = os.path.join(current_directory, 'basler_emulated_image.png')
    expected = io.imread(filename)
    assert np.allclose(output, expected)
