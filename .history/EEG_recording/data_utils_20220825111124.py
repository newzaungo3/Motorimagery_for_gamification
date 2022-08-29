import os
import json
import datetime
from pathlib import Path
import mne
import pickle


def save_raw(raw, rec_params):
    folder_path = create_session_folder(rec_params['subject'])
    raw.save(os.path.join(folder_path, "raw.fif"))
    json_dump(rec_params, os.path.join(folder_path, "params.json"))
    return os.path.basename(folder_path)

def create_session_folder(subj):
    folder_name = f'{now_datestring()}_{subj}'
    folder_path = os.path.join(const.RECORDINGS_DIR, folder_name)
    Path(folder_path).mkdir(exist_ok=True)
    return folder_path

def json_dump(obj, save_path):
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=4)