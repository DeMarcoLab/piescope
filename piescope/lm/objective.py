"""Module for the objective lens stage of the fluorescence detector.

SMARACT stage hardware.
"""
from socket import socket, AF_INET, SOCK_STREAM

pre_string = ':'
post_string = '\012'


class StageController(socket):
    def __init__(self, host='localhost', port=5000, timeout=2.0):
        super().__init__(family=AF_INET, type=SOCK_STREAM)
        self.settimeout(timeout)
        try:
            self.connect((host, port))
        except Exception as error:
            raise RuntimeError('Cannot connect to Smaract.'
                               'Error: %s', error)

    def move_absolute(self, position, hold=0):
        cmd = pre_string + 'MPA0,' + str(position) + ',' + str(hold) + \
              post_string
        ans = self.send_command(cmd)
        return ans

    def move_relative(self, distance, hold=0):
        cmd = pre_string + 'MPR0' + str(distance) + ',' + str(hold) + \
              post_string
        ans = self.send_command(cmd)
        return ans

    def current_position(self):
        cmd = pre_string + 'GP0' + post_string
        ans = self.send_command(cmd)
        return ans

    def send_command(self, cmd):
        self.sendall(cmd)
        return self.recv(1024)
