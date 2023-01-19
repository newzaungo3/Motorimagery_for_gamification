import matplotlib.pyplot as plt
import time
from mne.datasets import sample
from mne.io import read_raw_fif
import threading
import mne as mne
from mne_realtime import LSLClient, MockLSLStream
import numpy as np

print(__doc__)

######HYPERPARAMETERS
epoch_width = 7  #2.6
waittime = 0.2
threshold = 4  #3 out of 5 epochs
num_of_epochs = 5
host = 'UN-2022.01.70'
wait_max = 5
_, ax = plt.subplots(1)
n_epochs = 5
#########

#defining the stream data format
sfreq = 250
ch_names = ["Fz","C3","Cz","C4","Pz","PO7","Oz","PO8"]
ch_types = ['eeg'] * 8
info = mne.create_info(ch_names, sfreq, ch_types = ch_types)
# this is the host id that identifies your stream on LSL

epoch_chunks = int(np.round(sfreq * epoch_width))  #freq * 2.6seconds

# main function is necessary here to enable script as own program
# in such way a child process can be started (primarily for Windows)
def runRT(count):
    with LSLClient(info=info, host=host, wait_max=wait_max) as client:
        client_info = client.get_measurement_info()
        sfreq = int(client_info['sfreq'])
        epoch = client.get_data_as_epoch(n_samples=epoch_chunks)
        epoch.filter(8,14, method='fir', verbose=20)
        X = epoch.get_data() *1e-6  #n_epochs * n_channel * n_time_samples
        X=X[:,[1,3],:]
        print(X.shape)
        
        
print('Streams closed')

if __name__ == '__main__':
    count = 0
    while(True):
        time.sleep(waittime)
        x= threading.Thread(target = runRT, args=(count,))
        x.start()
        count+=1