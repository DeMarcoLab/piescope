"""Module for the Basler fluorescence detector."""
import sys

import numpy as np

from pypylon import pylon


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

    def camera_grab(self, exposure_time=None, flip_image=True):
        """Grab a new image from the Basler detector.

        Parameters
        ----------
        exposure_time : int
            Exposure time, in microseconds (us).

        Returns
        -------
        self.image : numpy array
        """
        self.camera.Open()
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

        self.camera.StartGrabbingMax(self.imageCount)
        self.image = []

        while self.camera.IsGrabbing():
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
        """Minimum alloable exposure time."""
        try:
            min_exposure = self.camera.ExposureTime.Min
        except Exception:
            try:
                min_exposure = self.camera.ExposureTimeAbs.Min
            except Exception as e:
                raise e
        return min_exposure

    def maximum_exposure(self):
        """Maximum alloable exposure time."""
        try:
            max_exposure = self.camera.ExposureTime.Max
        except Exception:
            try:
                max_exposure = self.camera.ExposureTimeAbs.Max
            except Exception as e:
                raise e
        return max_exposure