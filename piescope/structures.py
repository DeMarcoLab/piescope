from dataclasses import dataclass

from fibsem.structures import MicroscopeSettings, Point
from piescope.utils import TriggerMode 


@dataclass
class CameraSettings:
    max_num_buffer: int
    image_frame_interval: int
    pixel_size: float
    objective_mag: float
    telescope_mag: float

@dataclass
class LightMicroscopeSettings:
    magnification: float
    pixel_size: float
    relative_position: Point
    camera: CameraSettings
    trigger_mode: TriggerMode = TriggerMode.Hardware



@dataclass
class PIEScopeSettings:
    microscope: MicroscopeSettings
    light_microscope: LightMicroscopeSettings