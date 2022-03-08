import logging
import time
import numpy as np

import piescope.lm.detector
import piescope.lm.laser
import piescope.lm.objective
import piescope.lm.structured
import piescope.lm.mirror
from piescope.lm.mirror import StagePosition, StageMacro, ImagingType
from pypylon import pylon

logger = logging.getLogger(__name__)


def acquire_volume(num_z_slices, z_slice_distance, imaging_mode: ImagingType,
laser_controller, mirror_controller, objective_stage, detector, arduino, settings ):
    #TODO: PROPER DOCSTRING, always returns CAZPYX
    time_delay = settings['imaging']['volume']['time_delay']
    angles = settings['imaging']['SIM']['angles']
    phases = settings['imaging']['SIM']['phases']

    total_volume_height = (num_z_slices - 1) * z_slice_distance

    # Move objective lens stage to the top of the volume
    original_center_position = str(objective_stage.current_position())
    objective_stage.move_relative(int(total_volume_height / 2))
    time.sleep(time_delay)  # Pause to be sure movement is completed
    logger.debug('Objective lens stage moved to top of the image volume.')

    # temporarily set power to 0 to get image shape from detector
    temp_power = laser_controller.get_laser_power(laser_controller.current_laser)
    laser_controller.set_laser_power(laser_controller.current_laser, 0.)
    array_shape = np.shape(detector.camera_grab(laser_controller.current_laser, settings))  # no lasers on
    laser_controller.set_laser_power(laser_controller.current_laser, temp_power)
    
    print(f'Lasers: {laser_controller.lasers.values()}')

    volume_enabled_laser_count = 0 
    for laser in laser_controller.lasers.values():
        if laser.volume_enabled:
            volume_enabled_laser_count += 1
    
    
    laser_controller.volume_laser_count = volume_enabled_laser_count
    print(f'volume_enabled_laser_count: {laser_controller.volume_laser_count}')
    
    volume = np.ndarray(dtype=np.uint8,
        shape=(volume_enabled_laser_count, angles, num_z_slices, phases, array_shape[0], array_shape[1]))

    for z_slice in range(num_z_slices):
        if imaging_mode == ImagingType.WIDEFIELD:
            mirror_controller.stopAll()
            mirror_controller.move_to(StagePosition.WIDEFIELD)

            channel = 0
            for laser in laser_controller.lasers.values():
                if laser.volume_enabled:
                    image = detector.camera_grab(laser, settings)
                    volume[channel, 0, z_slice, 0, :, :] = image # (CAZPYX)
                    channel += 1 

        if imaging_mode == ImagingType.SIM:
            slice = grab_slice(laser_controller=laser_controller, detector=detector,
            settings=settings, mirror_controller=mirror_controller, arduino=arduino)

            slice_reshaped = np.array(slice).reshape(volume_enabled_laser_count, angles, phases, array_shape[0], array_shape[1])
            
            img_index = list(range(len(slice)))
            for channel in range(volume_enabled_laser_count):
                for angle in range(angles):
                    for phase in range(phases):
                        # get the index for each parameters image in the slice
                        # see notebook for details
                        idx = img_index[channel::volume_enabled_laser_count][angle::angles][phase::phases][0]
                        # idx = test[a::N_LASERS][b::N_ANGLES][c::N_PHASES]
                        slice_reshaped[channel, angle, phase] = slice[idx]
            volume[:, :, z_slice, :, :, :] = slice_reshaped  # (CAZPYX)
        
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

        count_max = settings['imaging']['volume']['count_max']
        threshold = settings['imaging']['volume']['threshold']

        while count < count_max and abs(difference) > threshold:
            objective_stage.move_relative(-int(difference))
            time.sleep(time_delay)  # Pause to be sure movement completed.
            current_position = float(objective_stage.current_position())
            difference = current_position - target_position
            logger.debug('Difference is: {}'.format(str(difference)))
            count = count + 1
        piescope.lm.structured.single_line_pulse(100000, 'P04')
        # TODO: add to pins in main

    # Finally, return the objective lens stage too original position
    objective_stage.move_absolute(original_center_position)
    logging.debug("Volume acquired, stage returned to its original position.")
    logging.debug("Volume array shape: {}".format(volume.shape))
    logging.info("Fluorescence volume acquistion finished.")
    return volume

def grab_slice(laser_controller, 
        detector,
        settings: dict,
        mirror_controller,
        arduino,
    ):
        """Grab a slice using Arduino and NI controller"""
        detector.camera.Open()
        detector.camera.LineSelector.SetValue("Line4")
        detector.camera.TriggerMode.SetValue("On")
        detector.camera.TriggerSource.SetValue("Line4")

        detector.camera.ExposureMode.SetValue("TriggerWidth")
        detector.camera.AcquisitionFrameRateEnable.SetValue(False)

        angles = settings['imaging']['SIM']['angles']
        phases = settings['imaging']['SIM']['phases']
        
        detector.camera.MaxNumBuffer = len(laser_controller.lasers) * angles * phases
        detector.camera.StopGrabbing()
        detector.camera.StartGrabbingMax(angles * phases * laser_controller.volume_laser_count)
        images = []

        arduino.send_volume_info(laser_controller=laser_controller)

        mirror_controller.stopAll()
        mirror_controller.start_macro(macro_name=StageMacro.MAIN)

        while detector.camera.IsGrabbing():
            grabResult = detector.camera.RetrieveResult(
                10000, pylon.TimeoutHandling_ThrowException
            )
            if grabResult.GrabSucceeded():
                image = grabResult.Array
                image = np.flipud(image)
                image = np.fliplr(image)
                images.append(image)

            else:
                raise RuntimeError(
                    "Error: "
                    + grabResult.ErrorCode
                    + "\n"
                    + grabResult.ErrorDescription
                )
            grabResult.Release()
        detector.camera.Close()
        return images



def volume_acquisition(laser_dict, num_z_slices, z_slice_distance,
                       time_delay=1, count_max=5, threshold=5, phases=1,
                       angles=1, mode="widefield", detector=None, lasers=None,
                       objective_stage=None, mirror_controller=None, arduino=None, laser_pins=None):
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

    time_delay : int, optional
        Pause after moving to the top of the imaging volume, by default 1

    count_max : int, optional
        Maximum number of attempts to move the stage to its target position.
        By default 5

    threshold : int, optional
        Threshold cutoff for deciding whether the current stage position
        is close enough to the target position. Must be a positive number.
        By default 5

    phases : int, optional
        The number of phases for structured illumination, typically 3.
        Must be a positive number.
        By default 1 for widefield imaging

    angles : int, optional
        The number of angles for structured illumination, typically 3.
        Must be a positive number.
        By default 1 for widefield imaging

    mode : str
        Imaging mode, by default widefield.
        Possible values are "widefield" and "sim".

    detector : piescope.lm.detector.Basler(), optional
        Fluorescence detector class instance.
        Default value is None.

    lasers : piescope.lm.lasers.Laser(), optional
        Lasers.
        Default value is None.

    objective_stage : piescope.lm.objective.StageController(), optional
        Objective lens stage class instance.
        Default value is None.

    mirror_controller : piescope.lm.mirror.PIController(), optional
        Stage controller for structured pattern mirror.
        Default value is None.

    laser_pins : list of str
        Pin names to trigger pins via hardware.
        Individual names passed as 'PXX', with XX being the port and pin number, respectively
        Default values is None.

    Returns
    -------
    volume : multidimensional numpy array
        numpy.ndarray with shape (z_slices, columns, rows, channels)

    Notes
    -----
    It's good to assume a minimum of 0.5 microns per step,
    and a maximum 300 microns total height for the volume acquisition.
    """
    logging.info("Acquiring fluorescence volume...")
    num_z_slices = int(num_z_slices)
    z_slice_distance = int(z_slice_distance)
    total_volume_height = (num_z_slices - 1) * z_slice_distance

    # Initialise hardware
    if detector is None:
        detector = piescope.lm.detector.Basler()
    if lasers is None:
        lasers = piescope.lm.laser.initialise_lasers()
    if objective_stage is None:
        objective_stage = piescope.lm.objective.StageController()
    for laser_name, (laser_power, exposure_time) in laser_dict.items():
        lasers[laser_name].laser_power = laser_power
    if mirror_controller is None:
        mirror_controller = piescope.lm.mirror.PIController()

    # Move objective lens stage to the top of the volume
    original_center_position = str(objective_stage.current_position())
    objective_stage.move_relative(int(total_volume_height / 2))
    time.sleep(time_delay)  # Pause to be sure movement is completed
    logger.debug('Objective lens stage moved to top of the image volume.')

    if mode != 'widefield':
        angles = 3
        phases = 3

    # Create volume array to put the results into
    array_shape = np.shape(detector.camera_grab())  # no lasers on
    volume = np.ndarray(dtype=np.uint8,
        shape=(len(laser_dict), angles, num_z_slices, phases, array_shape[0], array_shape[1]))

    # Acquire volume image
    # For each slice
    for z_slice in range(int(num_z_slices)):
        logging.debug("z_slice: {}".format(z_slice))

        if mode == "widefield":
            mirror_controller.stopAll()
            mirror_controller.move_to(StagePosition.WIDEFIELD)
            for channel, (laser_name, (laser_power, exposure_time)) in enumerate(laser_dict.items()):
                print("z_slice: {}, laser: {}".format(z_slice, laser_name))
                logging.debug("laser_name: {}".format(laser_name))

                image = detector.camera_grab(exposure_time, trigger_mode='hardware', laser_name=laser_name, laser_pins=laser_pins)
                image = np.fliplr(image)
                volume[channel, 0, z_slice, 0, :, :] = image  # (CAZPYX)

        else:
            # n_images = angles * phases * len(laser_dict)
            slice = detector.grab_slice(mirror_controller=mirror_controller, arduino=arduino, laser_dict=laser_dict)


            slice_reshaped = np.array(slice).reshape(len(laser_dict), angles, phases, array_shape[0], array_shape[1])
            # assert slice_reshaped.shape == ()

            img_index = list(range(len(slice)))
            for channel in range(len(laser_dict)):
                for angle in range(angles):
                    for phase in range(phases):
                        # get the index for each parameters image in the slice
                        # see notebook for details
                        idx = img_index[channel::len(laser_dict)][angle::angles][phase::phases][0]
                        # idx = test[a::N_LASERS][b::N_ANGLES][c::N_PHASES]
                        slice_reshaped[channel, angle, phase] = slice[idx]

            # Channel, then phase, then angle
            volume[:, :, z_slice, :, :, :] = slice_reshaped  # (CAZPYX)

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
        piescope.lm.structured.single_line_pulse(100000, 'P04')
        # PO4 IS OBJECTIVE READY PIN

    # Finally, return the objective lens stage too original position
    objective_stage.move_absolute(original_center_position)
    logging.debug("Volume acquired, stage returned to its original position.")
    logging.debug("Volume array shape: {}".format(volume.shape))
    logging.info("Fluorescence volume acquistion finished.")
    return volume
