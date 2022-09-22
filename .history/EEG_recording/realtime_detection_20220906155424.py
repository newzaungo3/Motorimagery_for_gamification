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
from data_utils import save_raw,getdata,getepoch,save_raw_to_dataframe,send_raw
import requests
from numpy import ndarray
import keyboard
from threading import Thread
import time
import logging
from database import Database 
from psychopy import visual, core, event,monitors
from experiment_gui import *
logging.getLogger().setLevel(logging.DEBUG)
def main():
    #Window setup
    mywin = visual.Window(SCREEN_SIZE, color="black",monitor="Experiment Monitor" , units='norm') 
    stimuli = get_stimuli()
    
    #Board setup
    BoardShim.enable_dev_board_logger()
    params = BrainFlowInputParams()
    params.serial_port = "COM3"
    board = BoardShim(0, params)
    board.prepare_session()
    board.start_stream(450000)

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
                    #1:'execute_left',2:'executed_right',3:'imagine_left',4:'imagine_right'
                    #12 trials
                    
                    for trials in range(NUM_TRIAL):
                        drawTextOnScreen(f"Session:{session+1}_Block:{block+1}({BLOCK_DICT[block+1]})_Trials:{trials+1}",mywin)
                        core.wait(1)
                        drawTextOnScreen("",mywin)
                        core.wait(0.5)
                        if block+1 == 1 or block+1 == 3 :
                            #left
                            stim = stimuli[0]
                        else:
                            #right
                            stim = stimuli[1]
                        print(stim)
                        print(BLOCK_MARKER[block+1])
                        
                        drawTrial(f"{stim}",BLOCK_MARKER[block+1],STIM_TIME,board,mywin)
                        a.hear('A_')
                        drawFixation(FIXATION_TIME,board,mywin)
                        
                        #จบ 1 trials 
                        time.sleep(3)
                        data = board.get_board_data()
                        temp:ndarray = data.copy()
                        database = Database(values=temp)
                        #thread 1 pack
                        thread1 = Thread(target=database.locked_update,args=(1,))
                        thread1.start()
                        #thread 2 send
                        thread2 = Thread(target=send_raw,args=(database,))
                        thread2.start()
                        
            '''print("wait 7 second")
            #หยุดไปเลยไม่อัดต่อ ต้องส่งเป็นthread
            time.sleep(7)
            
            
            
            drawTextOnScreen('End of experiment, Thank you')
            stop  = time.time()
            print(f"Total experiment time = {(stop-start)/60} ")
            core.wait(5)
            break
            '''
     
    board.stop_stream()
    board.release_session()
    
    
    
    #raw = getdata(data,args.board_id,n_samples = 250)
    #print(type(raw))
    #train_epochs,epochs_raw_data,labels = getepoch(raw,4,10)
    #getEpoch(eeg_data,eeg_channels,args.board_id)
    #save_raw(raw,NAME)
    #save_raw_to_dataframe(epochs_raw_data,NAME)
    
if __name__ == "__main__":
    main()
