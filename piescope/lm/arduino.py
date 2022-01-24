import time
import serial
import serial.tools.list_ports

DEFAULT_SERIAL_PORT = 'COM7'  # default laser serial communication port

class Arduino:
    """Arduino Class"""
    def __init__(self, serial_port=DEFAULT_SERIAL_PORT):
        self.SERIAL_PORT = serial_port
        self.connection = connect_serial_port(self.SERIAL_PORT)

    def send_volume_info(self, laser_dict):
        string_to_send = 'E'
        for laser_name in ['laser640', 'laser561', 'laser488', 'laser405']:
            if laser_name in laser_dict.keys():
                string_to_send += str(int(laser_dict[laser_name][1]/1e3)) + ' '
            else:
                string_to_send += str(0) + ' '

        self._write_serial_command(command=string_to_send)

    def _write_serial_command(self, command):
        self.connection.close()
        self.connection.open()
        time.sleep(1)  # required, not sure why
        self.connection.write(bytes(command, 'utf-8'))
        self.connection.close()


def connect_serial_port(port=DEFAULT_SERIAL_PORT, baudrate=115200, timeout=3):
    """Serial port for communication with the lasers.

    Parameters
    ----------
    port : str, optional
        Serial port device name, by default 'COM6'.
    baudrate : int, optional
        Rate of communication, by default 115200 bits per second.
    timeout : int, optional
        Timeout period, by default 1 second.

    Returns
    -------
    pyserial Serial() object
        Serial port for communication with the lasers.
    """
    return serial.Serial(port, baudrate=baudrate, timeout=timeout)
