import numpy as np
import pytest
import serial
from timeit import default_timer as timer

from piescope.lm import laser
from piescope.lm.laser import DEFAULT_SERIAL_PORT, _available_port_names
from serialtestclass import SerialTestClass


@pytest.fixture
def dummy_serial_port():
    dummy_serial_port = SerialTestClass()
    return dummy_serial_port


@pytest.fixture
def dummy_laser():
    return laser.Laser("laser640", SerialTestClass(), laser_power=1.)


def test_initialize_lasers():
    output = laser.initialize_lasers(serial_port=SerialTestClass())
    assert len(output) == 4
    assert output["laser405"].NAME == "laser405"
    assert output["laser405"].WAVELENGTH == 405
    assert output["laser488"].NAME == "laser488"
    assert output["laser488"].WAVELENGTH == 488
    assert output["laser561"].NAME == "laser561"
    assert output["laser561"].WAVELENGTH == 561
    assert output["laser640"].NAME == "laser640"
    assert output["laser640"].WAVELENGTH == 640


def test_Laser_class(dummy_serial_port):
    expected_laser_power = 2.
    output = laser.Laser("laser405", dummy_serial_port,
                         laser_power=expected_laser_power)
    assert isinstance(output.SERIAL_PORT, SerialTestClass)
    assert np.isclose(output.laser_power, expected_laser_power)


@pytest.mark.parametrize("name, expected_wavelength",
                         [("laser405", 405),
                          ("laser488", 488),
                          ("laser561", 561),
                          ("laser640", 640),
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
    start_time = timer()
    dummy_laser.emit(expected_duration)
    end_time = timer()
    duration = end_time - start_time
    assert np.isclose(duration, expected_duration, atol=0.001)


def test_laser_enable(dummy_laser):
    output = dummy_laser.enable()
    assert output == "(param-set! 'laser1:enable #t)\r"


def test_laser_disable(dummy_laser):
    output = dummy_laser.disable()
    assert output == "(param-set! 'laser1:enable #f)\r"


def test_laser_power():
    new_laser = laser.Laser("laser405", SerialTestClass(), laser_power=1)
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
