import logging
import time

from piescope.lm import objective, laser, detector

logger = logging.getLogger(__name__)

# Assume minimum 0.5 microns per step maximum 300 microns total height

time_delay = 1
count_max = 5
threshold = 5


def volume_acquisition(main_gui, exposure_time, laser_dict, no_z_slices,
                       z_slice_distance):

    total_volume_height = (int(no_z_slices)-1)*int(z_slice_distance)
    logger.debug('Total height is: %s' % str(total_volume_height) + '\n')
    logger.debug('Number of slices is: %s' % no_z_slices + '\n')
    logger.debug('Distance between slices is: %s' % z_slice_distance + '\n')

    stage_controller = objective.StageController()

    lasers = laser.initialize_lasers()
    logger.debug('Lasers successfully initialised \n')

    basler_detector = detector.Basler()
    logger.debug('Successfully connected to detector \n')

    initial_position = str(get_position(stage_controller))
    logger.debug("Initial position is: %s \n" % initial_position)

    stage_controller.move_relative(int(total_volume_height/2))
    print('Moved to top of volume')

    position = str(get_position(stage_controller))
    print("Top of volume is located at: %s \n" % position)
    time.sleep(time_delay)

    loop_range = int(no_z_slices)
    print("Loop range is: {}".format(loop_range))

    for z_slice in range(0, loop_range):
        count = 0
        for las, power in laser_dict.items():
            print("laser: {}".format(las))
            print("power: {}".format(power))
            lasers[las].enable()
            print('%s is now enabled' % las)

            lasers[las].laser_power = int(power)
            print(' %s power is %s' % (las, power))

            lasers[las].emission_on()
            logger.debug('%s now emitting' % las)

            if las == 'laser561':
                basler_detector.camera.ExposureTime.SetValue(exposure_time)
                logger.debug('Exposure time is: {}'.format(
                    basler_detector.camera.ExposureTime.GetValue()))
            else:
                basler_detector.camera.ExposureTime.SetValue(exposure_time)
                message = 'Exposure time is: {}'.format(
                    basler_detector.camera.ExposureTime.GetValue())
                logger.debug(message)
                main_gui.current_image = basler_detector.camera_grab()
            main_gui.array_list = main_gui.current_image

            lasers[las].emission_off()
            time.sleep(1)
            logger.debug('%s stopped emitting' % las)

            main_gui.string_list = ['Volume_image_' + str(z_slice+1)
                                + '_of_' + str(loop_range) + las]
            main_gui.update_display()

            main_gui.save_image()

            lasers[las].disable()
            print('%s now disabled' % las)

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

        while count < count_max and \
            (difference > threshold or difference < -threshold):

            stage_controller.move_relative(-int(difference))

            position = float(get_position(stage_controller))
            difference = position - target_position
            logger.debug('Difference is: %s' % str(difference))

            count = count + 1

    stage_controller.move_relative(int(total_volume_height/2))


def get_position(stage):
    time.sleep(time_delay)
    position = stage.current_position()
    return position
