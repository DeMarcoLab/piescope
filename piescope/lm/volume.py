import logging
import time

from piescope.lm import objective, laser, detector

logger = logging.getLogger(__name__)

# Assume minimum 0.5 microns per step maximum 300 microns total height

time_delay = 1
count_max = 5
threshold = 5


def volume_acquisition(self, exposure_time, laser_dict, no_z_slices,
                       z_slice_distance):

    try:
        total_volume_height = (int(no_z_slices)-1)*int(z_slice_distance)
        logger.debug('Total height is: %s' % str(total_volume_height) + '\n')
        logger.debug('Number of slices is: %s' % no_z_slices + '\n')
        logger.debug('Distance between slices is: %s' % z_slice_distance + '\n')
    except Exception as e:
        message = "Error in calculating total volume height.  Possibly due to"\
                 " not having ints in z_slice_distance and no_z_slices fields"
        logger.error(e)
        logger.error(message)
        return
    try:
        stage_controller = objective.StageController()
    except Exception as e:
        message = "Could not connect to stage controller"
        logger.error(e)
        logger.error(message)
        return

    try:
        lasers = laser.initialize_lasers()
        logger.debug('Lasers successfully initialised \n')
    except Exception as e:
        message = 'Could not initialise lasers'
        logger.error(e)
        logger.error(message)
        return

    try:
        basler_detector = detector.Basler()
        logger.debug('Successfully connected to detector \n')
    except Exception as e:
        message = 'Could not connect to Basler detector'
        logger.error(e)
        logger.error(message)
        return

    try:
        initial_position = str(get_position(stage_controller))
        logger.debug("Initial position is: %s \n" % initial_position)
    except Exception as e:
        message = 'Could not find initial position of stage'
        logger.error(e)
        logger.error(message)
        return

    try:
        stage_controller.move_relative(int(total_volume_height/2))
        print('Moved to top of volume')
    except Exception as e:
        message = 'Could not move stage to top of volume'
        logger.error(e)
        logger.error(message)
        return

    try:
        position = str(get_position(stage_controller))
        print("Top of volume is located at: %s \n" % position)
        time.sleep(time_delay)
    except Exception as e:
        message = 'Could not find top of volume position'
        logger.error(e)
        logger.error(message)
        return

    try:
        loop_range = int(no_z_slices)
        print("Loop range is: {}".format(loop_range))
    except ValueError:
        message = 'no_z_slices incorrect type, please enter an int'
        logger.error(e)
        logger.error(message)
        return

    try:
        for z_slice in range(0, loop_range):
            count = 0
            for las, power in laser_dict.items():
                print("laser: {}".format(las))
                print("power: {}".format(power))
                try:
                    lasers[las].enable()
                    print('%s is now enabled' % las)
                except Exception as e:
                    message = 'Could not enable %s' % las
                    logger.error(e)
                    logger.error(message)
                    return

                try:
                    lasers[las].laser_power = int(power)
                    print(' %s power is %s' % (las, power))
                except Exception as e:
                    message = 'Could not change %s power' % las
                    logger.error(e)
                    logger.error(message)
                    return

                try:
                    lasers[las].emission_on()
                    logger.debug('%s now emitting' % las)
                except Exception as e:
                    message = 'Could not emit %s' % las
                    logger.error(e)
                    logger.error(message)
                    return

                try:
                    if las == 'laser561':
                        basler_detector.camera.ExposureTime.SetValue(125000)
                        logger.debug('Exposure time is: {}'.format(
                            basler_detector.camera.ExposureTime.GetValue()))
                    else:
                        basler_detector.camera.ExposureTime.SetValue(20000)
                        message = 'Exposure time is: {}'.format(
                            basler_detector.camera.ExposureTime.GetValue())
                        logger.debug(message)
                        self.current_image = basler_detector.camera_grab()
                    self.array_list = self.current_image
                except Exception as e:
                    message = 'Could not grab basler image'
                    logger.error(e)
                    logger.error(message)
                    return

                try:
                    lasers[las].emission_off()
                    time.sleep(1)
                    logger.debug('%s stopped emitting' % las)
                except Exception as e:
                    message = 'Could not emit %s' % las
                    logger.error(e)
                    logger.error(message)
                    return

                try:
                    self.string_list = ['Volume_image_' + str(z_slice+1)
                                        + '_of_' + str(loop_range) + las]
                    self.update_display()
                except Exception as e:
                    message = 'Could not update display'
                    logger.error(e)
                    logger.error(message)
                    return

                try:
                    self.save_image()
                except Exception as e:
                    message = 'Could not save image'
                    logger.error(e)
                    logger.error(message)
                    return

                try:
                    lasers[las].disable()
                    print('%s now disabled' % las)
                except Exception as e:
                    message = 'Could not disable %s' % las
                    logger.error(e)
                    logger.error(message)
                    return

            try:
                target_position = float(total_volume_height/2.) \
                                  + float(initial_position) \
                                  - (float(z_slice) * float(z_slice_distance))
                logger.debug('Initial position is: {}'.format(initial_position))
                logger.debug('Z_slice is: {}'.format(z_slice))
                logger.debug('z_slice_distance is: {}'.format(z_slice_distance))
                logger.debug('Target position is: %s' % str(target_position))
            except Exception as e:
                message = 'Could not calculate target position'
                logger.error(e)
                logger.error(message)
                return

            try:
                stage_controller.move_relative(-int(z_slice_distance))
            except Exception as e:
                message = 'Failed to move stage controller by step distance'
                logger.error(e)
                logger.error(message)
                return

            try:
                position = float(get_position(stage_controller))
                logger.debug(position)
            except Exception as e:
                message = 'Failed to get current position after step movement'
                logger.error(e)
                logger.error(message)
                return

            try:
                difference = position - target_position
                logger.debug('Difference is: %s' % str(difference))
            except Exception as e:
                message = 'Failed to find diff between desired and current pos'
                logger.error(e)
                logger.error(message)
                return

            while count < count_max and \
                    (difference > threshold or difference < -threshold):
                try:
                    stage_controller.move_relative(-int(difference))
                except Exception as e:
                    message = 'Could not move controller by difference'
                    logger.error(e)
                    logger.error(message)
                    return

                try:
                    position = float(get_position(stage_controller))
                except Exception as e:
                    message = 'Failed to retrieve position after correction'
                    logger.error(e)
                    logger.error(message)
                    return

                try:
                    difference = position - target_position
                    logger.debug('Difference is: %s' % str(difference))
                except Exception:
                    message = 'Failed to calculate difference after correction'
                    logger.error(e)
                    logger.error(message)
                    return

                count = count + 1

    except Exception as e:
        logger.error(e)
        logger.error("Laser loop error")
        return

    try:
        stage_controller.move_relative(int(total_volume_height/2))
    except Exception as e:
        message = 'Could not return stage to middle position'
        logger.error(e)
        logger.error(message)
        return


def get_position(stage):
    time.sleep(time_delay)
    position = stage.current_position()
    return position
