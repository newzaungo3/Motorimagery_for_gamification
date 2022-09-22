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
from data_utils import save_raw,getdata,getepoch,save_raw_to_dataframe
import requests
from numpy import ndarray
import keyboard
from threading import Thread
import time
import logging
from database import Database 

def main():
    logging.getLogger().setLevel(logging.DEBUG)
    BoardShim.enable_dev_board_logger()
    params = BrainFlowInputParams()
    params.serial_port = "COM3"
    board = BoardShim(0, params)
    board.prepare_session()
    board.start_stream(450000)

    while True:  
        #wait to avoid bombardment of gpu
        #ตรงนี้ต้องเป็น experiment ซ้ายขวา
        print("wait 7 second")
        #หยุดไปเลยไม่อัดต่อ ต้องส่งเป็นthread
        time.sleep(7)
        data = board.get_board_data()
        temp:ndarray = data.copy()
        data = {
        "name":"New",
        "data": temp.tolist()
        }
        database = Database(values=temp)
        thread = Thread(target=database.locked_update,args=(1,))
        thread.start()
        #print(database.value)
        #requests.post("http://localhost:8000/items",json=data)
        if keyboard.is_pressed('q'):
                print("End of experiment")
                break
     
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
