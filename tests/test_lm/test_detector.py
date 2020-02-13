import os

import numpy as np
import pytest

import piescope.data

pytest.importorskip('pypylon', reason="The pypylon library is not available.")


@pytest.fixture
def basler_detector(monkeypatch):
    import piescope.lm.detector
    monkeypatch.setenv("PYLON_CAMEMU", "1")
    basler_detector = piescope.lm.detector.Basler()
    return basler_detector


def test_camera_grab(basler_detector):
    output = basler_detector.camera_grab()
    assert isinstance(output, np.ndarray)
    # Basler emulated mode produces images with shape (1040, 1024)
    # The real Basler detector in the lab produces images with shape (1200, 1920)
    assert output.shape == (1040, 1024) or output.shape == (1200, 1920)


def test_camera_grab_image(basler_detector):
    output = basler_detector.camera_grab()
    if output.shape != (1040, 1024):
        pytest.skip("Real hardware connected for Basler detector, don't check against the emulated image.")
    else:
        expected = piescope.data.basler_image()
        assert np.allclose(output, expected)


@pytest.mark.parametrize("exposure", [
    (None),
    (500),
    (100),
])
def test_camera_grab_exposure(basler_detector, exposure):
    output = basler_detector.camera_grab(exposure_time=exposure)
    assert isinstance(output, np.ndarray)
    # assert output.shape == (1040, 1024)
    # Check exposure mode is 'Timed'
    basler_detector.camera.Open()
    assert basler_detector.camera.ExposureMode.GetValue() == 'Timed'
    basler_detector.camera.Close()
    # check exposre time is the same as you set it to be
    if exposure is not None:
        basler_detector.camera.Open()
        try:
            output_exposure_time = basler_detector.camera.ExposureTime.GetValue()
        except Exception as e:
            output_exposure_time = basler_detector.camera.ExposureTimeAbs.GetValue()
        basler_detector.camera.Close()
        assert exposure == output_exposure_time
