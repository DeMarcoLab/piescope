import logging

import numpy as np
from piescope.utils import Modality
from autoscript_sdb_microscope_client import SdbMicroscopeClient
from autoscript_sdb_microscope_client.structures import GrabFrameSettings

"""Module for interacting with the FIBSEM using Autoscript."""

def move_to_microscope(microscope: SdbMicroscopeClient, settings: dict):
    from autoscript_sdb_microscope_client.structures import StagePosition
    x, y = settings['system']['relative_lm_position']
    current_position_x = microscope.specimen.stage.current_position.x
    fibsem_min = settings['system']['fibsem_min_position']
    fibsem_max = settings['system']['fibsem_max_position']
    lm_min = settings['system']['lm_min_position']
    lm_max = settings['system']['lm_max_position']
    
    if fibsem_min < current_position_x < fibsem_max:
        logging.info('Under FIBSEM, moving to light microscope')
    elif lm_min < current_position_x < lm_max:
        x = -x
        y = -y
        logging.info('Under light microscope, moving to FIBSEM')
    else:
        raise RuntimeError('Not positioned under the either microscope, cannot move to other microscope')

    new_position = StagePosition(x=x, y=y, z=0, r=0, t=0)
    microscope.specimen.stage.relative_move(new_position)


# def new_ion_image(microscope:SdbMicroscopeClient, settings: GrabFrameSettings = None):
#     """Take new ion beam image.

#     Uses whichever camera settings (resolution, dwell time, etc) are current.

#     Parameters
#     ----------
#     microscope : Autoscript microscope object.

#     Returns
#     -------
#     AdornedImage
#         If the returned AdornedImage is named 'image', then:
#         image.data = a numpy array of the image pixels
#         image.metadata.binary_result.pixel_size.x = image pixel size in x
#         image.metadata.binary_result.pixel_size.y = image pixel size in y
#     """
#     microscope.imaging.set_active_view(2)  # the ion beam view
#     if settings is not None:
#         image = microscope.imaging.grab_frame(settings)
#     else:
#         image = microscope.imaging.grab_frame()
#     return image


# def new_electron_image(microscope, settings=None):
#     """Take new electron beam image.

#     Uses whichever camera settings (resolution, dwell time, etc) are current.

#     Parameters
#     ----------
#     microscope : Autoscript microscope object.

#     Returns
#     -------
#     AdornedImage
#         If the returned AdornedImage is named 'image', then:
#         image.data = a numpy array of the image pixels
#         image.metadata.binary_result.pixel_size.x = image pixel size in x
#         image.metadata.binary_result.pixel_size.y = image pixel size in y
#     """
#     microscope.imaging.set_active_view(1)  # the electron beam view
#     if settings is not None:
#         image = microscope.imaging.grab_frame(settings)
#     else:
#         image = microscope.imaging.grab_frame()
#     return image

# TODO: replace with fibsem.conversions...
# def pixel_to_realspace_coordinate(coord, image):
#     """Covert pixel image coordinate to real space coordinate.

#     This conversion deliberately ignores the nominal pixel size in y,
#     as this can lead to inaccuraccies if the sample is not flat in y.

#     Parameters
#     ----------
#     coord : listlike, float
#         In x, y format & pixel units. Origin is at the top left.

#     image : AdornedImage
#         Image the coordinate came from.

#     Returns
#     -------
#     realspace_coord
#         xy coordinate in real space. Origin is at the image center.
#         Output is in (x, y) format.
#     """
#     coord = np.array(coord).astype(np.float64)
#     if len(image.data.shape) > 2:
#         y_shape, x_shape = image.data.shape[0:2]
#     else:
#         y_shape, x_shape = image.data.shape

#     pixelsize_x = image.metadata.binary_result.pixel_size.x
#     # deliberately don't use the y pixel size, any tilt will throw this off
#     coord[1] = y_shape - coord[1]  # flip y-axis for relative coordinate system
#     # reset origin to center
#     coord -= np.array([x_shape / 2, y_shape / 2]).astype(np.int32)
#     realspace_coord = list(np.array(coord) * pixelsize_x)  # to real space
#     return realspace_coord


# def autocontrast(microscope, view=2):
#     """Automatically adjust the microscope image contrast.

#     Parameters
#     ----------
#     microscope : Autoscript microscope object.

#     Returns
#     -------
#     RunAutoCbSettings
#         Automatic contrast brightness settings.
#     """
#     from autoscript_sdb_microscope_client.structures import RunAutoCbSettings
#     microscope.imaging.set_active_view(view)
#     autocontrast_settings = RunAutoCbSettings(
#         method="MaxContrast",
#         resolution="768x512",  # low resolution, so as not to damage the sample
#         number_of_frames=5,
#     )
#     # logging.info("Automatically adjusting contrast...")
#     microscope.auto_functions.run_auto_cb()
#     return autocontrast_settings


# def update_camera_settings(camera_dwell_time, image_resolution):
#     """Create new FIBSEM camera settings using Austoscript GrabFrameSettings.

#     Parameters
#     ----------
#     camera_dwell_time : float
#         Image acquisition dwell time in seconds.
#     image_resolution : str
#         String describing image resolution. Format is pixel width by height.
#         Common values include:
#             "1536x1024"
#             "3072x2048"
#             "6144x4096"
#             "768x512"
#         The full list of available values may differ between instruments.
#         See microscope.beams.ion_beam.scanning.resolution.available_values

#     Returns
#     -------
#     camera_settings
#         AutoScript GrabFrameSettings object instance.
#     """
#     from autoscript_sdb_microscope_client.structures import GrabFrameSettings
#     camera_settings = GrabFrameSettings(
#         resolution=image_resolution,
#         dwell_time=camera_dwell_time
#     )
#     return camera_settings


# def y_corrected_stage_movement(expected_y, stage_tilt, settings, image):
#     """Stage movement in Y, corrected for tilt of sample surface plane.
#     ----------
#     expected_y : in meters
#     stage_tilt : in radians        Can pass this directly microscope.specimen.stage.current_position.t
#     beam_type : BeamType, optional
#         BeamType.ELECTRON or BeamType.ION
#     Returns
#     -------
#     StagePosition
#         Stage position to pass to relative movement function.
#     """
#     from autoscript_sdb_microscope_client.structures import StagePosition
#     beam_type = image.metadata.acquisition.beam_type
#     if settings["system"]["pretilt"] == 0:
#         return StagePosition(x=0, y=expected_y, z=0)
#     if beam_type == 'Ion':
#         tilt_adjustment = np.deg2rad(settings["imaging"]["ib"]["relative_angle"] - settings['system']['pretilt'])
#     elif beam_type == 'Electron':
#         tilt_adjustment = np.deg2rad(-settings['system']['pretilt'])
#     else:
#         raise ValueError('Beam type of image not found')
#     tilt_radians = stage_tilt + tilt_adjustment
#     y_move = +np.cos(tilt_radians) * expected_y
#     z_move = -np.sin(tilt_radians) * expected_y
#     logging.info(f"drift correction: the corrected Y shift is {y_move:.3e} meters")
#     logging.info(f"drift correction: the corrected Z shift is  {z_move:.3e} meters")
#     return StagePosition(x=0, y=y_move, z=z_move)
