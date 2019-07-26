from piescope.lm import objective, laser, detector
import time

def volume_acquisition(exposure_time, laser_list, laser_power_list, no_z_slices,
                      z_slice_distance):
    total_height = (no_z_slices-1)*z_slice_distance

    # all_lasers = laser.initialize_lasers()
    print("Lasers initialised")
    stage_control = objective.StageController()
    print(stage_control)
    basler_detector = detector.Basler()
    stage_control.initialise_system_parameters()
    time.sleep(1)
    stage_control.current_position()

    print("Total height is: %s" % str(total_height))
    print("Distance between slices is: %s" % str(z_slice_distance))
    stage_control.current_position()

    print(total_height/2)

    stage_control.move_relative(int(total_height/2), 2000)
    time.sleep(1)
    stage_control.current_position()

    for n in range(1, no_z_slices):
        for i in range(0, len(laser_list)):
            # all_lasers[laser_list[i]-1].enable
            # print("Laser %s now enabled" % str(laser_list[i]))
            #all_lasers[laser_list[i]-1].set_laser_power
            # print("Laser power is now %s" % str(laser_power_list[i]))
            # # all_lasers[laser_list[i]-1].emit
            # print("Laser %s now emitting" % str(laser_list[i]))
            # current_image = basler_detector.grab_frame()
            print("Image taken")
            # save this image
            # print("Image saved")
            # # all_lasers[laser_list[i]-1].disable
            # print("Laser %s now disabled" % str(laser_list[i]))

        expected_pos = int(total_height/2) - n*z_slice_distance
        print("expected step: %s" % str(expected_pos))
        stage_control.move_relative(-z_slice_distance)
        time.sleep(1)
        current_pos = int(stage_control.current_position())
        difference = current_pos - expected_pos
        print("Difference is: %s" % str(difference))
        count = 0
        while count < 5 and (difference > 5 or difference < -5):
            stage_control.move_relative(-difference)
            time.sleep(1)
            current_pos = int(stage_control.current_position())
            difference = current_pos - expected_pos
            print("Difference is: %s" % str(difference))
            count = count + 1
            print(count)

    stage_control.move_relative(int(total_height/2), 2000)
    time.sleep(1)
    stage_control.current_position()


volume_acquisition(1000, [1, 2, 4], [0, 100, 27], 60, 500)
