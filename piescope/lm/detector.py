"""Module for the Basler fluorescence detector."""
import numpy as np
import logging 
from piescope.lm import structured
from piescope.lm.laser import Laser
from piescope.lm.mirror import StageMacro
from pypylon import pylon

from piescope.utils import TriggerMode
from enum import Enum, auto

class Basler:
    """Class for the Basler detector"""

    def __init__(self, settings: dict):
        super(Basler, self).__init__()
        self.camera = pylon.InstantCamera(
            pylon.TlFactory.GetInstance().CreateFirstDevice()
        )
        logging.info(f"Using {self.camera.GetDeviceInfo().GetModelName()} for light imaging.")
        self.camera.MaxNumBuffer = settings["imaging"]["lm"]["camera"]["max_num_buffer"]
        self.pixel_size = 5.86e-6 

    def camera_grab(self, laser: Laser, settings: dict) -> np.ndarray:
        """Grabs a single fluorescence image

        Args:
            laser (Laser): the laser to use when taking the image
            settings (dict): settings dictionary

        Raises:
            e: exception
            RuntimeError: times out if takes too long to obtain an image

        Returns:
            np.ndarray: an image of dimension (row, col)
        """
        self.camera.Open()
        self.camera.StopGrabbing()

        trigger_mode = settings["imaging"]["lm"]["trigger_mode"]

        # set software triggering mode settings
        if trigger_mode == TriggerMode.Software:
            self.camera.TriggerMode.SetValue("Off")
            self.camera.ExposureMode.SetValue("Timed")
            try:
                self.camera.ExposureTime.SetValue(float(laser.exposure_time))
            except Exception as e:
                try:
                    self.camera.ExposureTimeAbs.SetValue(float(laser.exposure_time))
                except Exception as e:
                    self.camera.Close()
                    raise e

        # set hardware triggering mode settings
        if trigger_mode == TriggerMode.Hardware:
            self.camera.LineSelector.SetValue("Line4")
            self.camera.TriggerMode.SetValue("On")
            self.camera.TriggerSource.SetValue("Line4")

            self.camera.ExposureMode.SetValue("TriggerWidth")
            self.camera.AcquisitionFrameRateEnable.SetValue(False)

        # take images
        self.camera.StartGrabbingMax(1)
        image = None

        while self.camera.IsGrabbing():
            if trigger_mode is TriggerMode.Hardware:
                structured.single_line_pulse(delay=laser.exposure_time, pin=laser.pin)

            grabResult = self.camera.RetrieveResult(
                10000, pylon.TimeoutHandling_ThrowException
            )

            if grabResult.GrabSucceeded():
                image = grabResult.Array
            else:
                raise RuntimeError(
                    "Error: "
                    + grabResult.ErrorCode
                    + "\n"
                    + grabResult.ErrorDescription
                )
            grabResult.Release()

        self.camera.Close()
        image = np.flipud(image)
        image = np.fliplr(image)
        return image


    def minimum_exposure(self):
        """Minimum allowable exposure time."""
        try:
            min_exposure = self.camera.ExposureTime.Min
        except Exception:
            try:
                min_exposure = self.camera.ExposureTimeAbs.Min
            except Exception as e:
                raise e
        return min_exposure

    def maximum_exposure(self):
        """Maximum allowable exposure time."""
        try:
            max_exposure = self.camera.ExposureTime.Max
        except Exception:
            try:
                max_exposure = self.camera.ExposureTimeAbs.Max
            except Exception as e:
                raise e
        return max_exposure
