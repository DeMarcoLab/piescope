import pytest
pytest.importorskip('pypylon', reason="The pypylon library is not available.")

@pytest.fixture
def dummy_camera(monkeypatch):
    from pypylon import pylon
    monkeypatch.setenv("PYLON_CAMEMU", "1")  # os.environ["PYLON_CAMEMU"] = "1"
    dummy_camera = pylon.InstantCamera(
        pylon.TlFactory.GetInstance().CreateFirstDevice())
    return dummy_camera


def test_grab_frame(dummy_camera):
    from pypylon import pylon
    dummy_camera.StartGrabbingMax(1)
    while dummy_camera.IsGrabbing():
        grabResult = dummy_camera.RetrieveResult(
            5000, pylon.TimeoutHandling_ThrowException)
    assert grabResult.Width == 1024
    assert grabResult.Height == 1040


# def test_get_frame():
#     from pypylon import pylon
#     pass


# TODO: non-blocking live imaging
# def test_live_image():
#     from pypylon import pylon
#     pass
