import logging
import time
import numpy as np

from piescope.lm import objective, laser, detector

logger = logging.getLogger(__name__)

# Assume minimum 0.5 microns per step maximum 300 microns total height

time_delay = 1
count_max = 5
threshold = 5


def volume_acquisition(laser_dict, no_z_slices, z_slice_distance):

    total_volume_height = (int(no_z_slices)-1)*int(z_slice_distance)
    logger.debug('Total height is: %s' % str(total_volume_height) + '\n')
    logger.debug('Number of slices is: %s' % no_z_slices + '\n')
    logger.debug('Distance between slices is: %s' % z_slice_distance + '\n')

    stage_controller = objective.StageController()

    lasers = laser.initialize_lasers()
    logger.debug('Lasers successfully initialised \n')

    basler_detector = detector.Basler()
    logger.debug('Successfully connected to detector \n')
    sizing_image = basler_detector.camera_grab()
    sizing_shape = np.shape(sizing_image)

    volume = np.ndarray(shape=(no_z_slices, sizing_shape[0], sizing_shape[1], len(laser_dict)), dtype=np.int8)

    initial_position = str(get_position(stage_controller))
    logger.debug("Initial position is: %s \n" % initial_position)

    stage_controller.move_relative(int(total_volume_height/2))
    print('Moved to top of volume')

    position = str(get_position(stage_controller))
    print("Top of volume is located at: %s \n" % position)
    time.sleep(time_delay)

    loop_range = int(no_z_slices)
    print("Loop range is: {}".format(loop_range))

    # initialise laser powers
    for las, power in laser_dict.items():
        lasers[las].laser_power = int(power[0])
        print(' %s power is %s' % (las, power[0]))

    for z_slice in range(0, loop_range):
        count = 0
        channel = 0
        for las, power in laser_dict.items():
            print("laser: {}".format(las))
            print("power: {}".format(power[0]))
            print("channel: {}".format(channel))
            lasers[las].emission_on()
            logger.debug('%s now emitting' % las)
            basler_detector.camera.Open()
            basler_detector.camera.ExposureTime.SetValue(int(power[1]))
            print("Exposure time set as: {}".format(power[1]))

            logger.debug('Exposure time is: {}'.format(
                    basler_detector.camera.ExposureTime.GetValue()))

            volume[z_slice, :, :, channel] = z_slice*int(power[0])*np.random.rand(1040,1024)#basler_detector.camera_grab()

            lasers[las].emission_off()
            time.sleep(1)
            logger.debug('%s stopped emitting' % las)

            target_position = float(total_volume_height/2.) \
                              + float(initial_position) \
                              - (float(z_slice) * float(z_slice_distance))
            logger.debug('Initial position is: {}'.format(initial_position))
            logger.debug('Z_slice is: {}'.format(z_slice))
            logger.debug('z_slice_distance is: {}'.format(z_slice_distance))
            logger.debug('Target position is: %s' % str(target_position))

            stage_controller.move_relative(-int(z_slice_distance))

            position = float(get_position(stage_controller))
            logger.debug(position)

            difference = position - target_position
            logger.debug('Difference is: %s' % str(difference))

            while count < count_max and difference > threshold or \
                    difference < -threshold:

                stage_controller.move_relative(-int(difference))

                position = float(get_position(stage_controller))
                difference = position - target_position
                logger.debug('Difference is: %s' % str(difference))

                count = count + 1

            channel = channel + 1

    stage_controller.move_relative(int(total_volume_height/2))

    return volume


def get_position(stage):
    time.sleep(time_delay)
    position = stage.current_position()
    return position
