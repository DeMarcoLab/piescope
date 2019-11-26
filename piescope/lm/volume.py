import logging
import time
import numpy as np
import piescope.utils as util

from piescope.lm import objective, laser, detector

logger = logging.getLogger(__name__)


def volume_acquisition(laser_dict, num_z_slices, z_slice_distance, destination,
					   time_delay=1, count_max=5, threshold=5):
	"""Acquire an image volume using the fluorescence microscope.

	Parameters
	----------
	laser_dict : dict
		Dictionary with structure: {"name": (power, exposure)} with types
		{str: (int, int)}

	num_z_slices : int
		Amount of slices to take for total volume

	z_slice_distance : int
		Distance in nm between each z slice

	destination : str
		Path to save location for images taken during volume acquisition

	time_delay : int, optional
		Pause after moving to the top of the imaging volume, by default 1

	count_max : int, optional
		Maximum number of attempts to move the stage to its target position.
		By default 5

	threshold : int, optional
		Threshold cutoff for deciding whether the current stage position
		is close enough to the target position.
		By default 5

	Returns
	-------
	volume : multidimensional numpy array
		numpy.ndarray with shape (slices, cols, rows, channels)

	Notes
	-----
	It's good to assume a minimum of 0.5 microns per step,
	and a maximum 300 microns total height for the volume acquisition.
	"""
	total_volume_height = (int(num_z_slices)-1)*int(z_slice_distance)
	logger.debug('Total height is: %s' % str(total_volume_height) + '\n')
	logger.debug('Number of slices is: %s' % num_z_slices + '\n')
	logger.debug('Distance between slices is: %s' % z_slice_distance + '\n')

	stage_controller = objective.StageController()

	lasers = laser.initialize_lasers()
	logger.debug('Lasers successfully initialised \n')

	basler_detector = detector.Basler()
	logger.debug('Successfully connected to detector \n')
	sizing_image = basler_detector.camera_grab()
	sizing_shape = np.shape(sizing_image)

	volume = np.ndarray(shape=(num_z_slices, sizing_shape[0], sizing_shape[1], len(laser_dict)), dtype=np.uint8)
	time.sleep(time_delay)  # Pause to be sure movement is completed.
	initial_position = str(stage_controller.current_position())
	logger.debug("Initial position is: %s \n" % initial_position)

	stage_controller.move_relative(int(total_volume_height/2))
	print('Moved to top of volume')
	time.sleep(time_delay)  # Pause to be sure movement is completed
	position = str(stage_controller.current_position())
	print("Top of volume is located at: %s \n" % position)
	time.sleep(time_delay)

	loop_range = int(num_z_slices)
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
			basler_detector.camera.ExposureTime.SetValue(int(float(power[1])*1000))
			print("Exposure time set as: {}".format(power[1]))

			logger.debug('Exposure time is: {}'.format(
					basler_detector.camera.ExposureTime.GetValue()))

			volume[z_slice, :, :, channel] = basler_detector.camera_grab()
			# util.save_image(volume[z_slice, :, :, channel], destination + str(las) + "_" + str(z_slice) + ".tiff")
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
			time.sleep(time_delay)  # Pause to be sure movement is completed.
			position = float(stage_controller.current_position())
			logger.debug(position)

			difference = position - target_position
			logger.debug('Difference is: %s' % str(difference))

			while count < count_max and difference > threshold or \
					difference < -threshold:
				stage_controller.move_relative(-int(difference))
				time.sleep(time_delay)  # Pause to be sure movement is completed.
				position = float(stage_controller.current_position())
				difference = position - target_position
				logger.debug('Difference is: %s' % str(difference))
				count = count + 1

			channel = channel + 1

	stage_controller.move_relative(int(total_volume_height/2))

	return volume
