"""Module for the objective lens stage of the fluorescence detector.

SMARACT stage hardware.
"""
from socket import socket, AF_INET, SOCK_STREAM
from piescope_gui import gui_interaction as interaction

pre_string = ':'
post_string = '\012'


class StageController(socket):
    def __init__(self, host='130.194.248.58', port=139, timeout=5.0):
        super().__init__(family=AF_INET, type=SOCK_STREAM)
        self.settimeout(timeout)
        try:
            self.connect((host, port))
            print('Successfully connected to Smaract')
        except Exception as error:
            interaction.error_msg(self, "Stage error: " + str(error))
            raise RuntimeError('Cannot connect to Smaract.'
                               'Error: %s', error)

    def initialise_system_parameters(self, relative_accumulation=0,
                                     reference_mark=0, reference_hold=1000,
                                     start_position=0):

        try:
            print('Initialising parameters.')
            self.set_relative_accumulation(relative_accumulation)
            self.find_reference_mark(reference_mark, reference_hold)
            self.set_start_position(start_position)
            print('Successfully initialised.')
        except:
            interaction.error_msg(self, "Error in initialising stage "
                                        "parameters")

    def set_relative_accumulation(self, onoff):
        try:
            cmd = 'SARP0,' + str(onoff)
            ans = self.send_command(cmd)
            return ans
        except:
            interaction.error_msg(self, "Unable to set relative accumulation")

    def find_reference_mark(self, mark, hold=1000):
         try:
            cmd = 'FRM0,' + str(mark) + ',' + str(hold) + ',1'
            ans = self.send_command(cmd)
            return ans
         except:
             interaction.error_msg(self, "Unable to find reference mark")

    def set_start_position(self, start_position):
        try:
            cmd = 'SP0,' + str(start_position)
            ans = self.send_command(cmd)
            return ans
        except:
            interaction.error_msg(self, "Unable to set start position")

    def move_absolute(self, position, hold=0):
        try:
            cmd = 'MPA0,' + str(position) + ',' + str(hold)
            ans = self.send_command(cmd)
            return ans
        except:
            interaction.error_msg(self, "Unable to move the stage")

    def move_relative(self, distance, hold=0):
        try:
            cmd = 'MPR0,' + str(distance) + ',' + str(hold)
            ans = self.send_command(cmd)
            return ans
        except:
            interaction.error_msg(self, "Unable to move the stage")

    def current_position(self):
        try:
            cmd = 'GP0'
            ans = self.send_command(cmd)
            position = str(ans).rsplit(',')[-1].split('\\')[0]
            return position
        except:
            interaction.error_msg(self, "Unable to fetch stage position")


    def send_command(self, cmd):
        try:
            cmd = bytes(pre_string + cmd + post_string, 'utf-8')
            self.sendall(cmd)
            return self.recv(1024)
        except:
            interaction.error_msg(self, "Unable to send command to controller")
