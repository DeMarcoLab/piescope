"""Module for laser control via serial communication."""

import time
import warnings

import serial
import serial.tools.list_ports

DEFAULT_SERIAL_PORT = 'COM6'  # default laser serial communication port
_available_serial_ports = serial.tools.list_ports.comports()
_available_port_names = [port.device for port in _available_serial_ports]
_available_lasers = (("laser640", "laser1", 640), # (far-red)
                     ("laser561", "laser2", 561), # (RFP)
                     ("laser488", "laser3", 488), # (GFP)
                     ("laser405", "laser4", 405)) # (DAPI)
_laser_name_to_wavelength = {i[0]: i[2] for i in _available_lasers}
_laser_wavelength_to_name = {i[2]: i[0] for i in _available_lasers}
_laser_wavelength_to_id = {i[2]: i[1] for i in _available_lasers}
_laser_id_to_wavelength = {i[1]: i[2] for i in _available_lasers}
_laser_name_to_id = {i[0]: i[1] for i in _available_lasers}
_laser_id_to_name = {i[1]: i[0] for i in _available_lasers}


def initialize_lasers(serial_port=None):
    """Initialize all available lasers.

    Parameters
    ----------
    serial_port : pyserial Serial() object, optional
        Serial port for communication with the lasers.

    Returns
    -------
    dict
        Dictionary of Laser() objects for all available lasers.
    """
    if serial_port is None:
        try:
            serial_port = connect_serial_port()
        except Exception:
            warnings.warn('Default laser serial port not available.\n'
                          'Fall back to {}'.format(_available_port_names[0]))
            serial_port = connect_serial_port(_available_port_names[0])
    all_lasers = {name: Laser(name, serial_port)
                  for name in list(_laser_name_to_wavelength)}
    return all_lasers


def connect_serial_port(port=DEFAULT_SERIAL_PORT, baudrate=115200, timeout=1):
    """Serial port for communication with the lasers.

    Parameters
    ----------
    port : str, optional
        Serial port device name, by default 'COM6'.
    baudrate : int, optional
        Rate of communication, by default 115200 bits per second.
    timeout : int, optional
        Timeout period, by default 1 second.

    Returns
    -------
    pyserial Serial() object
        Serial port for communication with the lasers.
    """
    if port == DEFAULT_SERIAL_PORT:
        if DEFAULT_SERIAL_PORT not in _available_port_names:
            warnings.warn('Default laser serial port not available.\n'
                          'Fall back to port {}'.format())
            port = _available_port_names[0]
    return serial.Serial(port, baudrate=baudrate, timeout=timeout)


class Laser():
    """Laser class."""

    def __init__(self, name, serial_port, laser_power=0.):
        """Initialize instance of Laser class. Laser enabled by default.

        Parameters
        ----------
        name : str
            Laser name string for serial communication.
            Available options:
            * "laser1" with wavelength 640nm (far-red)
            * "laser2" with wavelength 561nm (RFP)
            * "laser3" with wavelength 488nm (GFP)
            * "laser4" with wavelength 405nm (DAPI)
        serial_port : pyserial Serial() object
            Serial communication port for the laser.
        laser_power : float, optional
            Laser power percentage, by default 1%.
        """
        self.NAME = name
        self.ID = _laser_name_to_id[self.NAME]
        self.WAVELENGTH = _laser_name_to_wavelength[self.NAME]
        self.SERIAL_PORT = serial_port
        self.laser_power = laser_power
        self.enable()

    def emit(self, duration):
        """Emit laser light for a set duration.

        Parameters
        ----------
        duration : time the laser is on, in seconds.
        """
        command_turn_on = "(param-set! '" + self.ID + ":cw #t)\r"
        command_turn_off = "(param-set! '" + self.ID + ":cw #f)\r"
        self._write_serial_command(command_turn_on)
        time.sleep(duration)
        self._write_serial_command(command_turn_off)
        return command_turn_on, command_turn_off

    def enable(self):
        """Enable the laser.

        Returns
        -------
        str
            Serial command to enable the laser.
        """
        command = "(param-set! '" + self.ID + ":enable #t)\r"
        self._write_serial_command(command)
        self.enabled = True
        return command

    def disable(self):
        """Disable the laser.

        Returns
        -------
        str
            Serial command to disable the laser.
        """
        command = "(param-set! '" + self.ID + ":enable #f)\r"
        self._write_serial_command(command)
        self.enabled = False
        return command

    @property
    def laser_power(self):
        return self._laser_power

    @laser_power.setter
    def laser_power(self, value):
        """Laser power percentage.

        Parameters
        ----------
        value : int or float
            Laser power percentage.

        Returns
        -------
        str
            Serial command to set the laser power percentage.

        Raises
        ------
        ValueError
            Laser power percentage is limited to between 0 and 100.
        """
        if 0 <= value <= 100:
            command = "(param-set! '" + self.ID + \
                ":level " + str(round(value, 2)) + ")\r"
            self._write_serial_command(command)
            self._laser_power = value
        else:
            raise ValueError('Laser power percentage must be between 0 - 100')
        return command

    def _write_serial_command(self, command):
        self.SERIAL_PORT.open()
        bytelength = self.SERIAL_PORT.write(bytes(command, 'utf-8'))
        self.SERIAL_PORT.close()
        return bytelength
