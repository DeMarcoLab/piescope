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
