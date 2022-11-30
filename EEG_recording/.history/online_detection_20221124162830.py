import matplotlib.pyplot as plt
import time
from mne.datasets import sample
from mne.io import read_raw_fif
import threading
import mne as mne
from mne_realtime import LSLClient, MockLSLStream

print(__doc__)

######HYPERPARAMETERS
epoch_width = 3.5  #2.6
waittime = 0.2
threshold = 4  #3 out of 5 epochs
num_of_epochs = 5
#########


#defining the stream data format
sfreq = 250
ch_names = ["Fp1", "Fp2", "C3", "C4", "P3","P4","O1", "O2"]
ch_types = ['eeg'] * 8
info = mne.create_info(ch_names, sfreq, ch_types = ch_types)
# this is the host id that identifies your stream on LSL
host = 'OpenBCI'
wait_max = 5
# For this example, let's use the mock LSL stream.
_, ax = plt.subplots(1)
n_epochs = 5

# main function is necessary here to enable script as own program
# in such way a child process can be started (primarily for Windows)
def runRT(count):
    with LSLClient(info=info, host=host, wait_max=wait_max) as client:
        client_info = client.get_measurement_info()
        sfreq = int(client_info['sfreq'])

        # let's observe ten seconds of data
        for ii in range(n_epochs):
            print('Got epoch %d/%d' % (ii + 1, n_epochs))
            plt.cla()
            epoch = client.get_data_as_epoch(n_samples=sfreq)
            epoch.average().plot(axes=ax)
            plt.pause(1.)
        plt.draw()
print('Streams closed')

if __name__ == '__main__':
    count = 0
    while(True):
        time.sleep(waittime)
        x= threading.Thread(target = runRT, args=(count,))
        x.start()
        count+=1