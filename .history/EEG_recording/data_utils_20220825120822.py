import os
import json
import datetime
from pathlib import Path
import mne
import pickle
from config import *
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds, BrainFlowPresets
def now_datestring():
    return datetime.datetime.now().strftime("%Y-%m-%d--%H-%M-%S")

def save_raw(raw, name):
    folder_path = create_session_folder(name)
    raw.save(os.path.join(folder_path, "raw.fif"))
    return os.path.basename(folder_path)

def create_session_folder(subj):
    folder_name = f'{now_datestring()}_{subj}'
    folder_path = os.path.join(RECORDING_DIR, folder_name)
    Path(folder_path).mkdir(exist_ok=True)
    return folder_path

def load_recording(rec_folder):
    return mne.io.read_raw_fif(os.path.join(RECORDING_DIR, rec_folder, 'raw.fif'))

def getdata(data,board,clear_buffer=False,n_samples=None):
    """
        Get data that has been recorded to the board. (and clear the buffer by default)
        if n_samples is not passed all of the data is returned.
    """
    if not n_samples:
        n_samples = board.get_board_data_count()

    '''if clear_buffer:
        data = board.get_board_data()
    else:
        data = board.get_current_board_data(n_samples)'''
        
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
    
    print(raw_data.info['ch_names'])
    print(raw_data.info['sfreq'])
    print(raw_data['STIM MARKERS'])
    
    return raw_data

def getepoch(raws):
    for raw in raws:
        events = mne.find_events(raw)
        print(events)