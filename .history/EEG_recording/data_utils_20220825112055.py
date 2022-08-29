import os
import json
import datetime
from pathlib import Path
import mne
import pickle
from config import *
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