import pytest
from piescope.lm import laser


@pytest.mark.parametrize("wavelength_pass, level_pass",
                         [(405, 0), (488, 0), (561, 0), (640, 0),
                          (405, 00), (488, 00), (561, 00), (640, 00),
                          (405, 50), (488, 50), (561, 50), (640, 50),
                          (405, 75), (488, 75), (561, 75), (640, 75),
                          (405, 100), (488, 100), (561, 100), (640, 100)
                          ],)
def test_set_laser_power_pass(wavelength_pass, level_pass):
    if wavelength_pass == 405:
        las = "laser1"
    elif wavelength_pass == 488:
        las = "laser2"
    elif wavelength_pass == 561:
        las = "laser3"
    elif wavelength_pass == 640:
        las = "laser4"

    cmd = laser.set_laser_power(wavelength_pass, level_pass)

    assert cmd == "(param-set! '" + las + ":level " + str(level_pass) + ")\r"


@pytest.mark.parametrize("wavelength_type_error, level_type_error",
                         [(405, 22.2), (488, 22.2), (561, 22.2), (640, 22.2),
                          (405, 50.0), (488, 50.0), (561, 50.0), (640, 50.0),
                          (405, "50"), (488, "50"), (561, "50"), (640, "50"),
                          (405.7, 0), (405.7, 50), (405.7, 75), (405.7, 100),
                          (405.0, 0), (405.0, 50), (405.0, 75), (405.0, 100),
                          ("405", 0), ("405", 50), ("405", 75), ("405", 100),
                          ],)
def test_set_laser_power_type(wavelength_type_error, level_type_error):
    with pytest.raises(TypeError):
        laser.set_laser_power(wavelength_type_error, level_type_error)

    with pytest.raises(TypeError):
        laser.set_laser_power(504, 50, 1)

    with pytest.raises(TypeError):
        laser.set_laser_power(50)


@pytest.mark.parametrize("wavelength_value_error, level_value_error",
                         [(405, -1), (488, -1), (561, -1), (640, -1),
                          (405, 101), (488, 101), (561, 101), (640, 101),
                          (-1, 0), (-1, 50), (-1, 75), (-1, 100),
                          (100, 0), (100, 50), (100, 75), (100, 100),
                          (200, 0), (200, 50), (200, 75), (200, 100),
                          (1000, 0), (1000, 50), (1000, 75), (1000, 100)
                          ],)
def test_set_laser_power_value(wavelength_value_error, level_value_error):
    with pytest.raises(ValueError):
        laser.set_laser_power(wavelength_value_error, level_value_error)
