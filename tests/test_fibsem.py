import numpy as np
import pytest

from piescope.data.mocktypes import MockAdornedImage
import piescope.fibsem

autoscript = pytest.importorskip(
    "autoscript_sdb_microscope_client", reason="Autoscript is not available."
)

try:
    from autoscript_sdb_microscope_client import SdbMicroscopeClient
    microscope = SdbMicroscopeClient()
    microscope.connect("localhost")
except Exception as e:
    pytest.skip("AutoScript cannot connect to localhost, skipping all AutoScript tests.",
                allow_module_level=True)


@pytest.fixture
def microscope():
    from autoscript_sdb_microscope_client import SdbMicroscopeClient

    microscope = SdbMicroscopeClient()
    microscope.connect("localhost")
    return microscope


@pytest.fixture
def image():
    image_array = np.random.random((10, 10))
    return MockAdornedImage(image_array, pixelsize_x=1e-6, pixelsize_y=1e-6)


def test_move_to_light_microscope(microscope):
    original_position = microscope.specimen.stage.current_position
    final_position = piescope.fibsem.move_to_light_microscope(microscope)
    assert np.isclose(final_position.x, original_position.x + 50e-3, atol=1e-7)
    assert np.isclose(final_position.y, original_position.y + 0.)
    assert np.isclose(final_position.z, original_position.z)
    assert np.isclose(final_position.r, original_position.r)
    assert np.isclose(final_position.t, original_position.t)


def test_move_to_electron_microscope(microscope):
    original_position = microscope.specimen.stage.current_position
    final_position = piescope.fibsem.move_to_electron_microscope(microscope)
    assert np.isclose(final_position.x, original_position.x - 50e-3, atol=1e-7)
    assert np.isclose(final_position.y, original_position.y - 0.)
    assert np.isclose(final_position.z, original_position.z)
    assert np.isclose(final_position.r, original_position.r)
    assert np.isclose(final_position.t, original_position.t)


@pytest.mark.parametrize(
    "coord, expected_output",
    [
        ([5, 5], [0, 0]),
        ([6, 5], [1e-6, 0]),
        ([5, 4], [0, 1e-6]),
        ([6, 4], [1e-6, 1e-6]),
        ([4, 6], [-1e-6, -1e-6]),
        ([4, 4], [-1e-6, 1e-6]),
        ([6, 6], [1e-6, -1e-6]),
    ],
)
def test_pixel_to_realspace_coordinate(image, coord, expected_output):
    result = piescope.fibsem.pixel_to_realspace_coordinate(coord, image)
    assert np.allclose(np.array(result), np.array(expected_output))


def test_autocontrast(microscope):
    # This test checks autocontrast does not hit an error
    piescope.fibsem.autocontrast(microscope)



@pytest.mark.parametrize(
    "resolution",
    [
        ("1536x1024"),
        ("3072x2048"),
        ("6144x4096"),
        ("768x512"),
    ],
)
def test_update_camera_settings(resolution):
    dwell_time = 1e-7
    output = piescope.fibsem.update_camera_settings(dwell_time, resolution)
    assert output.dwell_time == dwell_time
    assert output.resolution == resolution
