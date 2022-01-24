"""Module for the Basler fluorescence detector."""
import sys

import numpy as np

from pypylon import pylon

import piescope.lm.mirror
from piescope.lm.mirror import StagePosition, StageMacro
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
        self.camera_pin = 'P14'

    def camera_grab(self, exposure_time=None, trigger_mode='software', flip_image=True, laser_name=None, laser_pins=None):
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
        laser_pins : list of str
            Pin names to trigger pins via hardware.
            Individual names passed as 'PXX', with XX being the port and pin number, respectively

        Returns
        -------
        self.image : numpy array
        """
        self.camera.Open()
        self.camera.StopGrabbing()

        if laser_name is not None:
            if laser_pins is not None:
                LASER_TO_PIN = {"laser640": laser_pins[0],
                                "laser561": laser_pins[1],
                                "laser488": laser_pins[2],
                                "laser405": laser_pins[3],
                                }
            else:
                LASER_TO_PIN = {"laser640": 'P00',
                                "laser561": 'P01',
                                "laser488": 'P02',
                                "laser405": 'P03',
                                }
            laser_pin = LASER_TO_PIN[laser_name]

        else:
            # raise ValueError('No laser selected')
            pass
            # TODO: Check this out
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
            # set input
            self.camera.LineSelector.SetValue('Line4')
            self.camera.TriggerMode.SetValue('On')
            self.camera.TriggerSource.SetValue('Line4')

            self.camera.ExposureMode.SetValue('TriggerWidth')
            self.camera.AcquisitionFrameRateEnable.SetValue(False)

            # # set output
            # self.camera.LineSelector.SetValue('Line3')
            # self.camera.LineMode.SetValue('Output')
            # self.camera.LineSource.SetValue('ExposureActive')

        else:
            raise ValueError('Select "software" or "hardware"')

        self.camera.StopGrabbing()
        self.camera.StartGrabbingMax(self.imageCount)
        self.image = []

        while self.camera.IsGrabbing():
            if trigger_mode is 'hardware':
                structured.single_line_pulse(delay=exposure_time, pin=laser_pin)
                # structured.multi_line_pulse(exposure_time, self.camera_pin, laser_pin, 'P27') #TODO remove direct reference to pin 27

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
            self.image = np.fliplr(self.image)
        return self.image

    def grab_slice(self, n_images=9, mirror_controller=None, arduino=None, laser_dict=None, flip_image=True):
        """Grab a slice using Arduino and NI controller"""

        self.camera.Open()
        self.camera.LineSelector.SetValue('Line4')
        self.camera.TriggerMode.SetValue('On')
        self.camera.TriggerSource.SetValue('Line4')

        self.camera.ExposureMode.SetValue('TriggerWidth')
        self.camera.AcquisitionFrameRateEnable.SetValue(False)

        self.camera.MaxNumBuffer = 27
        self.camera.StopGrabbing()
        # self.camera.StartGrabbing(pylon.GrabStrategy_OneByOne)
        self.camera.StartGrabbingMax(n_images*len(laser_dict))
        self.images = []

        arduino.send_volume_info(laser_dict=laser_dict)
        mirror_controller.stopAll()
        mirror_controller.start_macro(macro_name=StageMacro.MAIN)

        while self.camera.IsGrabbing():
            grabResult = self.camera.RetrieveResult(
                5000, pylon.TimeoutHandling_ThrowException)
            if grabResult.GrabSucceeded():
                image = grabResult.Array
                if flip_image is True:
                    image = np.flipud(image)
                    image = np.fliplr(image)
                self.images.append(image)

            else:
                raise RuntimeError("Error: " + grabResult.ErrorCode + '\n' +
                                   grabResult.ErrorDescription)
            grabResult.Release()
        self.camera.Close()
        print(self.images)
        return self.images

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
