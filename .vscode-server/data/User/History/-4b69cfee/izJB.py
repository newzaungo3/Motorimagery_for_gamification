import os
import json
import datetime
from pathlib import Path
import mne
import pickle
from mne.datasets import eegbci
from config import *
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds, BrainFlowPresets
from numpy import ndarray
import requests
from threading import Thread,Lock
import time
 
def now_datestring():
    return datetime.datetime.now().strftime("%Y-%m-%d--%H-%M-%S")

def save_raw_to_dataframe(raw,name):
    epoch_dataframe = raw.copy().to_data_frame()
    csv_folder = create_session_folder(PARTICIPANT_ID,CSV_DIR)
    csv_name = f'{name}.csv'
    epoch_dataframe.to_csv(os.path.join(csv_folder,csv_name),encoding='utf-8')

def save_raw(raw, name):
    folder_path = create_session_folder(PARTICIPANT_ID,RECORDING_DIR)
    raw.save(os.path.join(folder_path, f'{name}{TYPE_OF_FILE}'))
    return os.path.basename(folder_path)

def create_session_folder(subj,dir):
    folder_name = f'{subj}'
    if os.path.isdir(os.path.join(dir, folder_name)):
        folder_path = os.path.join(dir, folder_name)
    else:
        folder_path = os.path.join(dir, folder_name)
        Path(folder_path).mkdir(exist_ok=True)
    return folder_path

def load_recording(rec_folder):
    return mne.io.read_raw_fif(os.path.join(RECORDING_DIR, rec_folder, 'raw.fif'))

def getdata(data,board,clear_buffer=False,n_samples=None):
    """
        Get data that has been recorded to the board. (and clear the buffer by default)
        if n_samples is not passed all of the data is returned.
    """
    # Creating MNE objects from brainflow data arrays
    # the only relevant channels are eeg channels + marker channel
    # get row index which holds markers
    marker_channel = BoardShim.get_marker_channel(board)
    
    #row which hold eeg data
    eeg_channels = BoardShim.get_eeg_channels(board)
    data[eeg_channels] = data[eeg_channels] / 1e6
    #eeg row + marker row (8 + 1)
    data = data[eeg_channels + [marker_channel]]
    
    #string of all channel name ['Fp1', 'Fp2', 'C3', 'C4', 'P7', 'P8', 'O1', 'O2']
    ch_names = BoardShim.get_eeg_names(board)
    ch_types = (['eeg'] * len(eeg_channels)) + ['stim']
    ch_names = ch_names + ["Stim Markers"]
    
    #sample rate
    sfreq = BoardShim.get_sampling_rate(board)
    
    #Create Raw data from MNE
    info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)
    raw = mne.io.RawArray(data, info)
    raw_data = raw.copy()
    eegbci.standardize(raw_data)
    montage = mne.channels.make_standard_montage('standard_1020')
    raw_data.set_montage(montage)
    #2 electrode
    raw_data.pick_channels(['C3','C4','STIM MARKERS'])
    #print(raw_data.info['ch_names'])
    #print(raw_data.info['sfreq'])
    #print(raw_data['STIM MARKERS'])
    
    return raw_data

def getepoch(raw,trial_duration, calibration_duration,reject_bad=False,on_missing='warn'):
    reject_criteria = dict(eeg=100e-6)  # 100 µV
    flat_criteria = dict(eeg=1e-6)  # 1 µV
    markers= [0,1,2]
    epochs_list = []
    #raws = [raws]
    events = mne.find_events(raw)
    print("ESUS")
    print(events)
    event_dict = {'1.0': 0 ,'2.0':1}
    epochs = mne.Epochs(raw,events,event_id=event_dict,tmin=calibration_duration, tmax=trial_duration, picks="data",
    on_missing=on_missing, baseline=None)
    print("Esus 2")
    print(epochs.event_id)
    print("Esus 3")
    print(epochs.events)
    #epochs_list.append(epochs)
    #epochs = mne.concatenate_epochs(epochs_list)
    labels = epochs.events[:,-1]
    #print(f'Found {len(labels)} epochs')
    #print(epochs) 
    print("Ekuy")
    print(labels)
    
    return epochs.get_data(),epochs,labels

def send_raw(database):
    time.sleep(0.3)
    data = {
        "name":"New",
        "data": database.value.tolist()
    }
    requests.post("http://localhost:8000/items",json=data)
    