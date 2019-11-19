import numpy as np
import pytest

from piescope.data.mocktypes import MockAdornedImage
import piescope.fibsem

autoscript = pytest.importorskip(
    "autoscript_sdb_microscope_client", reason="Autoscript is not available."
)


def test_initialize():
    """Test connecting to the microscope offline with localhost."""
    microscope = piescope.fibsem.initialize("localhost")


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


def test_new_ion_image(microscope):
    result = piescope.fibsem.new_ion_image(microscope)
    assert microscope.imaging.get_active_view() == 2
    assert result.data.shape == (884, 1024)


def test_new_electron_image(microscope):
    result = piescope.fibsem.new_electron_image(microscope)
    assert microscope.imaging.get_active_view() == 1
    assert result.data.shape == (884, 1024)


def test_last_ion_image(microscope):
    result = piescope.fibsem.last_ion_image(microscope)
    assert microscope.imaging.get_active_view() == 2
    assert result.data.shape == (884, 1024)


def test_last_electron_image(microscope):
    result = piescope.fibsem.last_electron_image(microscope)
    assert microscope.imaging.get_active_view() == 1
    assert result.data.shape == (884, 1024)


def test_create_rectangular_pattern(microscope, image):
    x0 = 2
    x1 = 8
    y0 = 3
    y1 = 7
    depth = 1e-6
    output = piescope.fibsem.create_rectangular_pattern(
        microscope, image, x0, x1, y0, y1, depth)
    expected_center_x = 0
    expected_center_y = 0
    expected_width = 6e-6
    expected_height = 4e-6
    assert np.isclose(output.center_x, expected_center_x)
    assert np.isclose(output.center_y, expected_center_y)
    assert np.isclose(output.width, expected_width)
    assert np.isclose(output.height, expected_height)
    assert np.isclose(output.depth, depth)  # depth is unchanged
    assert np.isclose(output.rotation, 0)  # no rotation by befault


def test_empty_rectangular_pattern(microscope, image):
    x0 = None
    x1 = None
    y0 = 3
    y1 = 7
    depth = 1e-6
    output = piescope.fibsem.create_rectangular_pattern(
        microscope, image, x0, x1, y0, y1, depth)
    assert output is None


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
