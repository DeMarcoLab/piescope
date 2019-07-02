import time

import numpy as np
import pytest

from piescope.lm import laser
from serialtestclass import SerialTestClass


@pytest.fixture
def dummy_serial_port():
    dummy_serial_port = SerialTestClass()
    return dummy_serial_port


@pytest.fixture
def dummy_laser():
    return laser.Laser("laser1", SerialTestClass(), laser_power=1.)


def test_initialize_lasers():
    from piescope.lm.laser import _laser_name_to_wavelength, _laser_wavelength_to_name, _available_lasers
    print(_available_lasers)
    print(_laser_name_to_wavelength)
    print(_laser_wavelength_to_name)
    output = laser.initialize_lasers(serial_port=SerialTestClass())
    assert len(output) == 4
    assert output[0].NAME == "laser1"
    assert output[0].WAVELENGTH == 405
    assert output[1].NAME == "laser2"
    assert output[1].WAVELENGTH == 488
    assert output[2].NAME == "laser3"
    assert output[2].WAVELENGTH == 561
    assert output[3].NAME == "laser4"
    assert output[3].WAVELENGTH == 640


def test_Laser_class(dummy_serial_port):
    expected_laser_power = 2.
    output = laser.Laser("laser1", dummy_serial_port,
                         laser_power=expected_laser_power)
    assert isinstance(output.SERIAL_PORT, SerialTestClass)
    assert np.isclose(output.laser_power, expected_laser_power)


@pytest.mark.parametrize("name, expected_wavelength",
                         [("laser1", 405),
                          ("laser2", 488),
                          ("laser3", 561),
                          ("laser4", 640),
                          ],)
def test_laser(name, expected_wavelength):
    new_laser = laser.Laser(name, SerialTestClass(), laser_power=1)
    assert new_laser.WAVELENGTH == expected_wavelength


def test_laser_emit(dummy_laser):
    expected_duration = 0.2
    output_command_on, output_command_off = dummy_laser.emit(expected_duration)
    assert output_command_on == "(param-set! 'laser1:cw #t)\r"
    assert output_command_off == "(param-set! 'laser1:cw #f)\r"


@pytest.mark.parametrize("expected_duration",
                         [(0.005),
                          (0.01),
                          (0.05),
                          (0.1),
                          ],)
def test_laser_emit_duration(dummy_laser, expected_duration):
    start_time = time.perf_counter()
    dummy_laser.emit(expected_duration)
    end_time = time.perf_counter()
    duration = end_time - start_time
    assert duration >= expected_duration
    assert duration <= 1.2 * expected_duration


def test_laser_enable(dummy_laser):
    output = dummy_laser.enable()
    assert output == "(param-set! 'laser1:enable #t)\r"


def test_laser_disable(dummy_laser):
    output = dummy_laser.disable()
    assert output == "(param-set! 'laser1:enable #f)\r"


def test_laser_power():
    new_laser = laser.Laser("laser1", SerialTestClass(), laser_power=1)
    expected_laser_power = 3.3
    new_laser.laser_power = expected_laser_power
    assert np.isclose(new_laser.laser_power, expected_laser_power)


@pytest.mark.parametrize("invalid_laser_power",
                         [(-1.),
                          (150.),
                          (np.NaN),
                          (np.Inf),
                          ],)
def test_laser_power_invalid(dummy_laser, invalid_laser_power):
    with pytest.raises(ValueError):
        dummy_laser.laser_power = invalid_laser_power
