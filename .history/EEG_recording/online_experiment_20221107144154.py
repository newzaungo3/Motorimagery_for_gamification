import argparse
import time
import matplotlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds, BrainFlowPresets
from brainflow.data_filter import DataFilter
import mne
from mne.datasets import eegbci
from mne import Epochs, pick_types, events_from_annotations,find_events
from mne.channels import make_standard_montage
from mne.filter import construct_iir_filter,create_filter
from config import *
from data_utils import save_raw,getdata,getepoch,save_raw_to_dataframe,send_raw,Erd_Plot
import requests
from numpy import ndarray
import keyboard
from threading import Thread
import time
import logging
from database import Database 
from psychopy import visual, core, event,monitors
from experiment_gui import *
import multiprocessing
import concurrent.futures

a = beeps(1000)
b = beeps(800)
logging.getLogger().setLevel(logging.DEBUG)
def main():
    global EXE_COUNT
    global IMAGINE_COUNT
    global STIM_CHECK
    global PLAY_VIDEO
    #Window setup
    mywin = visual.Window(SCREEN_SIZE, color="black",monitor="Experiment Monitor" , units='norm',screen=2)
    erdWin = visual.Window(SCREEN_SIZE, color="black",monitor="ERD view" , units='norm',screen=1)
    stimuli = get_stimuli()
    
    #Board setup
    BoardShim.enable_dev_board_logger()
    params = BrainFlowInputParams()
    params.serial_port = SERIAL_PORT
    board = BoardShim(BOARD_ID, params)
    board.prepare_session()
    board.start_stream(450000)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        while True:  
            #wait to avoid bombardment of gpu
            #ตรงนี้ต้องเป็น experiment ซ้ายขวา
            drawTextOnScreen('Experiment session : Press space bar to start',mywin)
            keys = event.getKeys()
            if 'space' in keys: #start
                start = time.time()
                drawTextOnScreen('',mywin)
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
                        a.hear('A_')
                        for trials in range(NUM_TRIAL):
                            drawFixation(FIXATION_TIME,board,mywin)
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
                                playVideo(f"{stim}",Marker,STIM_TIME,board,mywin)
                                drawFixation(FIXATION_TIME,board,mywin)
                                STIM_CHECK += 1
                                print(STIM_CHECK)
                                
                                #จบ 1 trials
                                print("save and send") 
                                drawTextOnScreen('Save & Send',mywin)
                                #time.sleep(5)
                                data = board.get_board_data()
                                
                                temp:ndarray = data.copy()
                                database = Database(values=temp)
                                print(database.value.shape)
                                
                                #thread 1 pack
                                executor.submit(database.locked_update,1)
                                core.wait(0.1)
                                #thread 2 send                
                                drawTextOnScreen('Sending',mywin)
                                executor.submit(send_raw,database)
                                core.wait(15)
                                drawTextOnScreen('',mywin)
                                core.wait(5)
                                throw_data = board.get_board_data()
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
                                drawTrial(f"{stim}",Marker,STIM_TIME,board,mywin)
                                drawFixation(FIXATION_TIME,board,mywin)
                                STIM_CHECK += 1
                                print(STIM_CHECK)
                                
                                #จบ 1 trials
                                print("save and send") 
                                drawTextOnScreen('Save & Send',mywin)
                                #time.sleep(5)
                                data = board.get_board_data()
                                
                                #visualize ERD
                                drawTextOnScreen('Visualize',mywin)
                                raw = getdata(data,0,n_samples=250)
                                __,epochs_raw_data,__ = getepoch(raw,0,4)
                                image_path = Erd_Plot(epochs_raw_data,trials)
                                img = visual.ImageStim( erdWin,  image=image_path )
                                
                                drawTextOnScreen('Sending',mywin)
                                temp:ndarray = data.copy()
                                database = Database(values=temp)
                                print(database.value.shape)
                                
                                #thread 1 pack
                                executor.submit(database.locked_update,1)
                                core.wait(0.1)
                                #thread 2 send                
                                drawTextOnScreen('Sending',mywin)
                                executor.submit(send_raw,database)
                                
                                core.wait(15)
                                drawTextOnScreen('',mywin)
                                core.wait(5)
                                throw_data = board.get_board_data()
                            
                drawTextOnScreen('End of experiment, Thank you',mywin)
                stop  = time.time()
                core.wait(5)
                break
            
     
    if board.is_prepared():
            logging.info('Releasing session')
            # stop board to stream
            board.stop_stream()
            board.release_session()
    
    
    
if __name__ == "__main__":
    main()
