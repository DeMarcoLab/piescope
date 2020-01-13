"""Module for the objective lens stage of the fluorescence detector.

SMARACT stage hardware.
"""
import logging
from socket import socket, AF_INET, SOCK_STREAM

logger = logging.getLogger(__name__)


class StageController(socket):
    """Class for connecting to the SMARACT objective stage controller."""
    def __init__(self, host='169.254.111.111', port=139, timeout=5.0,
                 testing=False):
        """Create a new StageController instance, for SMARACT objective stage.

        Parameters
        ----------
        socket : socket object
            Socket object that the StageController class inherits from.
        host : str, optional
            IP address for SMARACT fluorescence objective lens stage.
            By default, '169.254.111.111'
        port : int, optional
            Port number for socket connection to SMARACT objective lens stage.
            Default port number is 139
        timeout : float, optional
            Time in seconds before connection times out, by default 5.0 seconds
        testing : bool, optional
            For offline testing only, by default False.

        Raises
        ------
        RuntimeError
            Error raised if socket connection to SMARACT ojbective lens stage
            cannot be established.
        """
        super().__init__(family=AF_INET, type=SOCK_STREAM)
        self.settimeout(timeout)
        if not testing:
            try:
                self.connect((host, port))
                print('Successfully connected to SMARACT objective lens stage')
            except Exception as e:
                logger.error("SMARACT objective stage error: " + str(e))
                raise RuntimeError('Cannot connect to SMARACT stage! '
                                   'Error: {}'.format(e))

    def initialise_system_parameters(self, relative_accumulation=0,
                                     reference_mark=0, reference_hold=1000,
                                     start_position=0):
        """Initialize the fluorescence objective lens stage controller.

        Parameters
        ----------
        relative_accumulation : 0 or 1
            Applies a setting that means relative movements add up when
            instructions are sent before previous instructions complete.
            0 for disable, 1 for enable.
            Default is 0 (meaning disabled).

        reference_mark : int
            Sets which reference mark to travel to when initialising.
            Default center mark is at 0.

        reference_hold : int
            Time in ms to keep power high after moving to the reference mark.
            Default is 1000.

        start_position : int
            Set the value in nm that the reference mark should represent.
            Default is 0.
        """
        try:
            logger.debug('Initialising parameters.')
            self.set_relative_accumulation(relative_accumulation)
            self.find_reference_mark(reference_mark, reference_hold)
            self.set_start_position(start_position)
            logger.debug('Successfully initialised.')
        except Exception as e:
            logger.error(e)
            logger.error("Error in initialising stage parameters")
            raise e

    def set_relative_accumulation(self, onoff):
        """Set the relative accumulation for the objective lens stage.

        Parameters
        ----------
        onoff : 0 or 1
            Applies a setting that means relative movements add up when
            instructions are sent before previous instructions complete.
            0 for disable, 1 for enable.

        Returns
        -------
        ans : string
            Return string from the stage controller.
            Gives information about whether or not call succeeded.
        """
        if str(onoff) not in set(["0", "1"]):
            raise ValueError("Input argument to set_relative_accumulation() "
                             "in piescope.lm.objective module "
                             "must be equal to either 0 or 1.")
        try:
            cmd = 'SARP0,' + str(onoff)
            ans = self.send_command(cmd)
            return ans
        except Exception as e:
            logger.error(e)
            logger.error("Unable to set relative accumulation.")
            raise e

    def find_reference_mark(self, mark, hold=1000):
        """Find reference mark position for fluorescence objective lens stage.

        Parameters
        ----------
        mark : int
            Sets which reference mark to travel to when initialising.
            Centre mark is at 0.

        hold : int
            Time in ms to keep power high after moving to the reference mark.

        Returns
        -------
        ans : string
            Return string from the stage controller.
            Gives information about whether or not call succeeded.
        """
        try:
            cmd = 'FRM0,' + str(mark) + ',' + str(hold) + ',1'
            ans = self.send_command(cmd)
        except Exception as e:
            logger.error(e)
            logger.error("Unable to find reference mark.")
            raise e
        else:
            return ans

    def set_start_position(self, start_position):
        """Set starting position for the fluorescence objective lens stage.

        Parameters
        ----------
        start_position : int
            Set what value in nm to have the reference mark represent.

        Returns
        -------
        ans : string
            Return string from the stage controller.
            Gives information about whether or not call succeeded.
        """
        try:
            cmd = 'SP0,' + str(start_position)
            ans = self.send_command(cmd)
        except Exception as e:
            logger.error(e)
            logger.error("Unable to set start position.")
            raise e
        else:
            return ans

    def move_absolute(self, position, hold=0):
        """Absolute movement of the fluorescence objective lens stage.

        Parameters
        ----------
        position : int
            Position in nanometers (nm) to move to relative to zero position.

        hold : int
            Time in ms to keep power high after moving to absolute position.

        Returns
        -------
        ans : string
            Return string from the stage controller.
            Gives information about whether or not call succeeded.
        """
        try:
            cmd = 'MPA0,' + str(position) + ',' + str(hold)
            ans = self.send_command(cmd)
        except Exception as e:
            logger.error(e)
            logger.error("Unable to move the stage.")
            raise e
        else:
            return ans

    def move_relative(self, distance, hold=0):
        """Relative movement of the fluorescence objective lens stage.

        Parameters
        ----------
        position : int
            Position in nanometers to move to, relative to current position.

        hold : int
            Time in ms to keep power high after moving to relative position.

        Returns
        -------
        ans : string
            Return string from the stage controller.
            Gives information about whether or not call succeeded.
        """
        try:
            cmd = 'MPR0,' + str(distance) + ',' + str(hold)
            ans = self.send_command(cmd)
        except Exception as e:
            logger.error(e)
            logger.error("Unable to move the stage.")
            raise e
        else:
            return ans

    def current_position(self):
        """Current position of the fluorescence objective lens stage.

        Returns
        -------
        position : string
            Current position of objective stage controller as a string.
        """
        try:
            cmd = 'GP0'
            ans = self.send_command(cmd)
        except Exception as e:
            logger.error(e)
            logger.error("Unable to fetch objective stage position.")
            raise e
        else:
            position = str(ans).rsplit(',')[-1].split('\\')[0]
            return position

    def send_command(self, cmd, pre_string=':', post_string='\012'):
        """Send command to the fluorescence objective lens stage.

        Parameters
        ----------
        cmd : str
            Command string to send to stage controller.
        pre_string : str
            Prefix to socket communication string.
        post_string : str
            Suffix to socket communication string.

        Returns
        -------
        self.recv(1024)
            Return string from the stage controller.
            Gives information about whether or not call succeeded.

        Raises
        ------
        Raises an exception if unable to send the command through the socket.
        """
        cmd = bytes(pre_string + cmd + post_string, 'utf-8')
        try:
            self.sendall(cmd)
        except Exception as e:
            logger.error(e)
            logger.error("Unable to send command to controller: "
                         "{}".format(cmd))
            raise e
        else:
            return self.recv(1024)
