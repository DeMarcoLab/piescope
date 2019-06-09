import pytest
from piescope.lm import laser


def test_set_laser_power():
    command = laser.set_laser_power(405, 50)
    assert command == "(param-set! 'laser1:level 50)\r"

    command = laser.set_laser_power(405, 75)
    assert command == "(param-set! 'laser1:level 75)\r"

    command = laser.set_laser_power(488, 50)
    assert command == "(param-set! 'laser2:level 50)\r"

    command = laser.set_laser_power(488, 75)
    assert command == "(param-set! 'laser2:level 75)\r"

    command = laser.set_laser_power(561, 50)
    assert command == "(param-set! 'laser3:level 50)\r"

    command = laser.set_laser_power(561, 75)
    assert command == "(param-set! 'laser3:level 75)\r"

    command = laser.set_laser_power(640, 50)
    assert command == "(param-set! 'laser4:level 50)\r"

    command = laser.set_laser_power(640, 75)
    assert command == "(param-set! 'laser4:level 75)\r"

    with pytest.raises(ValueError):
        laser.set_laser_power(405, 222)

    with pytest.raises(TypeError):
        laser.set_laser_power(405, 22.2)

    with pytest.raises(TypeError):
        laser.set_laser_power(405, 50.0)

    with pytest.raises(TypeError):
        laser.set_laser_power("405", 50)

    with pytest.raises(ValueError):
        laser.set_laser_power(420, 50)

    with pytest.raises(TypeError):
        laser.set_laser_power(405.7, 50)

    with pytest.raises(TypeError):
        laser.set_laser_power(405.0, 50)

    with pytest.raises(TypeError):
        laser.set_laser_power(405, "50")

    with pytest.raises(TypeError):
        laser.set_laser_power(504, 50, 1)

    with pytest.raises(TypeError):
        laser.set_laser_power(50)
