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
mywin = visual.Window(SCREEN_SIZE, color="black",monitor="Experiment Monitor" , units='norm') 

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
    board_shim.start_stream(450000, "file://brainflow_data.csv:w")

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
        keys = event.getKeys()
        if 'space' in keys:     
            start = time.time()
            drawTextOnScreen('',mywin)
            if IS_BASELINE: 
                drawBaselinerun(BASELINE_EYEOPEN,BASELINE_EYECLOSE,board_shim,BOARD_ID,mywin)
            for session in range(NUM_SESSION):
                image_list,numIm_list,video_list,numVi_list = randomStimuli(NUM_TRIAL)
                for block in range(NUM_BLOCK):
                    if IS_VIDEO:
                        if (block+1) % 2 != 0:
                            #Executed use image list
                            PLAY_VIDEO = False
                            stim = image_list
                        else:
                            #Imagine use video list
                            PLAY_VIDEO = True
                            stim = video_list
                    STIM_CHECK = 0
                    a.hear('A_')
                    for trials in range(NUM_TRIAL):
                        drawFixation(FIXATION_TIME,board_shim,mywin)     
                        if PLAY_VIDEO == True:
                            if PLAY_SOUND == True:
                                data, fs = sf.read(SOUND_DICT[numVi_list[trials]])
                                sd.play(data, fs)
                                sd.wait()
                            #playVideo(f"{stim}",Marker,STIM_TIME,board_shim,mywin)
                            playVideo(f"{stim[trials]}",BLOCK_MARKER[numVi_list[trials]],STIM_TIME,board_shim,mywin)
                            #b.hear('A_')
                            drawFixation(FIXATION_TIME,board_shim,mywin)
                            STIM_CHECK += 1
                            print(STIM_CHECK)
                        else:
                            if PLAY_SOUND == True:
                                data, fs = sf.read(SOUND_DICT[numVi_list[trials]])
                                sd.play(data, fs)
                                sd.wait()
                            drawTrial(f"{stim[trials]}",BLOCK_MARKER[numIm_list[trials]],STIM_TIME,board_shim,mywin)
                            drawFixation(FIXATION_TIME,board_shim,mywin)
                            STIM_CHECK += 1
                            print(STIM_CHECK)
                                
                    #save 1 block save เพราะมีซ้ายขวาแล้ว    
                    #save mne executed type
                    if (block+1) % 2 != 0:
                        logging.info('SAVING EXECUTED')
                        block_name = f'{PARTICIPANT_ID}R{EXECUTE_NO[EXE_COUNT]:02d}' 
                        # get all data and remove it from internal buffer
                        data = board_shim.get_board_data()
                        data_copy = data.copy()
                        raw = getdata(data_copy,BOARD_ID,n_samples = 250)
                        save_raw(raw,block_name)
                        EXE_COUNT = EXE_COUNT + 1
                    #save mne imagine type
                    elif (block+1) % 2 == 0:
                        logging.info('SAVING IMAGINE')
                        block_name = f'{PARTICIPANT_ID}R{IMAGINE_NO[IMAGINE_COUNT]:02d}'
                        # get all data and remove it from internal buffer 
                        data = board_shim.get_board_data()
                        data_copy = data.copy()
                        raw = getdata(data_copy,BOARD_ID,n_samples = 250)
                        save_raw(raw,block_name)
                        IMAGINE_COUNT = IMAGINE_COUNT + 1
                        
                    #block break
                    if (block+1) != 4:
                        a.hear('A_')
                        drawTextOnScreen('Block Break 2 Minutes',mywin)
                        core.wait(BLOCK_BREAK)
                        #throw data
                        data = board_shim.get_board_data()
                if (session+1) != 2:     
                    a.hear('A_')   
                    drawTextOnScreen('Session Break 60 seconds',mywin)        
                    core.wait(SESSION_BREAK)                
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