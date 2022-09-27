import logging
import os
import re
import warnings
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path

import numpy as np
import serial
import serial.tools.list_ports
import skimage.color
import skimage.io
import skimage.util
import tifffile
import yaml
from autoscript_sdb_microscope_client.structures import AdornedImage
from matplotlib import pyplot as plt


class TriggerMode(Enum):
    Hardware = 0
    Software = 1


class Modality(Enum):
    Light = 0
    Ion = 1
    Electron = 2


def load_image(filename: Path, adorned: bool = True):

    # check file
    if not os.path.exists(filename):
        raise FileNotFoundError("File not found")

    # open file
    if adorned:
        image = AdornedImage.load(filename)
        try:
            image.metadata.binary_result.pixel_size.x
        except AttributeError:
            raise AttributeError("Image must be AdornedImage type")
    else:
        image = skimage.io.imread(filename)

    return image


def save_image(
    image, destination, metadata={}, *, allow_overwrite=False, timestamp=True
):
    """Save image to file.

    Parameters
    ----------
    image : ndarray or AdornedImage
        Image array to save. Pixel values must have integer type.
    destination : str
        Filename of saved image, with .tif extension.
        Only the .tif file format is reliably supported.
    metadata : dict, optional
        This kwarg is ignored for AdornedImage, used only for numpy arrays.
        Default value is an empty dictionary.
        There are no restrictions on what key-value pairs you can use here.
        You can access this metadata in Fiji/ImageJ by opening the saved image
        with the BioFormats importer and checking the box 'Display Metadata'.
    allow_overwrite : bool, optional
        Whether to allow overwriting existing files. Default is False.
    timestamp : bool, optional
        Time stamp appended to filename.
        Uses ISO 8601 standard format, YYYY-mm-ddTTHHmmsszz
        ISO 8601 reference: https://en.wikipedia.org/wiki/ISO_8601

    Notes
    -----
    https://www.lfd.uci.edu/~gohlke/code/tifffile.py.html

    Save a volume with xyz voxel size 2.6755x2.6755x3.9474 µm^3 to an ImageJ file:

    >>> volume = numpy.random.randn(57*256*256).astype('float32')
    >>> volume.shape = 1, 57, 1, 256, 256, 1  # dimensions in TZCYXS order
    >>> imwrite('temp.tif', volume, imagej=True, resolution=(1./2.6755, 1./2.6755),
    ...         metadata={'spacing': 3.947368, 'unit': 'um'})

    """
    destination = os.path.normpath(destination)
    # Make sure the output file format is acceptable
    if not destination.endswith(".tiff"):
        destination += ".tiff"

    # Append timestamp string to filename, if needed
    if timestamp:
        timestamp_string = datetime.now().strftime("_%Y-%m-%dT%H%M%S%f")
        base, ext = os.path.splitext(destination)
        destination = base + timestamp_string + ext

    os.makedirs(os.path.dirname(destination), exist_ok=True)

    if isinstance(image, AdornedImage):
        image.save(destination)
        logging.debug("Saved: {}".format(destination))
        return
    if not isinstance(image, np.ndarray):
        raise ValueError(
        "Cannot save image! Expected a numpy array or AdornedImage, "
        "instead found image.dtype of {}".format(image.dtype)
        )

    if image.dtype.char not in "BHhf":  # uint8, uint16, int16, or ?
        image = skimage.util.img_as_uint(image)  # 16 bit unsigned int

    # if saving a volume:
    if image.ndim == 6:  # (CPZAYX) --> (PZAYX)
        metadata.update({"axes": "CPZAYX"})
        tifffile.imwrite(destination, image, bigtiff=True, metadata=metadata)
        temp_destination = destination
        print(f'Image shape when saving: {image.shape}')
        # volume_split = np.zeros(image.shape)
        for i in range(image.shape[0]):
            # volume_split[:, i] = image[:, i]
            metadata.update({"axes": "PZAYX"})
            temp_destination = (destination.replace(".tiff", "") + "_channel_" + str(i) + ".tiff")
            tifffile.imwrite(temp_destination, image[i], bigtiff=True, metadata=metadata)
        return

    # otherwise save regular image
    if image.ndim == 3:  # (YXC)
        image = np.moveaxis(image, -1, 0)  # move channel axis (CYX)
        metadata.update({"axes": "CYX"})

    skimage.io.imsave(destination, image, imagej=True, metadata=metadata)

    logging.debug("Saved: {}".format(destination))


def max_intensity_projection(image: np.ndarray) -> np.ndarray:
    """Returns maximum intensity projection of fluorescence image volume.

    Args:
        image (np.ndarray):  expecting numpy array with dimensions:
        (ch, angle, pln, phase, col, row)

    Raises:
        ValueError: only accepts 6-D volumes of shape (ch, angle, pln, phase, col, row)

    Returns:
        np.ndarray: maximum intensity projected to ndarray of dimensions (col, row, ch)
    """
    results = []

    #CPZAYX
    if image.ndim == 6:
        for channel_image in image:
            # collapse angles, phases and planes, keeping cols, rows and channels
            max_intensity = np.max(channel_image, axis=(0, 1, 2))
            results.append(max_intensity)

        # put channels on last axis
        projected_max_intensity = np.stack(results, axis=-1)
        #YXC
        return projected_max_intensity

    else:
        raise ValueError(
            "expecting numpy.array with dimensions " "(ch, angle, pln, phase, col, row)"
        )


def rgb_image(image: np.ndarray, colour_dict: dict) -> np.ndarray:
    """Convert an image into an RGB representation

    Args:
        image (np.ndarray): expect ndarray of dimension (col, row, ch<=4)
        colour_dict (dict): dictionary of colour mapping

    Raises:
        ValueError: image expected to be 3 dimensions

    Returns:
        np.ndarray: rgb version of image with shape (col, row, 3)
    """

    if image.ndim != 3:
        raise ValueError(
            "Wrong number of dimensions in input image! "
            "Expected an image with 3 dimensions, "
            "but found {} dimensions".format(image.ndim)
        )

    rgb = np.zeros(shape=(image.shape[0], image.shape[1], 3), dtype=np.uint8)

    for i in range(3):  # for RGB
        for channel in range(image.shape[-1]):  # for each laser channel
            rgb[:, :, i] = (
                rgb[:, :, i]
                + image[:, :, channel] * float(colour_dict[channel][i]) * 1 / 255
            )

    return rgb


def read_config(config_filename):
    with open(config_filename, "r") as file:
        settings_dict = yaml.safe_load(file)
    settings_dict = parse_config(settings_dict)
    return settings_dict

def write_config(config_filename, config):

    config['imaging']['lm']['trigger_mode'] = config['imaging']['lm']['trigger_mode'].name

    with open(config_filename, "w") as file:
        yaml.safe_dump(config, file, sort_keys=False)


def parse_config(config):
    mode = str(config["imaging"]["lm"]["trigger_mode"]).title()
    if mode in TriggerMode.__members__:
        config["imaging"]["lm"]["trigger_mode"] = TriggerMode[mode]
    else:
        config["imaging"]["lm"]["trigger_mode"] = TriggerMode.Software

    return config


def connect_serial_port(settings):
    """Serial port for communication with the lasers.

    Parameters
    ----------
    port : str, optional
        Serial port device name, by default 'COM3'.
    baudrate : int, optional
        Rate of communication, by default 115200 bits per second.
    timeout : int, optional
        Timeout period, by default 1 second.

    Returns
    -------
    pyserial Serial() object
        Serial port for communication with the lasers.
    """

    _available_serial_ports = serial.tools.list_ports.comports()
    _available_port_names = [port.device for port in _available_serial_ports]

    port = settings["serial"]["port"]
    baudrate = settings["serial"]["baudrate"]
    timeout = settings["serial"]["timeout"]

    if port not in _available_port_names:
        warnings.warn(
            "Default laser serial port not available.\n" "Fall back to port {}".format()
        )
        port = _available_port_names[0]
    return serial.Serial(port, baudrate=baudrate, timeout=timeout)


def write_serial_command(serial_connection, command):
    serial_connection.close()
    serial_connection.open()
    serial_connection.write(bytes(command, "utf-8"))
    serial_connection.close()


@dataclass
class Crosshair:
    rectangle_horizontal: plt.Rectangle
    rectangle_vertical: plt.Rectangle


def create_crosshair(image: np.ndarray or AdornedImage, settings: dict, x=None, y=None):
    if type(image) == AdornedImage:
        image = image.data

    if x is None:
        midx = int(image.shape[1] / 2)
    else:
        midx = x
    if y is None:
        midy = int(image.shape[0] / 2)
    else:
        midy = y

    cross_width = int(
        settings["imaging"]["crosshairs"]["thickness"] / 100 * image.shape[1]
    )
    cross_length = int(
        settings["imaging"]["crosshairs"]["length"] / 100 * image.shape[1]
    )

    rect_horizontal = plt.Rectangle(
        (midx - cross_length / 2, midy - cross_width / 2), cross_length, cross_width
    )
    rect_vertical = plt.Rectangle(
        (midx - cross_width, midy - cross_length / 2), cross_width * 2, cross_length
    )

    # set colours
    colour = settings["imaging"]["crosshairs"]["color"]
    rect_horizontal.set_color(colour)
    rect_vertical.set_color(colour)

    return Crosshair(
        rectangle_horizontal=rect_horizontal, rectangle_vertical=rect_vertical
    )



import logging

import numpy as np
from piescope.utils import Modality
from autoscript_sdb_microscope_client import SdbMicroscopeClient
from autoscript_sdb_microscope_client.structures import GrabFrameSettings

"""Module for interacting with the FIBSEM using Autoscript."""

def move_to_microscope(microscope: SdbMicroscopeClient, settings: dict):
    from autoscript_sdb_microscope_client.structures import StagePosition
    x, y = settings['system']['relative_lm_position']
    current_position_x = microscope.specimen.stage.current_position.x
    fibsem_min = settings['system']['fibsem_min_position']
    fibsem_max = settings['system']['fibsem_max_position']
    lm_min = settings['system']['lm_min_position']
    lm_max = settings['system']['lm_max_position']
    
    if fibsem_min < current_position_x < fibsem_max:
        logging.info('Under FIBSEM, moving to light microscope')
    elif lm_min < current_position_x < lm_max:
        x = -x
        y = -y
        logging.info('Under light microscope, moving to FIBSEM')
    else:
        raise RuntimeError('Not positioned under the either microscope, cannot move to other microscope')

    new_position = StagePosition(x=x, y=y, z=0, r=0, t=0)
    microscope.specimen.stage.relative_move(new_position)