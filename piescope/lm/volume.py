from piescope.lm import objective, laser, detector


def volume_aquisition(exposure_time, laser_list, laser_power_list, no_z_slices,
                      z_slice_distance):
    total_height = (no_z_slices-1)*z_slice_distance

    all_lasers = laser.initialize_lasers()
    stage_control = objective.StageController()
    basler_detector = detector.Basler()

    current_pos = stage_control.current_position()
    stage_control.move_relative(total_height/2, 1000)
    stage_control.close()

    for n in range(0, no_z_slices-1):
        for i in range(0, len(laser_list)):
            all_lasers[laser_list[i]-1].enable
            #all_lasers[laser_list[i]-1].set_laser_power
            all_lasers[laser_list[i]-1].emit
            current_image = basler_detector.grab_frame()
            #save this image
            all_lasers[laser_list[i]-1].disable


        stage_control.move_relative(-z_slice_distance)
        stage_control.current_position()
    stage_control.move_relative(total_height/2, 1000)
    stage_control.current_position()
