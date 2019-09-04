from piescope.lm import objective, laser, detector
import time
import piescope_gui.inputoutput.main as inout


# Assume minimum 0.5 microns per step maximum 300 microns total height

time_delay = 1
count_max = 5
threshold = 5

DEFAULT_PATH = "C:\\Users\\Admin\\Pictures\\Basler"


def volume_acquisition(exposure_time, laser_dict, no_z_slices,
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

    try:
        stage_controller.initialise_system_parameters(0, 0, 0, 0)
        print('Stage controller successfully initialised \n')
    except:
        print("Could not initialise stage controller parameters")
        return

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
    except:
        print('Could not move stage to top of volume')
        return

    try:
        position = str(get_position(stage_controller))
        print("Top of volume is located at: %s \n" % position)
    except:
        print('Could not find top of volume position')
        return

    try:
        loop_range = int(no_z_slices)
    except ValueError:
        print('no_z_slices incorrect type, please enter an int')

    try:
        for z_slice in range(1, loop_range):

            count = 0

            for las, power in laser_dict.items():

                try:
                    lasers[las].enable()
                    print('%s is now enabled' % las)
                except:
                    print('Could not enable %s' % las)
                    return

                try:
                    lasers[las].laser_power = power
                    print(' %s power is %s' % (las, power))
                except:
                    print('Could not change %s power' % las)
                    return

                try:
                    lasers[las].emit()
                    print('%s now emitting' % las)
                except:
                    print('Could not emit %s' % las)
                    return

                try:
                    current_image = basler_detector.camera_grab()
                except:
                    print('Could not grab basler image')
                    return

                try:
                    inout.save_image(current_image, DEFAULT_PATH)
                except:
                    print('Could not save image at %s' % DEFAULT_PATH)
                    return

                try:
                    lasers[laser].disable()
                    print('%s now disabled' % las)
                except:
                    print('Could not disable %s' % las)
                    return

        try:
            target_position = int(initial_position) + \
                (int(total_volume_height/2)) - int((z_slice * z_slice_distance))
            print('Target position is: %s" % str(target_position))')
        except:
            print('Could not calculate target position')
            return

        try:
            stage_controller.move_relative(-z_slice_distance)
        except:
            print('Failed to move stage controller by step distance')
            return

        try:
            position = int(get_position(stage_controller))
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
                stage_controller.move_relative(-difference)
            except:
                print('Could not move controller by difference')
                # return

            try:
                position = int(get_position(stage_controller))
            except:
                print('Failed to retrieve position after correction')
                # return

            try:
                difference = position - target_position
                print('Difference is: %s' % str(difference))
            except:
                print('Failed to calculated difference after correction')
                # return

            count = count + 1
            print(count)

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
