from pipython import GCSDevice
from enum import Enum, auto
import logging

class StagePosition(Enum):
    WIDEFIELD = [2, -3]
    HORIZONTAL = [-3, -3]
    SIXTY = [3, 3]
    ONETWENTY = [-2, 2]



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
        self.move_to(StagePosition.WIDEFIELD)
        self.current_position = StagePosition.WIDEFIELD
        self.mode = ImagingType.WIDEFIELD

    def home(self) -> None:
        """Returns the stage to 0 on all axes"""
        GCSDevice.MOV(self.device, self.axes, len(self.axes)*[0])

    def move_to(self, stage_position: StagePosition) -> None:
        self.stopAll()
        GCSDevice.MOV(self.device, self.axes, stage_position.value)
        self.start_macro(StageMacro.ONTARGET)
        self.current_position = stage_position
        logging.info(f'Current position: {self.current_position.name}')

    def get_current_position(self):
        """Returns currently set position, not necessarily actual position"""
        return self.current_position.value

    def next_position(self):
        """Moves to the next SIM angle"""
        if self.mode == ImagingType.WIDEFIELD:
            return
        self.stopAll()
        if self.current_position == StagePosition.SIXTY:
            self.move_to(StagePosition.ONETWENTY)
        elif self.current_position == StagePosition.ONETWENTY:
            self.move_to(StagePosition.HORIZONTAL)
        elif self.current_position == StagePosition.HORIZONTAL:
            self.move_to(StagePosition.SIXTY)

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
