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

    total_volume_height = (int(no_z_slices)-1)*int(z_slice_distance)
    print('Total height is: %s' % str(total_volume_height) + '\n')
    print('Number of slices is: %s' % no_z_slices + '\n')
    print('Distance between slices is: %s' % z_slice_distance + '\n')

    stage_controller = objective.StageController()
    stage_controller.initialise_system_parameters(0, 0, 0, 0)
    print('Stage controller successfully initialised \n')

    lasers = laser.initialize_lasers()
    print('Lasers successfully initialised \n')

    basler_detector = detector.Basler()
    print('Successfully connected to detector \n')

    initial_position = str(get_position(stage_controller))
    print("Initial position is: %s \n" % initial_position)

    stage_controller.move_relative(int(total_volume_height/2))
    position = str(get_position(stage_controller))
    print("Top of volume is located at: %s \n" % position)

    for z_slice in range(1, no_z_slices):

        count = 0

        for las, power in laser_dict.items():
            lasers[las].enable()

            print('%s is now enabled' % las)

            lasers[las].laser_power = power
            print(' %s power is %s' % (las, power))

            lasers[las].emit()
            print('%s now emitting' % las)

            current_image = basler_detector.camera_grab()

            inout.save_image(current_image, DEFAULT_PATH)

            lasers[laser].disable()
            print('%s now disabled' % las)

        target_position = int(initial_position) + \
            (int(total_volume_height/2)) - int((z_slice * z_slice_distance))
        print('Target position is: %s" % str(target_position))')

        stage_controller.move_relative(-z_slice_distance)
        position = int(get_position(stage_controller))

        difference = position - target_position
        print('Difference is: %s' % str(difference))

        while count < count_max and \
                (difference > threshold or difference < -threshold):
            #
            stage_controller.move_relative(-difference)
            #
            position = int(get_position(stage_controller))
            difference = position - target_position
            print('Difference is: %s' % str(difference))
            #
            count = count + 1
            print(count)

    stage_controller.move_relative(int(total_volume_height/2))


def get_position(stage):
    time.sleep(time_delay)
    position = stage.current_position()
    return position
