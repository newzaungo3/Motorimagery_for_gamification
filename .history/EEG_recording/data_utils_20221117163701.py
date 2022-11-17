import os
import json
import datetime
from pathlib import Path
import mne
import pickle
from mne.datasets import eegbci
from mne.time_frequency import tfr_multitaper
from config import *
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds, BrainFlowPresets
from numpy import ndarray
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from threading import Thread,Lock
import threading
import time
from utils import get_filenames_in_path
import random
from matplotlib.colors import TwoSlopeNorm
import pandas as pd
import numpy as np
 
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

def save_fig(data,name,trial):
    folder_path = create_session_folder(PARTICIPANT_ID,ERD_FOLDER)
    data.savefig(os.path.join(folder_path, f'{name}_{trial:02d}{FIG_FILE}'))
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
    raw_data=raw_data.notch_filter([50,75,100])
    raw_data=raw_data.filter(8,14, method='fir', verbose=20)
    #2 electrode
    #raw_data.pick_channels(['C3','C4','STIM MARKERS'])
    #raw_data = raw_data.drop_channels(['Fp1', 'Fp2', 'P7', 'P8', 'O1', 'O2'])
    print(raw_data.info['ch_names'])
    #print(raw_data.info['sfreq'])
    #print(raw_data['STIM MARKERS'])
    
    return raw_data

def getepoch(raw,tmin,tmax,reject_bad=False,on_missing='warn'):
    reject_criteria = dict(eeg=100e-6)  # 100 µV
    flat_criteria = dict(eeg=1e-6)  # 1 µV
    markers= [0,1,2]
    epochs_list = []
    baseline = (0,2)
    #raws = [raws]
    events = mne.find_events(raw,stim_channel='STIM MARKERS')
    event_dict = {'Left': 1, 'Right': 2, '3': 3}
    epochs = mne.Epochs(raw,events,event_id=event_dict,tmin=tmin, tmax=tmax,reject=reject_criteria, picks="data",
    on_missing=on_missing, preload=True, baseline=baseline)
    #epochs = epochs.copy().resample(160)
    print(epochs.get_data().shape)
    #epochs_list.append(epochs)
    #epochs = mne.concatenate_epochs(epochs_list)
    labels = epochs.events[:,-1]-1
    #print(f'Found {len(labels)} epochs')
    #print(epochs) 
    
    return epochs.get_data(),epochs,labels

def send_raw(database):
    lock = threading.Lock()
    with lock:
        data = {
            "name":"New",
            "data": database.value.tolist()
        }
        requests.post("http://localhost:8000/items",json=data)
        time.sleep(5)

def randomStimuli():
    '''Input
        1. Stimuli set
        2. randomnumber
        3. marker
        Output
        
        Dict of stimuli and marker    
    '''
    #ubuntu, delete folder
    stimuli = []
    for cat in CATEGORIES:
        l = get_filenames_in_path(f"{IMAGE_FOLDER}{cat}")
        stimuli.append(f'{IMAGE_FOLDER}{cat}{"/"}{l[0]}')
    
    for cat in CATEGORIES:
        v = get_filenames_in_path(f"{VIDEO_FOLDER}{cat}")
        stimuli.append(f'{VIDEO_FOLDER}{cat}{"/"}{v[0]}')
    
    print(stimuli)
    image_list=[]
    video_list=[]
    
    left_i = 0
    right_i = 0
    
    n=20
    for i in range(n):
        # random check number of list before append in list
        num = random.randint(0,1)
        if num == 0:
            if left_i != 10:
                print('left')
                image_list.append(num)
                left_i += 1
            else:
                image_list.append(1)
        elif num == 1:
            if right_i != 10:
                print('right')
                image_list.append(num)
                right_i += 1
            else:
                image_list.append(0) 
        #image_list.append(random.randint(1,2))
        video_list.append(random.randint(3,4))
    print(image_list)
    print(video_list)
    return image_list,video_list
def randomlist(num_range,min,max):
    for i in range(num_range):
        # random check number of list before append in list
        num = random.randint(min,max)
        return_list = []
        if num == 0:
            if left_i != 10:
                print('left')
                return_list.append(num)
                left_i += 1
            else:
                return_list.append(1)
        elif num == 1:
            if right_i != 10:
                print('right')
                return_list.append(num)
                right_i += 1
            else:
                return_list.append(0) 
    return return_list               
def Erd_Plot(epochs,trial):
    
    print("ERE PROCESS")
    freqs = np.arange(8, 14)  # frequencies from 2-35Hz
    vmin, vmax = -1, 1.5  # set min and max ERDS values in plot
    baseline = (0, 3)  # baseline interval (in s)
    cnorm = TwoSlopeNorm(vmin=vmin, vcenter=0, vmax=vmax)  # min, center & max ERDS
    kwargs = dict(n_permutations=100, step_down_p=0.05, seed=1,
                buffer_size=None, out_type='mask')  # for cluster test
    tmin, tmax = 0, 8
    
    tfr = tfr_multitaper(epochs, freqs=freqs, n_cycles=freqs, use_fft=True,
                     return_itc=False, average=False, decim=1)
    tfr.crop(tmin, tmax).apply_baseline(baseline, mode="percent")
    
    
    df = tfr.to_data_frame(time_format=None, long_format=True)
    print(df)
    # Map to frequency bands:
    freq_bounds = {'_': 0,
               'delta': 3,
               'theta': 7,
               'alpha': 13,
               'beta': 35,
               'gamma': 140}
    df['band'] = pd.cut(df['freq'], list(freq_bounds.values()),
                    labels=list(freq_bounds)[1:])
    
    # Filter to retain only relevant frequency bands:
    freq_bands_of_interest = ['delta', 'theta', 'alpha', 'beta']

    df = df[df.band.isin(freq_bands_of_interest)]

    df['band'] = df['band'].cat.remove_unused_categories()

    # Order channels for plotting:
    df['channel'] = df['channel'].cat.reorder_categories(('C3', 'C4'),
                                                        ordered=True)
    
    g = sns.FacetGrid(df, row='band', col='condition')
    g.map(sns.lineplot, 'time', 'value', 'channel', n_boot=10)
    axline_kw = dict(color='black', linestyle='dashed', linewidth=0.5, alpha=0.5)
    g.map(plt.axhline, y=0, **axline_kw)
    g.map(plt.axvline, x=0, **axline_kw)
    g.set(ylim=(-1, None))
    g.set_axis_labels("Time (s)", "ERDS (%)")
    g.set_titles(col_template="{col_name}", row_template="{row_name}")
    g.add_legend(ncol=2, loc='lower center')
    g.fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.08)
    save_fig(g,NAME,trial)
