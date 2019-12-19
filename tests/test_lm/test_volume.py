import mock

import numpy as np
import pytest

import pypylon.pylon
import pypylon.genicam

import piescope.data
import piescope.lm.volume
from piescope.lm.detector import Basler
from piescope.lm.objective import StageController

pytest.importorskip('pypylon', reason="The pypylon library is not available.")


def test_mock_basler(monkeypatch):
    # This is how you make a mock Basler detector for the volume function
    monkeypatch.setenv("PYLON_CAMEMU", "1")
    with mock.patch("pypylon.pylon"):
        with mock.patch.object(pypylon.genicam.INodeMap, "GetNode"):
            detector = Basler()
            detector.camera_grab()
            detector.camera.Open()
            detector.camera.ExposureTime.SetValue(10)


@mock.patch.object(StageController, 'connect')
@mock.patch.object(StageController, 'recv')
@mock.patch.object(StageController, 'sendall')
def test_mock_objective_stage(mock_sendall, mock_recv, mock_connect):
    # This is how you mock the SMARACT objective lens stage
    # By mocking the StageConroller connect() method we don't need testing=True
    mock_sendall.return_value = None
    mock_recv.return_value = None
    stage = StageController()  # completely mocked
    stage.current_position()
    mock_sendall.assert_called_with(bytes(':' + 'GP0' + '\012', 'utf-8'))


@mock.patch.object(StageController, 'current_position')
@mock.patch.object(StageController, 'connect')
@mock.patch.object(StageController, 'recv')
@mock.patch.object(StageController, 'sendall')
def test_volume_acquisition(mock_sendall, mock_recv, mock_connect,
                            mock_current_position, tmpdir, monkeypatch):
    mock_current_position.return_value = 5
    monkeypatch.setenv("PYLON_CAMEMU", "1")
    power = 0.01  # as a percentage
    exposure = 200  # in microseconds
    laser_dict = {
        "laser640": (power, exposure),  # 640 nm (far-red)
        "laser561": (power, exposure),  # 561 nm (RFP)
        "laser488": (power, exposure),  # 488 nm (GFP)
        "laser405": (power, exposure),  # 405 nm (DAPI)
    }
    num_z_slices = 3
    z_slice_distance = 10
    destination = tmpdir
    output = piescope.lm.volume.volume_acquisition(
        laser_dict, num_z_slices, z_slice_distance, destination,
        time_delay=0.01, count_max=0, threshold=np.Inf)
    assert output.dtype == np.uint8  # 8-bit output expected
    # Basler emulated mode produces images with shape (1040, 1024)
    # The real Basler detector in the lab produces images with shape (1200, 1920)
    # shape has format: (pln, row, col, ch)
    assert output.shape == (3, 1040, 1024, 4) or output.shape == (3, 1200, 1920, 4)
    if output.shape == (3, 1040, 1024, 4):
        emulated_image = piescope.data.basler_image()
        expected = np.stack([emulated_image for _ in range(4)], axis=-1)
        expected = np.stack([expected, expected, expected], axis=0)
        assert np.allclose(output, expected)
