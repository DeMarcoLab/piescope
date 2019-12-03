import logging
import time
import numpy as np

import piescope

logger = logging.getLogger(__name__)


def volume_acquisition(laser_dict, num_z_slices, z_slice_distance, destination,
                       time_delay=1, count_max=5, threshold=5):
    """Acquire an image volume using the fluorescence microscope.

    Parameters
    ----------
    laser_dict : dict
        Dictionary with structure: {"name": (power, exposure)} with types
        {str: (int, int)}

    num_z_slices : int
        Amount of slices to take for total volume

    z_slice_distance : int
        Distance in nm between each z slice

    destination : str
        Path to save location for images taken during volume acquisition

    time_delay : int, optional
        Pause after moving to the top of the imaging volume, by default 1

    count_max : int, optional
        Maximum number of attempts to move the stage to its target position.
        By default 5

    threshold : int, optional
        Threshold cutoff for deciding whether the current stage position
        is close enough to the target position. Must be a positive number.
        By default 5

    Returns
    -------
    volume : multidimensional numpy array
        numpy.ndarray with shape (z_slices, columns, rows, channels)

    Notes
    -----
    It's good to assume a minimum of 0.5 microns per step,
    and a maximum 300 microns total height for the volume acquisition.
    """
    num_z_slices = int(num_z_slices)
    z_slice_distance = int(z_slice_distance)
    total_volume_height = (num_z_slices - 1) * z_slice_distance

    # Initialize hardware
    objective_stage = piescope.lm.objective.StageController()
    lasers = piescope.lm.laser.initialize_lasers()
    detector = piescope.lm.detector.Basler()
    for laser_name, (laser_power, exposure_time) in laser_dict.items():
        lasers[laser_name].laser_power = laser_power

    # Move objective lens stage to the top of the volume
    original_center_position = str(objective_stage.current_position())
    objective_stage.move_relative(int(total_volume_height / 2))
    time.sleep(time_delay)  # Pause to be sure movement is completed
    logger.debug('Objective lens stage moved to top of the image volume.')

    # Create volume array to put the results into
    array_shape = np.shape(detector.camera_grab())  # no lasers on
    volume = np.ndarray(dtype=np.uint8,
        shape=(num_z_slices, array_shape[0], array_shape[1], len(laser_dict)))

    # Acquire volume image
    for z_slice in range(int(num_z_slices)):
        for channel, (laser_name, (laser_power, exposure_time)) in enumerate(laser_dict.items()):
            # Take an image
            lasers[laser_name].emission_on()
            volume[z_slice, :, :, channel] = detector.camera_grab(exposure_time)
            lasers[laser_name].emission_off()

            # Move objective lens stage
            target_position = (float(original_center_position)
                               + float(total_volume_height / 2.)
                               - (float(z_slice) * float(z_slice_distance))
                               )
            objective_stage.move_relative(-int(z_slice_distance))
            time.sleep(time_delay)  # Pause to be sure movement is completed.
            # If objective stage movement not accurate enough, try it again
            count = 0
            current_position = float(objective_stage.current_position())
            difference = current_position - target_position
            while count < count_max and abs(difference) > threshold:
                objective_stage.move_relative(-int(difference))
                time.sleep(time_delay)  # Pause to be sure movement completed.
                current_position = float(objective_stage.current_position())
                difference = current_position - target_position
                logger.debug('Difference is: {}'.format(str(difference)))
                count = count + 1

    # Finally, return the objective lens stage too original position
    objective_stage.move_absolute(original_center_position)

    return volume
