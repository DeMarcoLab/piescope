"""Module for the Basler fluorescence detector."""

from pypylon import pylon


class Basler():
    """Class for each Basler fluorescence detector camera instance"""
    def __init__(self):
        """Initialise camera settings"""
        super(Basler, self).__init__()
        self.camera = pylon.InstantCamera(
            pylon.TlFactory.GetInstance().CreateFirstDevice())
        print("Using device ", self.camera.GetDeviceInfo().GetModelName())
        self.camera.MaxNumBuffer = 1

    def get_frame(self):
        """Grab a single frame from Basler fluorescence detector"""
        self.camera.StartGrabbingMax(1)
        while self.camera.IsGrabbing():
            grabResult = self.camera.RetrieveResult(
                5000)
            if grabResult.GrabSucceeded():
                image = grabResult.Array
            else:
                print("Warning: ", grabResult.Errorcode,
                      grabResult.ErrorDescription)
            grabResult.Release()
        return image

# TODO: non-blocking live imaging
# def live_image():
#     pass
