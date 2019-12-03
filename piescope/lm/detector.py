"""Module for the Basler fluorescence detector."""
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

    def camera_grab(self, exposure_time=None):
        """Grab a new image from the Basler detector.

        Parameters
        ----------
        exposure_time : int
            Exposure time, in microseconds.

        Returns
        -------
        self.image : numpy array
        """
        self.camera.Open()
        self.camera.ExposureMode.SetValue('Timed')
        if exposure_time is not None:
            self.camera.ExposureTimeAbs.SetValue(exposure_time)
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

        return self.image
