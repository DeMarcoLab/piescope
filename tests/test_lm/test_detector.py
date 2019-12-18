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


@pytest.mark.parametrize("exposure", [
    (None),
    (500),
    (100),
])
def test_camera_grab_exposure(basler_detector, exposure):
    output = basler_detector.camera_grab(exposure_time=exposure)
    assert output.shape == (1040, 1024)
    assert basler_detector.camera.ExposureMode.GetValue() == 'Timed'
    if exposure is not None:
        assert basler_detector.camera.ExposureTimeAbs.GetValue() == exposure
