"""Module for the Basler fluorescence detector."""
import sys

import numpy as np

from pypylon import pylon
from piescope.lm import structured


class Basler():
    """Class for the Basler detector"""
    def __init__(self):
        super(Basler, self).__init__()
        self.camera = pylon.InstantCamera(
            pylon.TlFactory.GetInstance().CreateFirstDevice())
        print("Using device ", self.camera.GetDeviceInfo().GetModelName())
        self.camera.MaxNumBuffer = 5
        self.imageCount = 1
        self.currentImageIndex = 0
        self.image = []
        self.camera_pin = 'P03'

    def camera_grab(self, exposure_time=None, trigger_mode='software', flip_image=True, laser_name=None):
        """Grab a new image from the Basler detector.

        Parameters
        ----------
        exposure_time : int
            Exposure time, in microseconds (us).
        trigger_mode : str
            Trigger mode.
            Available values are "software", "hardware"
        flip_image : bool, optional
            Whether to flip images, by default True
        laser_name : str
            Name of laser to use in live imaging.
            Available values are "laser640", "laser561", "laser488", "laser405"

        Returns
        -------
        self.image : numpy array
        """
        self.camera.Open()
        self.camera.StopGrabbing()

        if laser_name is not None:
            LASER_TO_PIN = {"laser640": 'P10',
                            "laser561": 'P05',
                            "laser488": 'P12',
                            "laser405": 'P13',
                            }
            laser_pin = LASER_TO_PIN[laser_name]

        if trigger_mode is 'software':
            self.camera.TriggerMode.SetValue('Off')
            self.camera.ExposureMode.SetValue('Timed')
            if exposure_time is not None:
                try:
                    self.camera.ExposureTime.SetValue(float(exposure_time))
                except Exception as e:
                    try:
                        self.camera.ExposureTimeAbs.SetValue(float(exposure_time))
                    except Exception as e:
                        self.camera.Close()
                        raise e
        elif trigger_mode is 'hardware':
            self.camera.TriggerMode.SetValue('On')
            self.camera.TriggerSource.SetValue('Line4')
            self.camera.ExposureMode.SetValue('TriggerWidth')
            self.camera.AcquisitionFrameRateEnable.SetValue(False)
        else:
            raise ValueError('Select "software" or "hardware"')

        self.camera.StopGrabbing()
        self.camera.StartGrabbingMax(self.imageCount)
        self.image = []

        while self.camera.IsGrabbing():
            if trigger_mode is 'hardware':
                structured.multi_line_pulse(exposure_time, self.camera_pin, laser_pin)

            grabResult = self.camera.RetrieveResult(
                5000, pylon.TimeoutHandling_ThrowException)

            if grabResult.GrabSucceeded():
                self.image = grabResult.Array
            else:
                raise RuntimeError("Error: " + grabResult.ErrorCode + '\n' +
                                   grabResult.ErrorDescription
                                   )
            grabResult.Release()
        self.camera.Close()
        if flip_image is True:
            self.image = np.flipud(self.image)
        return self.image

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
