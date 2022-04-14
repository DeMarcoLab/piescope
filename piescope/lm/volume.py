import logging
import time
import numpy as np

import piescope.lm.detector
import piescope.lm.laser
from piescope.lm.laser import LaserController
import piescope.lm.objective
from piescope.lm.objective import StageController
from piescope.lm.detector import Basler
from piescope.lm.arduino import Arduino
import piescope.lm.structured
import piescope.lm.mirror
from piescope.lm.mirror import PIController, MirrorPosition, StageMacro, ImagingType
from pypylon import pylon

logger = logging.getLogger(__name__)


def acquire_volume(
    num_z_slices: int,
    z_slice_distance: float,
    imaging_type: ImagingType,
    laser_controller: LaserController,
    mirror_controller: PIController,
    objective_stage: StageController,
    detector: Basler,
    arduino: Arduino,
    settings: dict,
):
    """acquires a volume through hardware triggering.

    Args:
        num_z_slices (int): number of slices in the volume
        z_slice_distance (float): distance between each slice
        imaging_type (ImagingType): mode of imaging (options are widefield and SIM)
        laser_controller (LaserController): Laser Controller
        mirror_controller (PIController): Mirror Controller
        objective_stage (StageController): Objective Stage Controller
        detector (Basler): Basler Detector
        arduino (Arduino): Arduino
        settings (dict): configuration settings of the user interface

    Returns:
        np.ndarray: volume stack of images, always 6 dimensional (CAZPYX)
    """
    time_delay = settings["imaging"]["volume"]["time_delay"]
    if imaging_type != ImagingType.WIDEFIELD:
        angles = settings["imaging"]["SIM"]["angles"]
        phases = settings["imaging"]["SIM"]["phases"]
    else:
        angles = 1
        phases = 1

    total_volume_height = (num_z_slices - 1) * z_slice_distance

    # Move objective lens stage to the top of the volume
    original_center_position = str(objective_stage.current_position())
    objective_stage.move_relative(int(total_volume_height / 2))
    time.sleep(time_delay)  # Pause to be sure movement is completed
    logger.debug("Objective lens stage moved to top of the image volume.")

    # temporarily set power to 0 to get image shape from detector
    temp_power = laser_controller.get_laser_power(laser_controller.current_laser)
    laser_controller.set_laser_power(laser_controller.current_laser, 0.0)
    array_shape = np.shape(
        detector.camera_grab(laser_controller.current_laser, settings)
    )  # no lasers on
    laser_controller.set_laser_power(laser_controller.current_laser, temp_power)

    # logging.info(f"Lasers: {laser_controller.lasers.values()}")

    volume_enabled_laser_count = 0
    for laser in laser_controller.lasers.values():
        if laser.volume_enabled:
            volume_enabled_laser_count += 1

    laser_controller.volume_laser_count = volume_enabled_laser_count
    logging.info(f"volume_enabled_laser_count: {laser_controller.volume_laser_count}")

    volume = np.ndarray(
        dtype=np.uint8,
        shape=(
            volume_enabled_laser_count,
            angles,
            num_z_slices,
            phases,
            array_shape[0],
            array_shape[1],
        ),
    )

    for z_slice in range(num_z_slices):
        if imaging_type == ImagingType.WIDEFIELD:
            mirror_controller.stopAll()
            mirror_controller.move_to(MirrorPosition.WIDEFIELD)

            channel = 0
            for laser in laser_controller.lasers.values():
                if laser.volume_enabled:
                    image = detector.camera_grab(laser, settings)
                    volume[channel, 0, z_slice, 0, :, :] = image  # (CAZPYX)
                    channel += 1

        if imaging_type == ImagingType.SIM:
            slice = grab_slice(
                laser_controller=laser_controller,
                detector=detector,
                settings=settings,
                mirror_controller=mirror_controller,
                arduino=arduino,
            )

            # CPAYX
            slice_reshaped = np.array(slice).reshape(
                volume_enabled_laser_count,
                phases,
                angles,
                array_shape[0],
                array_shape[1],
            )

            # CPAYX
            img_index = list(range(len(slice)))
            for channel in range(volume_enabled_laser_count):
                for phase in range(phases):
                    for angle in range(angles):
                        # get the index for each parameters image in the slice
                        # see notebook for details
                        idx = img_index[channel::volume_enabled_laser_count][
                            phase::phases
                        ][angle::angles][0]
                        # idx = test[a::N_LASERS][b::N_ANGLES][c::N_PHASES]
                        slice_reshaped[channel, phase, angle] = slice[idx]
            volume[:, :, z_slice, :, :, :] = slice_reshaped  # (CPZAYX)

            # Move objective lens stage
        target_position = (
            float(original_center_position)
            + float(total_volume_height / 2.0)
            - (float(z_slice) * float(z_slice_distance))
        )
        objective_stage.move_relative(-int(z_slice_distance))
        time.sleep(time_delay)  # Pause to be sure movement is completed.
        # If objective stage movement not accurate enough, try it again
        count = 0
        current_position = float(objective_stage.current_position())
        difference = current_position - target_position

        count_max = settings["imaging"]["volume"]["count_max"]
        threshold = settings["imaging"]["volume"]["threshold"]

        while count < count_max and abs(difference) > threshold:
            objective_stage.move_relative(-int(difference))
            time.sleep(time_delay)  # Pause to be sure movement completed.
            current_position = float(objective_stage.current_position())
            difference = current_position - target_position
            logger.debug("Difference is: {}".format(str(difference)))
            count = count + 1
        piescope.lm.structured.single_line_pulse(100000, settings["imaging"]["volume"]["slice_interrupt_pin"])


    # Finally, return the objective lens stage too original position
    objective_stage.move_absolute(original_center_position)
    logging.debug("Volume acquired, stage returned to its original position.")
    logging.debug("Volume array shape: {}".format(volume.shape))
    logging.info("Fluorescence volume acquistion finished.")
    return volume


def grab_slice(
    laser_controller,
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

    angles = settings["imaging"]["SIM"]["angles"]
    phases = settings["imaging"]["SIM"]["phases"]

    detector.camera.MaxNumBuffer = len(laser_controller.lasers) * angles * phases
    detector.camera.StopGrabbing()
    detector.camera.StartGrabbingMax(
        angles * phases * laser_controller.volume_laser_count
    )
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
                "Error: " + grabResult.ErrorCode + "\n" + grabResult.ErrorDescription
            )
        grabResult.Release()
    detector.camera.Close()
    # CPAYX
    return images
