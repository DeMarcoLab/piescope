"""Module for the objective lens stage of the fluorescence detector.

SMARACT stage hardware.
"""
from socket import socket, AF_INET, SOCK_STREAM

pre_string = ':'
post_string = '\012'


class StageController(socket):
    def __init__(self, host='130.194.192.40', port=139, timeout=3.0):
        super().__init__(family=AF_INET, type=SOCK_STREAM)
        self.settimeout(timeout)
        try:
            self.connect((host, port))
        except Exception as error:
            raise RuntimeError('Cannot connect to Smaract.'
                               'Error: %s', error)

    def initialise_system_parameters(self, relative_accumulation=0,
                                     reference_mark=0, reference_hold=1000,
                                     start_position=0):
        print("Successfully connected to Smaract.  Initialising parameters.")
        self.set_relative_accumulation(relative_accumulation)
        self.find_reference_mark(reference_mark, reference_hold)
        self.set_start_position(start_position)
        print("Successfully initalised.")

    def set_relative_accumulation(self, onoff):
        cmd = 'SARP0,' + str(onoff)
        ans = self.send_command(cmd)
        return ans

    def find_reference_mark(self, mark, hold=1000):
        cmd = 'FRM0,' + str(mark) + ',' + str(hold) + ',1'
        ans = self.send_command(cmd)
        return ans

    def set_start_position(self, start_position):
        cmd = 'SP0,' + str(start_position)
        ans = self.send_command(cmd)
        return ans

    def move_absolute(self, position, hold=0):
        cmd = 'MPA0,' + str(position) + ',' + str(hold)
        ans = self.send_command(cmd)
        return ans

    def move_relative(self, distance, hold=0):
        cmd = 'MPR0,' + str(distance) + ',' + str(hold)
        ans = self.send_command(cmd)
        return ans

    def current_position(self):
        cmd = 'GP0'
        ans = self.send_command(cmd)
        position = str(ans).rsplit(',')[-1].split('\\')[0]
        print('Current position is: ' + position)
        return position

    def send_command(self, cmd):
        cmd = bytes(pre_string + cmd + post_string, 'utf-8')
        self.sendall(cmd)
        return self.recv(1024)
