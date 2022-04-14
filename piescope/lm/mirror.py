from pipython import GCSDevice
from enum import Enum, auto
import logging

h_move = [0.0164, 0]
s_move = [0.008031, 0.006564]
o_move = [-0.008031, 0.006564]

class MirrorPosition(Enum):
    WIDEFIELD = [3, -2]
    HORIZONTAL = [-2, -2]
    HORIZONTAL_120 = [HORIZONTAL[0]+h_move[0], HORIZONTAL[1]+h_move[1]]
    HORIZONTAL_240 = [HORIZONTAL[0]+2*h_move[0], HORIZONTAL[1]+2*h_move[1]]
    SIXTY = [3, 3]
    SIXTY_120 = [SIXTY[0]+s_move[0], SIXTY[1]+s_move[1]]
    SIXTY_240 = [SIXTY[0]+2*s_move[0], SIXTY[1]+2*s_move[1]]
    ONETWENTY = [-2, 3]
    ONETWENTY_120 = [ONETWENTY[0]+o_move[0], ONETWENTY[1]+o_move[1]]
    ONETWENTY_240 = [ONETWENTY[0]+2*o_move[0], ONETWENTY[1]+2*o_move[1]]

class StageMacro(Enum):
    MAIN = auto()
    PHASE = auto()
    MOVEA = auto()
    MOVER = auto()
    ONTARGET = auto()


class ImagingType(Enum):
    WIDEFIELD = auto()
    SIM = auto()


class PIController:
    def __init__(self):
        super(PIController, self).__init__()
        self.COM_PORT = 4
        self.device = GCSDevice()
        self._open_device()
        self.axes = self.device.allaxes
        self.move_to(MirrorPosition.WIDEFIELD)
        self.current_position = MirrorPosition.WIDEFIELD
        self.set_mode(mode=ImagingType.WIDEFIELD)

    def home(self) -> None:
        """Returns the stage to 0 on all axes"""
        GCSDevice.MOV(self.device, self.axes, len(self.axes)*[0])

    def move_to(self, mirror_position: MirrorPosition) -> None:
        self.stopAll()
        GCSDevice.MOV(self.device, self.axes, mirror_position.value)
        self.start_macro(StageMacro.ONTARGET)
        self.current_position = mirror_position
        logging.info(f'Current position: {self.current_position.name}')

    def get_current_position(self):
        """Returns currently set position, not necessarily actual position"""
        return self.current_position.value

    def set_mode(self, mode=ImagingType.WIDEFIELD):
        self.mode = mode

    def get_mode(self):
        return self.mode

    def start_macro(self, macro_name: StageMacro, *args) -> None:
        GCSDevice.MAC_START(self.device, macro=macro_name.name, args=args)

    def stopAll(self) -> None:
        """Stops all movement and macros"""
        GCSDevice.StopAll(self.device, noraise=True)

    def _open_device(self) -> None:
        # self.device.InterfaceSetupDlg()
        self.device.ConnectRS232(comport=self.COM_PORT, baudrate=115200, autoconnect=False)
        # stop any previous or start-up macros
        if GCSDevice.IsRunningMacro(self.device):
            startup_macro = GCSDevice.qRMC(self.device).strip('\n')
            logging.info(f'Currently running macro: {startup_macro}, closing...')
            self.stopAll()
        else:
            logging.info(f'Not running any macros on startup.')
