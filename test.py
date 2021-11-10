import numpy as np
import matplotlib.pyplot as plt

from sklearn.pipeline import Pipeline
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import ShuffleSplit, cross_val_score
import mne
from mne import Epochs, pick_types, events_from_annotations
from mne.channels import make_standard_montage
from mne.io import concatenate_raws, read_raw_edf,read_raw_edf,read_raw_gdf
from mne.datasets import eegbci
from mne.decoding import CSP
import os

def get_data():
    path = "dataset\\bci_dataset\\train"
    test_path = "dataset\\bci_dataset\\train\\A03T.gdf"
    files = os.listdir(path)
    data_path = []
    for f in files:
        file = os.path.join(path,f)
        data_path.append(file)
        
    
    tmin, tmax = -0.5, 4.
    event_id = dict(left=1, right = 2, foot=3,tongue=4)

    #raw = concatenate_raws([read_raw_gdf(f, preload=True) for f in data_path])
    raw = concatenate_raws([read_raw_gdf(test_path, preload=True)])
    raw_data = raw.copy()
    print(raw_data.info)
    # strip channel names of "." characters
    raw_data.rename_channels(lambda x: x.strip('.'))

    # Apply band-pass filter
    raw_data.filter(4., 38., fir_design='firwin', skip_by_annotation='edge')
    raw_data.notch_filter(50)

    events, _ = events_from_annotations(raw_data)
    
    #ploting
    fig = mne.viz.plot_events(events, sfreq=raw_data.info['sfreq'],
                          first_samp=raw_data.first_samp, event_id=event_id)
    
    
    picks = pick_types(raw_data.info, meg=False, eeg=True, stim=False, eog=False,
                       exclude='bads')
    #delete eog band
    picks = np.delete(picks,[22,23,24])
    # Read epochs (train will be done only between 1 and 2s)
    #reject_criteria = dict( eeg=100e-6)       # 100 µV
    # Testing will be done with a running classifier
    epochs = Epochs(raw_data, events, event_id, tmin, tmax, proj=True, picks=picks,
                    baseline=None,preload=True)
    epochs.crop(tmin=1., tmax=None)
    labels = epochs.events[:, 2] -1
    return epochs.get_data()[:, :, :256], labels,epochs,raw_data


epochs_data, labels,epochs1,raw= get_data()

print(epochs1)
epochs1.plot()
epochs1.plot_psd(fmax=50)