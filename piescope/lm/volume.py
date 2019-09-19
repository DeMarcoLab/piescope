from piescope.lm import objective, laser, detector
import time

# Assume minimum 0.5 microns per step maximum 300 microns total height

time_delay = 1
count_max = 5
threshold = 5

DEFAULT_PATH = "C:\\Users\\Admin\\Pictures\\Basler"


def volume_acquisition(self, exposure_time, laser_dict, no_z_slices,
                       z_slice_distance):

    try:
        total_volume_height = (int(no_z_slices)-1)*int(z_slice_distance)
        print('Total height is: %s' % str(total_volume_height) + '\n')
        print('Number of slices is: %s' % no_z_slices + '\n')
        print('Distance between slices is: %s' % z_slice_distance + '\n')
    except:
        print("Error in calculating total volume height.  Possibly caused by "
              "not having ints in the z_slice_distance and no_z_slices fields")
        return

    try:
        stage_controller = objective.StageController()
    except:
        print("Could not connect to stage controller")
        return

    # try:
        # stage_controller.initialise_system_parameters(0, 0, 0, 0)
        # time.sleep(time_delay)
        # print('Stage controller successfully initialised \n')
    # except:
    #     print("Could not initialise stage controller parameters")
    #     return

    try:
        lasers = laser.initialize_lasers()
        print('Lasers successfully initialised \n')
    except:
        print('Could not initialise lasers')
        return

    try:
        basler_detector = detector.Basler()
        print('Successfully connected to detector \n')
    except:
        print('Could not connect to Basler detector')
        return

    try:
        initial_position = str(get_position(stage_controller))
        print("Initial position is: %s \n" % initial_position)
    except:
        print('Could not find initial position of stage')
        return

    try:
        stage_controller.move_relative(int(total_volume_height/2))
        print('Moved to top of volume')
    except:
        print('Could not move stage to top of volume')
        return

    try:
        position = str(get_position(stage_controller))
        print("Top of volume is located at: %s \n" % position)
        time.sleep(time_delay)
    except:
        print('Could not find top of volume position')
        return

    try:
        loop_range = int(no_z_slices)
        print("Loop range is: {}".format(loop_range))
    except ValueError:
        print('no_z_slices incorrect type, please enter an int')

    try:
        for z_slice in range(0, loop_range):

            count = 0

            for las, power in laser_dict.items():
                print("laser: {}".format(las))
                print("power: {}".format(power))
                try:
                    lasers[las].enable()
                    print('%s is now enabled' % las)
                except:
                    print('Could not enable %s' % las)
                    return

                try:
                    lasers[las].laser_power = int(power)
                    print(' %s power is %s' % (las, power))
                except:
                    print('Could not change %s power' % las)
                    return

                try:
                    lasers[las].emission_on()
                    print('%s now emitting' % las)
                except:
                    print('Could not emit %s' % las)
                    return

                try:
                    if las == 'laser561':
                        basler_detector.camera.ExposureTime.SetValue(125000)
                        print('Exposure time is: {}'.format(basler_detector.camera.ExposureTime.GetValue()))
                    else:
                        basler_detector.camera.ExposureTime.SetValue(20000)
                        print('Exposure time is: {}'.format(basler_detector.camera.ExposureTime.GetValue()))
                    self.current_image = basler_detector.camera_grab()
                    self.array_list = self.current_image
                except:
                    print('Could not grab basler image')
                    return

                try:
                    lasers[las].emission_off()
                    time.sleep(1)
                    print('%s stopped emitting' % las)
                except:
                    print('Could not emit %s' % las)
                    return

                try:
                    self.string_list = ['Volume_image_' + str(z_slice+1) + '_of_' + str(loop_range) +
                                        las]
                    self.update_display()
                except:
                    print('Could not update display')
                    return

                try:
                    self.save_image()
                except:
                    print('Could not save image')
                    return

                try:
                    lasers[las].disable()
                    print('%s now disabled' % las)
                except:
                    print('Could not disable %s' % las)
                    return

            try:
                target_position = float(total_volume_height/2.) + float(initial_position)\
                                  - (float(z_slice) * float(z_slice_distance))
                print('Initial position is: {}'.format(initial_position))
                print('Z_slice is: {}'.format(z_slice))
                print('z_slice_distance is: {}'.format(z_slice_distance))

                print('Target position is: %s' % str(target_position))
            except:
                print('Could not calculate target position')
                return

            try:
                stage_controller.move_relative(-int(z_slice_distance))
            except:
                print('Failed to move stage controller by step distance')
                return

            try:
                position = float(get_position(stage_controller))
                print(position)
            except:
                print('Failed to get current position after step movement')
                return

            try:
                difference = position - target_position
                print('Difference is: %s' % str(difference))
            except:
                print('Failed to find difference between desired and current pos')
                return

            while count < count_max and \
                    (difference > threshold or difference < -threshold):
                try:
                    stage_controller.move_relative(-int(difference))
                except:
                    print('Could not move controller by difference')
                    # return

                try:
                    position = float(get_position(stage_controller))
                except:
                    print('Failed to retrieve position after correction')
                    # return

                try:
                    difference = position - target_position
                    print('Difference is: %s' % str(difference))
                except:
                    print('Failed to calculated difference after correction')
                    return

                count = count + 1

    except:
        print("Laser loop error")
        return

    try:
        stage_controller.move_relative(int(total_volume_height/2))
    except:
        print('Could not return stage to middle position')
        return


def get_position(stage):
    time.sleep(time_delay)
    position = stage.current_position()
    return position
