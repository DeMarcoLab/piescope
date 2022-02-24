"""Module for laser control via serial communication."""
from dataclasses import dataclass
from wsgiref.simple_server import demo_app

import numpy as np
from piescope import utils


@dataclass
class Laser:
    name: str
    serial_id: str
    wavelength: float
    power: float
    exposure_time: float  # us
    enabled: bool
    pin: str


class LaserController:
    def __init__(self, settings):

        self.lasers = {}
        self.serial_connection = utils.connect_serial_port(settings)

        # grab available lasers
        for laser in settings["lm"]["lasers"]:
            current_laser = Laser(
                name=laser["name"],
                serial_id=laser["ID"],
                wavelength=laser["wavelength"],
                power=0.0,
                exposure_time=0.0,
                enabled=False,
                pin=laser["pin"]
            )
            self.lasers[current_laser.name] = current_laser

        # set initial laser values
        for laser in self.lasers.values():
            self.enable(laser)

        default_laser = settings['lm']['default_laser']
        if default_laser not in self.lasers:
            raise ValueError(f"Default laser set in config not found in available lasers.  Default laser is {default_laser}")

        self.current_laser = self.lasers[default_laser]

    def set_laser_power(self, laser: Laser, power: float) -> None:
        """sets power level of laser

        Parameters
        ----------
        laser : Laser
            laser to set the power level of
        power : float
            percentage of total power to set

        Raises
        ------
        TypeError
            Laser power percentage must be a float
        """
        if not isinstance(power, float):
            raise TypeError(f"Power must be a float. {type(power)} was passed.")

        power = np.clip(power, 0.0, 100.0)
        command = (
            "(param-set! '" + laser.serial_id + ":level " + str(round(power, 2)) + ")\r"
        )
        utils.write_serial_command(self.serial_connection, command)
        laser.power = power

    def get_laser_power(self, laser: Laser) -> float:
        """returns the laser power

        Parameters
        ----------
        laser : Laser
            laser to get the power level of

        Returns
        -------
        float
            laser power as percentage of total
        """
        return laser.power

    def set_exposure_time(self, laser: Laser, exposure_time: float) -> None:
        """sets exposure time of laser

        Parameters
        ----------
        laser : Laser
            laser to set the exposure time of
        exposure time : float
             exposure time to set in microseconds

        Raises
        ------
        TypeError
            Laser power percentage must be a float
        """
        if not isinstance(exposure_time, float):
            raise TypeError(
                f"Exposure time must be a float. {type(exposure_time)} was passed."
            )

        exposure_time = np.clip(
            exposure_time, 0.0, 10.0e6
        )  # unable to reverse the flow of time
        laser.exposure_time = exposure_time

    def get_exposure_time(self, laser: Laser) -> float:
        """returns the exposure time for the laser

        Parameters
        ----------
        laser : Laser
            laser to get the exposure time of

        Returns
        -------
        float
            exposure time
        """
        return laser.exposure_time

    def enable(self, laser: Laser) -> None:
        """enables the laser using serial commands.
        See documentation file for command structure.

        Parameters
        ----------
        laser : Laser
            the laser to enable

        """
        command = "(param-set! '" + laser.serial_id + ":enable #t)\r"
        utils.write_serial_command(self.serial_connection, command)
        laser.enabled = True

    def disable(self, laser: Laser) -> None:
        """disables the laser using serial commands.
        See documentation file for command structure.

        Parameters
        ----------
        laser : Laser
            the laser to disable

        """
        command = "(param-set! '" + laser.serial_id + ":enable #f)\r"
        utils.write_serial_command(self.serial_connection, command)
        laser.enabled = True

    def emission_on(self, laser: Laser) -> None:
        """turn on the laser

        Parameters
        ----------
        laser : Laser
            the laser to turn on
        """
        command = "(param-set! '" + laser.serial_id + ":cw #t)\r"
        utils.write_serial_command(self.serial_connection, command)

    def emission_off(self, laser: Laser) -> None:
        """turn off the laser

        Parameters
        ----------
        laser : Laser
            the laser to turn off
        """
        command = "(param-set! '" + laser.serial_id + ":cw #f)\r"
        utils.write_serial_command(self.serial_connection, command)
