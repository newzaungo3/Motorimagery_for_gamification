import argparse
import logging
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
from data_utils import save_raw,getdata,getepoch,save_raw_to_dataframe
logging.getLogger('PIL').setLevel(logging.WARNING)
#Configuration
stimuli = []
a = beeps(800)
mywin = visual.Window(SCREEN_SIZE, color="black",monitor="testMonitor" , units='norm') 

#ubuntu, delete folder
for cat in CATEGORIES:
    l = get_filenames_in_path(f"{IMAGE_FOLDER}{cat}")
    stimuli.append(f'{IMAGE_FOLDER}{cat}{"/"}{l[0]}')

#เวลาทั้งหมด = (4 block * 12 trials * 3 session * 5 second) + (10 second(instruction))+(120 second(baseline))+(50 second(fixation)*3session)
experiment_time = (NUM_BLOCK*NUM_TRIAL*NUM_SESSION*STIM_TIME)+(INSTRUCTION_TIME)+(BASELINE_EYEOPEN+BASELINE_EYECLOSE)+(FIXATION_TIME*5*3)
print(f"Total experiment time = {'{:.2f}'.format(math.ceil(experiment_time/60))} Minute" )

#==============================================
# Configuration
#==============================================
def drawTextOnScreen(massage) :
    message = visual.TextStim( mywin, text=massage, languageStyle='LTR')
    message.contrast =  0.3
    message.height= 0.07
    message.draw() # draw on screen
    mywin.flip()   # refresh to show what we have draw

def drawTrial(imgPath, mark, stimTime,board) :
    drawTextOnScreen('') 
    core.wait(STIM_BLINK_TIME)
    img = visual.ImageStim( mywin,  image=imgPath )
    img.size *= 1.5
    img.draw()
    mywin.flip()
    eegMarking(board,mark)
    core.wait(stimTime)
    
def drawFixation(fixationTime,board):
    fixation = visual.ShapeStim(mywin,
                                vertices=((0, -0.5), (0, 0.5), (0,0), (-0.5,0), (0.5, 0)),
                                lineWidth=5,
                                closeShape=False,
                                lineColor="white"
            )
    fixation.draw()      
    mywin.flip()   # refresh to show what we have draw
    eegMarking(board,3.0)
    core.wait(fixationTime-0.5)
    drawTextOnScreen('')
    core.wait(0.5)
    
def drawBaselinerun(openTime,closeTime,board):
    #Baseline run
    #open
    drawTextOnScreen("Baseline run 1: Open eyes (estimated time: 60 second)")
    core.wait(3)
    drawTextOnScreen('')
    eegMarking(board,3.0)
    core.wait(openTime)
    #alert
    mywin.flip()
    a.hear('A_')
    drawFixation(FIXATION_TIME,board)

    #close
    drawTextOnScreen("Baseline run 2: Close eyes (estimated time: 60 second)")
    core.wait(3)
    drawTextOnScreen('')
    eegMarking(board,3.0)
    core.wait(closeTime)
    #alert
    mywin.flip()
    a.hear('A_')
    drawFixation(FIXATION_TIME,board)
    
def eegMarking(board,marker):   # use trial variable from main
    if marker == 1.0:
        print("Marker string Left")
    elif marker == 2.0:
        print("Marker string Right" )
    elif marker == 3.0:
        print("Marker string Idle")
    board.insert_marker(marker)
    
# Setup EEG board
def main():
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
    logging.info("Begin experiment")
    while True:
        # how to start an experiment
        drawTextOnScreen('Experiment session : Press space bar to start')
        keys = event.getKeys()
        if 'space' in keys:      # If space has been pushed
            start = time.time()
            drawTextOnScreen('') 
            drawBaselinerun(BASELINE_EYEOPEN,BASELINE_EYECLOSE,board_shim)
            #experiment      
            #3 session
            for session in range(NUM_SESSION):
                # 4 block
                for block in range(NUM_BLOCK):
                    #1:'execute_left',2:'imagine_left',3:'executed_right',4:'imagine_right'
                    #12 trials
                    for trials in range(NUM_TRIAL):
                        drawTextOnScreen(f"Session:{session+1}_Block:{block+1}({BLOCK_DICT[block+1]})_Trials:{trials+1}")
                        core.wait(1)
                        drawTextOnScreen("")
                        core.wait(0.5)
                        if block+1 == 1 or block+1 == 2 :
                            stim = stimuli[0]
                        else:
                            stim = stimuli[1]
                        print(stim)
                        drawTrial(f"{stim}",BLOCK_MARKER[block+1],STIM_TIME,board_shim)
                        a.hear('A_')
                        drawFixation(FIXATION_TIME,board_shim)
            drawTextOnScreen('End of experiment, Thank you')
            
            stop  = time.time()
            print(f"Total experiment time = {(stop-start)/60} ")
            core.wait(10)
            break
    mywin.close()
    logging.info('End')
    
    if board_shim.is_prepared():
            logging.info('Releasing session')
            # get all data and remove it from internal buffer
            data = board_shim.get_board_data()
            # stop board to stream
            board_shim.stop_stream()
            board_shim.release_session()
            
    #MNE process
    raw = getdata(data,args.board_id,n_samples = 250)
    train_epochs,epochs_raw_data,labels = getepoch(raw,4,10)
    save_raw(raw,NAME)
    save_raw_to_dataframe(epochs_raw_data,NAME)
    

if __name__ == "__main__":
    main()