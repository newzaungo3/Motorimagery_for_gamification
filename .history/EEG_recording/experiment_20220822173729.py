import argparse
import logging
import keyboard
import pyqtgraph as pg
import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds, BrainFlowPresets
from brainflow.data_filter import DataFilter, FilterTypes,DetrendOperations,WindowOperations
from pyqtgraph.Qt import QtGui, QtCore,QtWidgets
from unicodedata import category
from beeply.notes import *
import pylsl
import time
import itertools
import math
import psychopy
from psychopy import visual, core, event,monitors
from datetime import datetime
from IPython.display import clear_output
import random
from numpy.random import default_rng


from utils import get_filenames_in_path

#==============================================
# Image setup
#==============================================
folder = 'Experiment_Gui/'
image = 'images/'
categories = ['left','right']
stimuli = []

#ubuntu, delete folder
for cat in categories:
    l = get_filenames_in_path(f"{folder}{image}{cat}")
    stimuli.append(f'{folder}{image}{cat}{"/"}{l[0]}')

print(stimuli)
#==============================================
# experiment parameters
#==============================================
#Widowsetting

screen_size = [1920, 1000]
#screen_size = [800,600]
#category
a = beeps(800)

#left and right image
total_image = 2
num_trial = 12 #12
num_block = 4 #4
num_session = 3 #3

# baseline run
baseline_eyeopen = 60 #60second
baseline_eyeclose = 60 #60second
alert_time = 800 #8second 
instruction_time = 2 
#stimuli time (left arrow and right arrow)
stim_time = 5 #5second
stim_blink_time = 0 #0second
fixation_time = 3 #10 "+" inter trial interval

#เวลาทั้งหมด = (4 block * 12 trials * 3 session * 5 second) + (10 second(instruction))+(120 second(baseline))+(50 second(fixation)*3session)
experiment_time = (num_block*num_trial*num_session*stim_time)+(instruction_time)+(baseline_eyeclose+baseline_eyeopen)+(fixation_time*5*3)
print(f"Total experiment time = {'{:.2f}'.format(math.ceil(experiment_time/60))} Minute" )

#==============================================
# Configuration
#==============================================

#name, type, channel_count, sampling rate, channel format, source_id
#info = StreamInfo('CytonMarkers', 'Markers', 1, 0.0, 'int32', 'CytonMarkerID')#make an outlet
info = pylsl.StreamInfo('CytonMarkers', 'Markers', 1, 0.0, 'string', 'CytonMarkerID')#make an outlet
outlet = pylsl.StreamOutlet(info)
# %whos

BoardShim.enable_dev_board_logger()
logging.basicConfig(level=logging.DEBUG)

parser = argparse.ArgumentParser()
# use docs to check which parameters are required for specific board, e.g. for Cyton - set serial port
parser.add_argument('--timeout', type=int, help='timeout for device discovery or connection', required=False,
                        default=0)
parser.add_argument('--ip-port', type=int, help='ip port', required=False, default=0)
parser.add_argument('--ip-protocol', type=int, help='ip protocol, check IpProtocolType enum', required=False,
                        default=0)
parser.add_argument('--ip-address', type=str, help='ip address', required=False, default='')
parser.add_argument('--serial-port', type=str, help='serial port', required=False, default='')
parser.add_argument('--mac-address', type=str, help='mac address', required=False, default='')
parser.add_argument('--other-info', type=str, help='other info', required=False, default='')
parser.add_argument('--streamer-params', type=str, help='streamer params', required=False, default='')
parser.add_argument('--serial-number', type=str, help='serial number', required=False, default='')
parser.add_argument('--board-id', type=int, help='board id, check docs to get a list of supported boards',
                        required=False, default=BoardIds.SYNTHETIC_BOARD)
parser.add_argument('--file', type=str, help='file', required=False, default='')
parser.add_argument('--master-board', type=int, help='master board id for streaming and playback boards',
                        required=False, default=BoardIds.NO_BOARD)
parser.add_argument('--preset', type=int, help='preset for streaming and playback boards',
                        required=False, default=BrainFlowPresets.DEFAULT_PRESET)
args = parser.parse_args()

#brainflow initialization 
params = BrainFlowInputParams()
params.ip_port = args.ip_port
params.serial_port = args.serial_port
params.mac_address = args.mac_address
params.other_info = args.other_info
params.serial_number = args.serial_number
params.ip_address = args.ip_address
params.ip_protocol = args.ip_protocol
params.timeout = args.timeout
params.file = args.file
params.master_board = args.master_board
params.preset = args.preset
board_shim = BoardShim(args.board_id, params)

#board prepare
try:
    board.prepare_session()
except brainflow.board_shim.BrainFlowError as e:
        print(CRED + f"Error: {e}" + CEND)
        if ser:
            ser.write("c".encode()) # message for arduino to stop streaming
            time.sleep(1)
            ser.close()
        print("The end")
        time.sleep(1)
        sys.exit()
#board start streaming
#draw start screen

#begin experiment and collect data with brainflow(while loop)