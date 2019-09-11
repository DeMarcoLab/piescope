import numpy as np
import pytest

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


def test_(microscope):
    result = piescope.fibsem.last_ion_image(microscope)
    assert microscope.imaging.get_active_view() == 2
    assert result.data.shape == (884, 1024)


def test_(microscope):
    result = piescope.fibsem.last_electron_image(microscope)
    assert microscope.imaging.get_active_view() == 1
    assert result.data.shape == (884, 1024)
