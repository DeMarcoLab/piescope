import numpy as np
import pytest
import serial
from timeit import default_timer as timer

from piescope.lm import laser
from piescope.lm.laser import DEFAULT_SERIAL_PORT, _available_port_names
from serialtestclass import SerialTestClass


<<<<<<< HEAD
@pytest.mark.parametrize("wavelength, power_percentage",
                         [(405, 0), (488, 0), (561, 0), (640, 0),
                          (405, 00), (488, 00), (561, 00), (640, 00),
                          (405, 50), (488, 50), (561, 50), (640, 50),
                          (405, 75), (488, 75), (561, 75), (640, 75),
                          (405, 100), (488, 100), (561, 100), (640, 100)
                          ],)
def test_set_laser_power_pass(wavelength, power_percentage):
    if wavelength == 405:
        las = "laser1"
    elif wavelength == 488:
        las = "laser2"
    elif wavelength == 561:
        las = "laser3"
    elif wavelength == 640:
        las = "laser4"

    cmd = laser.set_laser_power(wavelength, power_percentage)

    assert cmd == "(param-set! '" + las + ":level " + str(power_percentage)\
        + ")\r"


@pytest.mark.parametrize("wavelength, power_percentage",
                         [#(405, 22.2), (488, 22.2), (561, 22.2), (640, 22.2),
                          # (405, 50.0), (488, 50.0), (561, 50.0), (640, 50.0),
                          (405, "50"), (488, "50"), (561, "50"), (640, "50"),
                          (405.7, 0), (405.7, 50), (405.7, 75), (405.7, 100),
                          #(405.0, 0), (405.0, 50), (405.0, 75), (405.0, 100),
                          ("405", 0), ("405", 50), ("405", 75), ("405", 100),
                          ]     ,)
def test_set_laser_power_type(wavelength, power_percentage):
    with pytest.raises(TypeError):
        laser.set_laser_power(wavelength, power_percentage)

    with pytest.raises(TypeError):
        laser.set_laser_power(wavelength, power_percentage, 1)

    with pytest.raises(TypeError):
        laser.set_laser_power(wavelength)


@pytest.mark.parametrize("wavelength, power_percentage",
                         [(405, -1), (488, -1), (561, -1), (640, -1),
                          (405, 101), (488, 101), (561, 101), (640, 101),
                          (-1, 0), (-1, 50), (-1, 75), (-1, 100),
                          (100, 0), (100, 50), (100, 75), (100, 100),
                          (200, 0), (200, 50), (200, 75), (200, 100),
                          (1000, 0), (1000, 50), (1000, 75), (1000, 100)
                          ],)
def test_set_laser_power_value(wavelength, power_percentage):
    with pytest.raises(ValueError):
        laser.set_laser_power(wavelength, power_percentage)


@pytest.mark.parametrize("wavelength, onoff",
                         [(405, "on"), (488, "on"), (561, "on"),
                          (640, "on"), (405, "off"), (488, "off"),
                          (561, "off"), (640, "off"),
                          (405, "ON"), (488, "ON"), (561, "ON"),
                          (640, "ON"), (405, "OFF"), (488, "OFF"),
                          (561, "OFF"), (640, "OFF"),
                          (405, "On"), (488, "On"), (561, "On"),
                          (640, "On"), (405, "Off"), (488, "Off"),
                          (561, "Off"), (640, "Off"),
                          ],)
def test_set_laser_enable_pass(wavelength, onoff):
    if wavelength == 405:
        las = "laser1"
    elif wavelength == 488:
        las = "laser2"
    elif wavelength == 561:
        las = "laser3"
    elif wavelength == 640:
        las = "laser4"

    if onoff.lower() == "on":
        onoff_temp = "t"
    elif onoff.lower() == "off":
        onoff_temp = "f"

    cmd = laser.set_laser_enable(wavelength, onoff)

    assert cmd == "(param-set! '" + las + ":enable #" + onoff_temp + ")\r"


@pytest.mark.parametrize("wavelength, onoff",
                         [(405.7, "on"), (405.7, "off"), (405, 0), (405, 100),
                          (405.0, "on"), (405.0, "off"), (488, 0), (488, 100),
                          ("405", "on"), ("405", "off"), (561, 0), (561, 100),
                          ],)
def test_set_laser_enable_type(wavelength, onoff):
    with pytest.raises(TypeError):
        laser.set_laser_enable(wavelength, onoff)

    with pytest.raises(TypeError):
        laser.set_laser_enable(wavelength, onoff, 1)

    with pytest.raises(TypeError):
        laser.set_laser_enable(wavelength)


@pytest.mark.parametrize("wavelength, onoff",
                         [(405, "nn"), (488, "nn"), (561, "nn"), (640, "nn"),
                          (405, "ff"), (488, "ff"), (561, "ff"), (640, "ff"),
                          (-1, "on"), (-1, "off"), (-100, "on"), (-100, "off"),
                          (100, "on"), (100, "off"), (200, "on"), (200, "off"),
                          (1000, "on"), (1000, "off")
                          ],)
def test_set_laser_enable_value(wavelength, onoff):
    with pytest.raises(ValueError):
        laser.set_laser_enable(wavelength, onoff)


@pytest.mark.parametrize("wavelength, onoff",
                         [(405, "on"), (488, "on"), (561, "on"),
                          (640, "on"), (405, "off"), (488, "off"),
                          (561, "off"), (640, "off"),
                          (405, "ON"), (488, "ON"), (561, "ON"),
                          (640, "ON"), (405, "OFF"), (488, "OFF"),
                          (561, "OFF"), (640, "OFF"),
                          (405, "On"), (488, "On"), (561, "On"),
                          (640, "On"), (405, "Off"), (488, "Off"),
                          (561, "Off"), (640, "Off"),
                          ],)
def test_set_laser_emit_pass(wavelength, onoff):
    if wavelength == 405:
        las = "laser1"
    elif wavelength == 488:
        las = "laser2"
    elif wavelength == 561:
        las = "laser3"
    elif wavelength == 640:
        las = "laser4"

    if onoff.lower() == "on":
        onoff_temp = "t"
    elif onoff.lower() == "off":
        onoff_temp = "f"

    cmd = laser.set_laser_emit(wavelength, onoff)

    assert cmd == "(param-set! '" + las + ":cw #" + onoff_temp + ")\r"


@pytest.mark.parametrize("wavelength, onoff",
                         [(405.7, "on"), (405.7, "off"), (405, 0), (405, 100),
                          (405.0, "on"), (405.0, "off"), (488, 0), (488, 100),
                          ("405", "on"), ("405", "off"), (561, 0), (561, 100),
                          ],)
def test_set_laser_emit_type(wavelength, onoff):
    with pytest.raises(TypeError):
        laser.set_laser_emit(wavelength, onoff)

    with pytest.raises(TypeError):
        laser.set_laser_emit(wavelength, onoff, 1)

    with pytest.raises(TypeError):
        laser.set_laser_emit(wavelength)


@pytest.mark.parametrize("wavelength, onoff",
                         [(405, "nn"), (488, "nn"), (561, "nn"), (640, "nn"),
                          (405, "ff"), (488, "ff"), (561, "ff"), (640, "ff"),
                          (-1, "on"), (-1, "off"), (-100, "on"), (-100, "off"),
                          (100, "on"), (100, "off"), (200, "on"), (200, "off"),
                          (1000, "on"), (1000, "off")
                          ],)
def test_set_laser_emit_value(wavelength, onoff):
    with pytest.raises(ValueError):
        laser.set_laser_emit(wavelength, onoff)
=======
@pytest.fixture
def serial_port_name():
    if DEFAULT_SERIAL_PORT in _available_port_names:
        serial_port_name = DEFAULT_SERIAL_PORT
    else:
        # Substitute the first serial port that does exist
        serial_port_name = _available_port_names[0]
    return serial_port_name


@pytest.fixture
def dummy_serial_port():
    dummy_serial_port = SerialTestClass()
    return dummy_serial_port


@pytest.fixture
def dummy_laser():
    return laser.Laser("laser1", SerialTestClass(), laser_power=1.)


def test__connect_serial_port(serial_port_name):
    output = laser._connect_serial_port(port=serial_port_name)
    assert isinstance(output, serial.Serial)


def test_initialize_lasers():
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
>>>>>>> laser-class
