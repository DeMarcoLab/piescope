"""Module for the Basler fluorescence detector."""

from pypylon import pylon

class Basler():
    def __init__(self):
        super(Basler, self).__init__()
        self.camera = pylon.InstantCamera(
            pylon.TlFactory.GetInstance().CreateFirstDevice())
        print("Using device ", self.camera.GetDeviceInfo().GetModelName())
        self.camera.MaxNumBuffer = 1
        self.imageCount = 1
        self.currentImageIndex = 0
        self.imageList = []

    def get_frame(self):
        self.camera.StartGrabbingMax(self.imageCount)
        self.imageList = []
        while self.camera.IsGrabbing():
            grabResult = self.camera.RetrieveResult(
                5000, pylon.TimeoutHandling_ThrowException)

            if grabResult.GrabSucceeded():
                print("SizeX: ", grabResult.Width)
                print("SizeY: ", grabResult.Height)
                img = grabResult.Array
                self.imageList.append(img)
                self.currentImageIndex = self.currentImageIndex + 1
                print(img)
                print("Gray value of first pixel: ", img[0, 0])
                print(self.imageList)
            else:
                print("Error: ", grabResult.Errorcode,
                      grabResult.ErrorDescription)
            grabResult.Release()
        return self.imageList

test = Basler()
test2 = test.get_frame()



# TODO: non-blocking live imaging
# def live_image():
#     pass
