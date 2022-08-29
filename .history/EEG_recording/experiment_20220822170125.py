import argparse
import logging
import keyboard
import pyqtgraph as pg
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