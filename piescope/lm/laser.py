"""Module for laser control via serial communication."""


def set_laser_power(wavelength, power_percentage):
    if isinstance(wavelength, int):
        if wavelength == 405:
            laser = "1"
        elif wavelength == 488:
            laser = "2"
        elif wavelength == 561:
            laser = "3"
        elif wavelength == 640:
            laser = "4"
        else:
            raise ValueError('Expecting a wavelength of 405, 488, 561 or 640')
    else:
        raise TypeError('Wavelength must be an integer')

    if isinstance(power_percentage, int):
        print(power_percentage)
        if (power_percentage <= 100) & (power_percentage >= 0):
            command = "(param-set! '" + laser + ":level " + str(
                power_percentage) + ")\r"
        else:
            raise ValueError('Power percentage must be between 0 and 100')
    else:
        raise TypeError('Power percentage must be an integer')

    return command

# set_laser_power(405, 12)
# set_laser_power(405, 122)
# set_laser_power(405, 12.2)
# set_laser_power(405, 0.0)
# set_laser_power(405.0, 12)
# set_laser_power(404, 122)
# set_laser_power(404, 12.2)
# set_laser_power(404, -2)