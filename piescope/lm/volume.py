from piescope.lm import objective, laser, detector
import time


# Assume minimum 0.5 microns per step maximum 300 microns total height

time_delay = 1
count_max = 5
threshold = 5


def volume_acquisition(exposure_time, laser_list, laser_power_list, no_z_slices,
                       z_slice_distance):

    total_volume_height = (no_z_slices-1)*z_slice_distance
    print('Total height is: %s' % str(total_volume_height) + '\n')
    print('Distance between slices is: %s' % str(z_slice_distance) + '\n')

    stage_controller = objective.StageController()
    stage_controller.initialise_system_parameters(0, 0, 0, 0)

    lasers = laser.initialize_lasers()
    print('Lasers successfully initialised \n')

    basler_detector = detector.Basler()
    print('Connected to detector \n')

    initial_position = str(get_position(stage_controller))
    print("Initial position is: %s \n" % initial_position)

    stage_controller.move_relative(int(total_volume_height/2))
    position = str(get_position(stage_controller))
    print("Top of volume is located at: %s \n" % position)

    for z_slice in range(1, no_z_slices):

        count = 0

        for i in range(0, len(laser_list)):
            lasers[laser_list[i]].enable()
            print([laser_list[i]])

            print('Laser %s is now enabled' % str(laser_list[i]))

            lasers[laser_list[i]].laser_power = laser_power_list[i]
            print(laser_power_list[i])
            print('Laser %s power is %s' %
                  (str(laser_list[i]), str(laser_power_list[i])))

            lasers[laser_list[i]].emit()
            print('Laser %s now emitting' % str(laser_list[i]))

            current_image = basler_detector.camera_grab()

            #save this image

            lasers[laser_list[i]].disable()
            print('Laser %s now disabled' % str(laser_list[i]))

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
