import argparse
import logging
from turtle import color
import keyboard
import pandas as pd
import numpy as np
import pyqtgraph as pg
import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds, BrainFlowPresets
from brainflow.data_filter import DataFilter, FilterTypes,DetrendOperations,WindowOperations
from pyqtgraph.Qt import QtGui, QtCore,QtWidgets
from unicodedata import category
from beeply.notes import *
from experiment_gui import *
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
import sys
from config import *
from utils import get_filenames_in_path
from data_utils import save_raw,getdata,getepoch,save_raw_to_dataframe,randomStimuli
from psychopy.visual import vlcmoviestim
import sounddevice as sd
import soundfile as sf

logging.getLogger('PIL').setLevel(logging.WARNING)
#Configuration
stimuli = []
a = beeps(1000)
b = beeps(1000)
mywin = visual.Window(SCREEN_SIZE, color="black",monitor="Experiment Monitor" , units='norm',screen=0) 

#ubuntu, delete folder
for cat in CATEGORIES:
    l = get_filenames_in_path(f"{IMAGE_FOLDER}{cat}")
    v = get_filenames_in_path(f"{VIDEO_FOLDER}{cat}")
    stimuli.append(f'{IMAGE_FOLDER}{cat}{"/"}{l[0]}')
    stimuli.append(f'{VIDEO_FOLDER}{cat}{"/"}{v[0]}')

print(stimuli)

#เวลาทั้งหมด = (4 block * 12 trials * 3 session * 5 second) + (10 second(instruction))+(120 second(baseline))+(50 second(fixation)*3session)
experiment_time = (NUM_BLOCK*NUM_TRIAL*NUM_SESSION*STIM_TIME)+(INSTRUCTION_TIME)+(BASELINE_EYEOPEN+BASELINE_EYECLOSE)+(FIXATION_TIME*5*3)
print(f"Total experiment time = {'{:.2f}'.format(math.ceil(experiment_time/60))} Minute" )
  
# Setup EEG board
def main():
    global EXE_COUNT
    global IMAGINE_COUNT
    global STIM_CHECK
    global PLAY_VIDEO
    global IS_FINISH
    BoardShim.enable_dev_board_logger()
    logging.basicConfig(level=logging.DEBUG)
    #brainflow initialization 
    params = BrainFlowInputParams()
    params.serial_port = SERIAL_PORT
    board_shim = BoardShim(BOARD_ID, params)

    #board prepare
    try:
        board_shim.prepare_session()
    except brainflow.board_shim.BrainFlowError as e:
        print(f"Error: {e}")
        print("The end")
        time.sleep(1)
        sys.exit()
    #board start streaming
    board_shim.start_stream()

    ##############################################
    # Experiment session
    ##############################################
    #task 
    #1) baseline run and save
    #2) imagine left and right save
    #3) execute left and right save
    logging.info("Begin experiment")
    while True:
        drawTextOnScreen('Experiment session : Press space bar to start',mywin)
        resp_key = event.getKeys(keyList=['1','2','3'])
        start = time.time()
        if '1' in resp_key:
            IS_FINISH = startExperiment(1,board_shim,mywin)
        elif '2' in resp_key:
            IS_FINISH = startExperiment(2,board_shim,mywin)
        elif '3' in resp_key:
            IS_FINISH = startExperiment(3,board_shim,mywin)
        if IS_FINISH:
            drawTextOnScreen('End of experiment, Thank you',mywin)
            stop  = time.time()
            print(f"Total experiment time = {(stop-start)/60} ")
            core.wait(10)
            break
    mywin.close()
    logging.info('End')
    
    if board_shim.is_prepared():
            logging.info('Releasing session')
            # stop board to stream
            board_shim.stop_stream()
            board_shim.release_session()

if __name__ == "__main__":
    main()