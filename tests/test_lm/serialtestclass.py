# Testing serial ports
# https://faradayrf.com/unit-testing-pyserial-code/

# Import modules
import serial


class SerialTestClass(object):
    """A mock serial port test class"""

    def __init__(self):
        """Creates a mock serial port which is a loopback object"""
        self.device = "test"
        self._port = "loop://"
        self._timeout = 0
        self._baudrate = 115200
        self.serialPort = \
            serial.serial_for_url(url=self._port,
                                  timeout=self._timeout,
                                  baudrate=self._baudrate)

    def __enter__(self, *args, **kwargs):
        pass

    def __exit__(self, *args, **kwargs):
        pass

    def open(self, *args, **kwargs):
        pass

    def close(self, *args, **kwargs):
        pass

    def read(self, command):
        pass

    def write(self, command):
        pass
