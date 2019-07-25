from piescope.lm import objective, laser

s = objective.StageController()

s.current_position()

s.move_relative(10000, hold=200)

s.current_position()

s.move_relative(-10000, 2000)

s.current_position()

# current_position = s.current_position()
# print('Current position is: ' + str(current_position))
#
# s.move_relative(-100000, hold=2000)
#
# current_position = s.current_position()
# print('Current position is: ' + str(current_position))
#
# print('End of commands.')

# s.close()




#
# exposure = 1000
# lasers = {1, 2, 4}
# laserpowers = {0, 100, 50}
#
#
# def test(exposuretime, lasers, laserpowers, *args):
#     print('exposuretime: ' + str(exposuretime))
#     print('lasers: ' + str(lasers))
#     print('laserpowers: ' + str(laserpowers))
#     print('args: ' + str(args))
#     return "hi"
#
#
# t = test(exposure, lasers, laserpowers)
# t = test(exposure, lasers, laserpowers, '23', '23', '12', '0', 4)
