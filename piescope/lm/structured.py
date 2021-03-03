"""Module for communication with the national intstruments controller.
"""

import nidaqmx
import time
from nidaqmx.constants import (LineGrouping)

LINES = {'P00': 'Dev1/port0/line0',
         'P01': 'Dev1/port0/line1',
         'P02': 'Dev1/port0/line2',
         'P03': 'Dev1/port0/line3',
         'P04': 'Dev1/port0/line4',
         'P05': 'Dev1/port0/line5',
         'P06': 'Dev1/port0/line6',
         'P07': 'Dev1/port0/line7',
         'P10': 'Dev1/port1/line0',
         'P11': 'Dev1/port1/line1',
         'P12': 'Dev1/port1/line2',
         'P13': 'Dev1/port1/line3',
         'P14': 'Dev1/port1/line4',
         'P15': 'Dev1/port1/line5',
         'P16': 'Dev1/port1/line6',
         'P17': 'Dev1/port1/line7',
         'P20': 'Dev1/port2/line0',
         'P21': 'Dev1/port2/line1',
         'P22': 'Dev1/port2/line2',
         'P23': 'Dev1/port2/line3',
         'P24': 'Dev1/port2/line4',
         'P25': 'Dev1/port2/line5',
         'P26': 'Dev1/port2/line6',
         'P27': 'Dev1/port2/line7'
         }


def single_line_pulse(delay, pin):
    print(pin)
    print(LINES[pin])
    task = nidaqmx.Task()
    task.do_channels.add_do_chan(
        LINES[pin], line_grouping=LineGrouping.CHAN_FOR_ALL_LINES)
    task.write(True)
    time.sleep(delay/1e3)
    task.write(False)
    task.close()


def multi_line_pulse(delay, *pins):
    task = nidaqmx.Task()
    for pin in pins:
        print(pin)
        task.do_channels.add_do_chan(
            LINES[pin], line_grouping=LineGrouping.CHAN_FOR_ALL_LINES)
    task.write([True]*len(pins))
    time.sleep(delay/1e3)
    task.write([False]*len(pins))
    task.close()
