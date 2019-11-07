import numpy as np
from autoscript_sdb_microscope_client.structures import (
    GrabFrameSettings,
    Rectangle,
    RunAutoCbSettings,
)
"""Module for interacting with the FIBSEM using Autoscript."""


def initialize(ip_address='10.0.0.1'):
    """Initialize connection to FIBSEM microscope with Autoscript."""
    from autoscript_sdb_microscope_client import SdbMicroscopeClient
    microscope = SdbMicroscopeClient()
    microscope.connect(ip_address)
    return microscope


def move_to_light_microscope(microscope, x=50.0e-3, y=0.0):
    """Move the sample stage from the FIBSEM to the light microscope.

    Parameters
    ----------
    microscope : Autoscript microscope object.
    x : float, optional
        Relative movement in x to go from the FIBSEM to the light microscope.
        By default positive 50 millimeters in the x-direction.
    y : float, optional
        Relative movement in y to go from the FIBSEM to the light microscope.
        By default this is zero.

    Returns
    -------
    StagePosition
        FIBSEM microscope sample stage position after moving.
        If the returned stage position is called 'stage_pos' then:
        stage_pos.x = the x position of the FIBSEM sample stage (in meters)
        stage_pos.y = the y position of the FIBSEM sample stage (in meters)
        stage_pos.z = the z position of the FIBSEM sample stage (in meters)
        stage_pos.r = the rotation of the FIBSEM sample stage (in radians)
        stage_pos.t = the tilt of the FIBSEM sample stage (in radians)
    """
    from autoscript_sdb_microscope_client.structures import StagePosition
    new_position = StagePosition(x=x, y=y, z=0, r=0, t=0)
    microscope.specimen.stage.relative_move(new_position)
    return microscope.specimen.stage.current_position


def move_to_electron_microscope(microscope, x=-50.0e-3, y=0.0):
    """Move the sample stage from the light microscope to the FIBSEM.

    Parameters
    ----------
    microscope : Autoscript microscope object.
    x : float, optional
        Relative movement in x to go from the light microscope to the FIBSEM.
        By default negative 50 millimeters in the x-direction.
    y : float, optional
        Relative movement in y to go from the light microscope to the FIBSEM.
        By default this is zero.

    Returns
    -------
    StagePosition
        FIBSEM microscope sample stage position after moving.
        If the returned stage position is called 'stage_pos' then:
        stage_pos.x = the x position of the FIBSEM sample stage (in meters)
        stage_pos.y = the y position of the FIBSEM sample stage (in meters)
        stage_pos.z = the z position of the FIBSEM sample stage (in meters)
        stage_pos.r = the rotation of the FIBSEM sample stage (in radians)
        stage_pos.t = the tilt of the FIBSEM sample stage (in radians)
    """
    from autoscript_sdb_microscope_client.structures import StagePosition

    new_position = StagePosition(x=x, y=y, z=0, r=0, t=0)
    microscope.specimen.stage.relative_move(new_position)
    return microscope.specimen.stage.current_position


def new_ion_image(microscope):
    """Take new ion beam image.

    Uses whichever camera settings (resolution, dwell time, etc) are current.

    Parameters
    ----------
    microscope : Autoscript microscope object.

    Returns
    -------
    AdornedImage
        If the returned AdornedImage is named 'image', then:
        image.data = a numpy array of the image pixels
        image.metadata.binary_result.pixel_size.x = image pixel size in x
        image.metadata.binary_result.pixel_size.y = image pixel size in y
    """
    microscope.imaging.set_active_view(2)  # the ion beam view
    image = microscope.imaging.grab_frame()
    return image


def new_electron_image(microscope):
    """Take new electron beam image.

    Uses whichever camera settings (resolution, dwell time, etc) are current.

    Parameters
    ----------
    microscope : Autoscript microscope object.

    Returns
    -------
    AdornedImage
        If the returned AdornedImage is named 'image', then:
        image.data = a numpy array of the image pixels
        image.metadata.binary_result.pixel_size.x = image pixel size in x
        image.metadata.binary_result.pixel_size.y = image pixel size in y
    """
    microscope.imaging.set_active_view(1)  # the electron beam view
    image = microscope.imaging.grab_frame()
    return image


def last_ion_image(microscope):
    """Get the last previously acquired ion beam image.

    Parameters
    ----------
    microscope : Autoscript microscope object.

    Returns
    -------
    AdornedImage
        If the returned AdornedImage is named 'image', then:
        image.data = a numpy array of the image pixels
        image.metadata.binary_result.pixel_size.x = image pixel size in x
        image.metadata.binary_result.pixel_size.y = image pixel size in y
    """
    microscope.imaging.set_active_view(2)  # the ion beam view
    image = microscope.imaging.get_image()
    return image


def last_electron_image(microscope):
    """Get the last previously acquired electron beam image.

    Parameters
    ----------
    microscope : Autoscript microscope object.

    Returns
    -------
    AdornedImage
        If the returned AdornedImage is named 'image', then:
        image.data = a numpy array of the image pixels
        image.metadata.binary_result.pixel_size.x = image pixel size in x
        image.metadata.binary_result.pixel_size.y = image pixel size in y
    """
    microscope.imaging.set_active_view(1)  # the electron beam view
    image = microscope.imaging.get_image()
    return image


def create_rectangular_pattern(microscope, image, x0, x1, y0, y1, depth=1e-6):
    pixelsize_x = image.metadata.binary_result.pixel_size.x
    pixelsize_y = image.metadata.binary_result.pixel_size.y
    image_shape_y, image_shape_x = image.data.shape
    width = (x1-x0) * pixelsize_x #  real space (meters)
    height = (y1-y0) * pixelsize_y # real space (meters)

    center_x_pixels = (x0 + ((x1-x0)/2))
    center_y_pixels = (y0 + ((y1-y0)/2))

    center_x_realspace, center_y_realspace = pixel_to_realspace_coordinate([center_x_pixels, center_y_pixels], image)
    microscope.patterning.create_rectangle(center_x_realspace, center_y_realspace, width, height, depth)


def pixel_to_realspace_coordinate(coord, image):
    """Covert pixel image coordinate to real space coordinate.
    This conversion deliberately ignores the nominal pixel size in y,
    as this can lead to inaccuraccies if the sample is not flat in y.
    Parameters
    ----------
    coord : listlike, float
        In x, y format & pixel units. Origin is at the top left.
    image : AdorrnedImage
        Image the coordinate came from.
    Returns
    -------
    realspace_coord
        xy coordinate in real space. Origin is at the image center.
        Output is in (x, y) format.
    """
    coord = np.array(coord).astype(np.float64)
    y_shape, x_shape = image.data.shape
    pixelsize_x = image.metadata.binary_result.pixel_size.x
    # deliberately don't use the y pixel size, any tilt will throw this off
    coord[1] = y_shape - coord[1]  # flip y-axis for relative coordinate system
    # reset origin to center
    coord -= np.array([x_shape / 2, y_shape / 2]).astype(np.int32)
    realspace_coord = list(np.array(coord) * pixelsize_x)  # to real space
    return realspace_coord


def autocontrast(microscope):
    """Atuomatically adjust the microscope image contrast.
        Parameters
        ----------
        microscope : Autoscript microscope object.
        Returns
        -------
        RunAutoCbSettings
            Automatic contrast brightness settings.
        """
    microscope.imaging.set_active_view(2)
    autocontrast_settings = RunAutoCbSettings(
        method="MaxContrast",
        resolution="768x512",  # low resolution, so as not to damage the sample
        number_of_frames=5,
    )
    # logging.info("Automatically adjusting contrast...")
    microscope.auto_functions.run_auto_cb()
    return autocontrast_settings


def test_numpy():
    return np.random.random((100,200))
