"""Module for laser control via serial communication."""

import time

import serial

def set_laser_power(wavelength, power_percentage):
    """Create command string to change laser power to 'power_percentage'"""
    if isinstance(wavelength, int):
        if wavelength == 405:
            laser = "laser1"
        elif wavelength == 488:
            laser = "laser2"
        elif wavelength == 561:
            laser = "laser3"
        elif wavelength == 640:
            laser = "laser4"
        else:
            raise ValueError('Expecting a wavelength of 405, 488, 561 or 640')
    else:
        raise TypeError('Wavelength must be an integer')

    if isinstance(power_percentage, int):
        if (power_percentage <= 100) & (power_percentage >= 0):
            command = "(param-set! '" + laser + ":level " + str(
                power_percentage) + ")\r"
        else:
            raise ValueError('Power percentage must be between 0 and 100')
    else:
        raise TypeError('Power percentage must be an integer')

    return command


def set_laser_enable(wavelength, onoff):
    """Create command string to change laser enabled to 'onoff' value"""
    if isinstance(wavelength, int):
        if wavelength == 405:
            laser = "laser1"
        elif wavelength == 488:
            laser = "laser2"
        elif wavelength == 561:
            laser = "laser3"
        elif wavelength == 640:
            laser = "laser4"
        else:
            raise ValueError('Expecting a wavelength of 405, 488, 561 or 640')
    else:
        raise TypeError('Wavelength must be an integer')

    if isinstance(onoff, str):
        if onoff.lower() == "on":
            command = "(param-set! '" + laser + ":enable #t)\r"
        elif onoff.lower() == "off":
            command = "(param-set! '" + laser + ":enable #f)\r"
        else:
            raise ValueError('On/off value must be "on" or "off"')
    else:
        raise TypeError('On/off value must be a string')

    return command


def set_laser_emit(wavelength, onoff):
    """Create command string to change laser emit to 'onoff' value"""
    if isinstance(wavelength, int):
        if wavelength == 405:
            laser = "laser1"
        elif wavelength == 488:
            laser = "laser2"
        elif wavelength == 561:
            laser = "laser3"
        elif wavelength == 640:
            laser = "laser4"
        else:
            raise ValueError('Expecting a wavelength of 405, 488, 561 or 640')
    else:
        raise TypeError('Wavelength must be an integer')

    if isinstance(onoff, str):
        if onoff.lower() == "on":
            command = "(param-set! '" + laser + ":cw #t)\r"
        elif onoff.lower() == "off":
            command = "(param-set! '" + laser + ":cw #f)\r"
        else:
            raise ValueError('On/off value must be "on" or "off"')
    else:
        raise TypeError('On/off value must be a string')

    return command


def _serial_write(command, port):
    """Send command string over serial port 'port' to set laser parameters"""
    ser = serial.Serial(port, baudrate=115200, timeout=1)
    ser.write(bytes(command, 'utf-8'))
    time.sleep(1)
    ser.close()
