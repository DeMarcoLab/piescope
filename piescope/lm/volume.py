from piescope.lm import objective, laser, detector
import time
from PyQt5 import QtWidgets
from piescope_gui import gui_interaction as interaction

# Assume minimum 0.5 microns per step maximum 300 microns total height

time_delay = 1
count_max = 5
threshold = 5


def volume_acquisition(self, exposure_time, laser_dict, no_z_slices,
                       z_slice_distance):

    try:
        total_volume_height = (int(no_z_slices)-1)*int(z_slice_distance)
        print('Total height is: %s' % str(total_volume_height) + '\n')
        print('Number of slices is: %s' % no_z_slices + '\n')
        print('Distance between slices is: %s' % z_slice_distance + '\n')
    except:
        message = "Error in calculating total volume height.  Possibly due to"\
                 " not having ints in z_slice_distance and no_z_slices fields"
        print(message)
        interaction.error_msg(self, message)
        return

    try:
        stage_controller = objective.StageController()
    except:
        message = "Could not connect to stage controller"
        print(message)
        interaction.error_msg(self, message)
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
        message = 'Could not initialise lasers'
        print(message)
        interaction.error_msg(self, message)
        return

    try:
        basler_detector = detector.Basler()
        print('Successfully connected to detector \n')
    except:
        message = 'Could not connect to Basler detector'
        print(message)
        interaction.error_msg(self, message)
        return

    try:
        initial_position = str(get_position(stage_controller))
        print("Initial position is: %s \n" % initial_position)
    except:
        message = 'Could not find initial position of stage'
        print(message)
        interaction.error_msg(self, message)
        return

    try:
        stage_controller.move_relative(int(total_volume_height/2))
        print('Moved to top of volume')
    except:
        message = 'Could not move stage to top of volume'
        print(message)
        interaction.error_msg(self, message)
        return

    try:
        position = str(get_position(stage_controller))
        print("Top of volume is located at: %s \n" % position)
        time.sleep(time_delay)
    except:
        message = 'Could not find top of volume position'
        print(message)
        interaction.error_msg(self, message)
        return

    try:
        loop_range = int(no_z_slices)
        print("Loop range is: {}".format(loop_range))
    except ValueError:
        message = 'no_z_slices incorrect type, please enter an int'
        print(message)
        interaction.error_msg(self, message)
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
                except:
                    message = 'Could not enable %s' % las
                    print(message)
                    interaction.error_msg(self, message)
                    return

                try:
                    lasers[las].laser_power = int(power)
                    print(' %s power is %s' % (las, power))
                except:
                    message = 'Could not change %s power' % las
                    print(message)
                    interaction.error_msg(self, message)
                    return

                try:
                    lasers[las].emission_on()
                    print('%s now emitting' % las)
                except:
                    message = 'Could not emit %s' % las
                    print(message)
                    interaction.error_msg(self, message)
                    return

                try:
                    if las == 'laser561':
                        basler_detector.camera.ExposureTime.SetValue(125000)
                        print('Exposure time is: {}'.format(basler_detector.camera.ExposureTime.GetValue()))
                    else:
                        basler_detector.camera.ExposureTime.SetValue(20000)
                        message = 'Exposure time is: {}'.format(basler_detector.camera.ExposureTime.GetValue())
                        print(message)
                        interaction.error_msg(self, message)
                        self.current_image = basler_detector.camera_grab()
                    self.array_list = self.current_image
                except:
                    message = 'Could not grab basler image'
                    print(message)
                    interaction.error_msg(self, message)
                    return

                try:
                    lasers[las].emission_off()
                    time.sleep(1)
                    print('%s stopped emitting' % las)
                except:
                    message = 'Could not emit %s' % las
                    print(message)
                    interaction.error_msg(self, message)
                    return

                try:
                    self.string_list = ['Volume_image_' + str(z_slice+1) + '_of_' + str(loop_range) +
                                        las]
                    self.update_display()
                except:
                    message = 'Could not update display'
                    print(message)
                    interaction.error_msg(self, message)
                    return

                try:
                    self.save_image()
                except:
                    message = 'Could not save image'
                    print(message)
                    interaction.error_msg(self, message)
                    return

                try:
                    lasers[las].disable()
                    print('%s now disabled' % las)
                except:
                    message = 'Could not disable %s' % las
                    print(message)
                    interaction.error_msg(self, message)
                    return

            try:
                target_position = float(total_volume_height/2.) + float(initial_position)\
                                  - (float(z_slice) * float(z_slice_distance))
                print('Initial position is: {}'.format(initial_position))
                print('Z_slice is: {}'.format(z_slice))
                print('z_slice_distance is: {}'.format(z_slice_distance))

                print('Target position is: %s' % str(target_position))
            except:
                message = 'Could not calculate target position'
                print(message)
                interaction.error_msg(self, message)
                return

            try:
                stage_controller.move_relative(-int(z_slice_distance))
            except:
                message = 'Failed to move stage controller by step distance'
                print(message)
                interaction.error_msg(self, message)
                return

            try:
                position = float(get_position(stage_controller))
                print(position)
            except:
                message = 'Failed to get current position after step movement'
                print(message)
                interaction.error_msg(self, message)
                return

            try:
                difference = position - target_position
                print('Difference is: %s' % str(difference))
            except:
                message = 'Failed to find difference between desired and current pos'
                print(message)
                interaction.error_msg(self, message)
                return

            while count < count_max and \
                    (difference > threshold or difference < -threshold):
                try:
                    stage_controller.move_relative(-int(difference))
                except:
                    message = 'Could not move controller by difference'
                    print(message)
                    interaction.error_msg(self, message)
                    return

                try:
                    position = float(get_position(stage_controller))
                except:
                    message = 'Failed to retrieve position after correction'
                    print(message)
                    interaction.error_msg(self, message)
                    return

                try:
                    difference = position - target_position
                    print('Difference is: %s' % str(difference))
                except:
                    message = 'Failed to calculated difference after correction'
                    print(message)
                    interaction.error_msg(self, message)
                    return

                count = count + 1

    except:
        print("Laser loop error")
        return

    try:
        stage_controller.move_relative(int(total_volume_height/2))
    except:
        message = 'Could not return stage to middle position'
        print(message)
        interaction.error_msg(self, message)
        return


def get_position(stage):
    time.sleep(time_delay)
    position = stage.current_position()
    return position
