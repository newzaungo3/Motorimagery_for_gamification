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
from data_utils import save_raw,getdata,getepoch,save_raw_to_dataframe
from psychopy.visual import vlcmoviestim
logging.getLogger('PIL').setLevel(logging.WARNING)
#Configuration
stimuli = []
a = beeps(500)
b = beeps(800)
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

#==============================================
# Configuration
#==============================================
def drawTextOnScreen(massage) :
    message = visual.TextStim( mywin, text=massage, languageStyle='LTR',bold=True,color=[89, 206, 143],colorSpace='rgb')
    message.contrast =  0.3
    message.height= 0.10
    message.width = 0.10
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
    eegMarking(board,4.0)
    core.wait(fixationTime-0.5)
    drawTextOnScreen('')
    core.wait(0.5)
    
def drawBaselinerun(openTime,closeTime,board,board_id):
    baseline_open_name = f'{PARTICIPANT_ID}R{1:02d}'
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
    
    #save baselinefile to mne and .fif
    #remove buffer
    #next experiment will no have baseline signal
    data = board.get_board_data()
    data_copy = data.copy()
    raw = getdata(data_copy,board_id,n_samples = 250)
    save_raw(raw,baseline_open_name)   
    
    #close
    baseline_close_name = f'{PARTICIPANT_ID}R{2:02d}'
    drawTextOnScreen("Baseline run 2: Close eyes (estimated time: 60 second)")
    core.wait(3)
    drawTextOnScreen('')
    eegMarking(board,3.0)
    core.wait(closeTime)
    #alert
    mywin.flip()
    a.hear('A_')
    drawFixation(FIXATION_TIME,board)
    
    #save baselinefile to mne and .fif
    #remove buffer
    #next experiment will have no baseline signal
    data = board.get_board_data()
    data_copy = data.copy()
    raw = getdata(data_copy,board_id,n_samples = 250)
    save_raw(raw,baseline_close_name)
    
def eegMarking(board,marker):   # use trial variable from main
    if marker == 1.0:
        print("Marker string Left")
    elif marker == 2.0:
        print("Marker string Right" )
    elif marker == 3.0:
        print("Marker string Idle")
    elif marker == 4.0:
        print("Marker string Fixation")
    board.insert_marker(marker)

def playVideo(videoPath, mark, stimTime,board):
    video = vlcmoviestim.VlcMovieStim(mywin,videoPath)
    video.loadMovie(videoPath)
    video.setVolume(0)
    video.play()
    eegMarking(board,mark)
    while True:
        video.draw(mywin)
        mywin.flip()
        if video.frameTime >= STIM_TIME:
            break
    
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
        # how to start an experiment
        drawTextOnScreen('Experiment session : Press space bar to start')
        keys = event.getKeys()
        if 'space' in keys:      # If space has been pushed
            start = time.time()
            drawTextOnScreen('')
            if IS_BASELINE: 
                drawBaselinerun(BASELINE_EYEOPEN,BASELINE_EYECLOSE,board_shim,BOARD_ID)
            #experiment      
            #3 session
            for session in range(NUM_SESSION):
                # 4 block
                for block in range(NUM_BLOCK):
                    if IS_VIDEO:
                        if (block+1) % 2 != 0:
                            #Executed
                            PLAY_VIDEO = False
                        else:
                            #Imagine
                            PLAY_VIDEO = True
                    #1:'execute_left',2:'executed_right',3:'imagine_left',4:'imagine_right'
                    #12 trials
                    STIM_CHECK = 0
                    for trials in range(NUM_TRIAL):
                        #drawTextOnScreen(f"Session:{session+1}_Block:{block+1}({BLOCK_DICT[block+1]})_Trials:{trials+1}")
                        a.hear('A_')
                        drawFixation(FIXATION_TIME,board_shim)
                        #สลับซ้ายขวา = ใช้ mod
                        #check is_video == true       
                        if PLAY_VIDEO == True:
                            #left
                            if STIM_CHECK % 2 == 0:
                                stim = stimuli[1]
                                Marker = BLOCK_MARKER[1]
                            #right
                            elif STIM_CHECK % 2 != 0:
                                stim = stimuli[3]
                                Marker = BLOCK_MARKER[2]
                            #drawTrial(f"{stim}",Marker,STIM_TIME,board_shim)
                            playVideo(f"{stim}",Marker,STIM_TIME,board_shim)
                            a.hear('A_')
                            drawFixation(FIXATION_TIME,board_shim)
                            STIM_CHECK += 1
                            print(STIM_CHECK)
                        else:
                            #left     
                            if STIM_CHECK % 2 == 0:
                                stim = stimuli[0]
                                Marker = BLOCK_MARKER[1]
                            #right
                            elif STIM_CHECK % 2 != 0:
                                stim = stimuli[2]
                                Marker = BLOCK_MARKER[2]
                            #print(stim)
                            #print(Marker)
                            drawTrial(f"{stim}",Marker,STIM_TIME,board_shim)
                            a.hear('A_')
                            drawFixation(FIXATION_TIME,board_shim)
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
                    drawTextOnScreen('Block Break 30 seconds')
                    core.wait(BLOCK_BREAK)
                drawTextOnScreen('Session Break 60 seconds')        
                core.wait(SESSION_BREAK)                
            drawTextOnScreen('End of experiment, Thank you')
            
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
            
    #MNE process
    #raw = getdata(data,args.board_id,n_samples = 250)
    '''
    train_epochs,epochs_raw_data,labels = getepoch(raw,4,10)
    save_raw(raw,NAME)
    save_raw_to_dataframe(epochs_raw_data,NAME)
    '''

if __name__ == "__main__":
    main()