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
from mne.datasets import eegbci
from mne.channels import make_standard_montage
from mne.filter import construct_iir_filter,create_filter

def getEpoch(eeg_data,channel,board_id):
    # Creating MNE objects from brainflow data arrays
    ch_types = ['eeg'] * len(channel)
    ch_names = BoardShim.get_eeg_names(board_id)
    sfreq = BoardShim.get_sampling_rate(board_id)
    info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)
    raw = mne.io.RawArray(eeg_data, info)
    raw_data = raw.copy()
    eegbci.standardize(raw_data)
    montage = mne.channels.make_standard_montage('standard_1005')
    raw_data.set_montage(montage)
    print(raw_data.info['ch_names'])
    raw_data.rename_channels(lambda x: x.strip('.'))
    print(raw_data.info['ch_names'])
    print(raw_data.info['sfreq'])
    
    #2 electrode        
    raw_data.pick_channels(['C3','C4'])
    
    #get epoch
    tmin, tmax = 0, 4
    event_id = dict(T1=0, T2=1)
    events = find_events(raw_data)
    print(events)
    '''
    picks = pick_types(raw_data.info, meg=False, eeg=True, stim=False, eog=False,
                       exclude='bads')
    reject_criteria = dict(eeg=100e-6)  #most frequency in this range is not brain components
    
    epochs = Epochs(raw_data, events, event_id, tmin, tmax, proj=True, picks=picks,
                    baseline=None,preload=True)
    labels = epochs.events[:, -1]
    '''
    '''
    # its time to plot something!
    raw.plot_psd(average=True)
    plt.savefig('psd.png')'''

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
    marker_channel = board.get_marker_channel(board)
    
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
    
    info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)
    raw = mne.io.RawArray(data, info)
    raw_data = raw.copy()
    eegbci.standardize(raw_data)
    montage = mne.channels.make_standard_montage('standard_1005')
    raw_data.set_montage(montage)
    
    print(raw_data.info['ch_names'])
    print(raw_data.info['sfreq'])
    print(raw_data)


def main():
    BoardShim.enable_dev_board_logger()

    parser = argparse.ArgumentParser()
    # use docs to check which parameters are required for specific board, e.g. for Cyton - set serial port
    parser.add_argument('--timeout', type=int, help='timeout for device discovery or connection', required=False,
                        default=0)
    parser.add_argument('--ip-port', type=int, help='ip port', required=False, default=0)
    parser.add_argument('--ip-protocol', type=int, help='ip protocol, check IpProtocolType enum', required=False,
                        default=0)
    parser.add_argument('--ip-address', type=str, help='ip address', required=False, default='')
    parser.add_argument('--serial-port', type=str, help='serial port', required=False, default='')
    parser.add_argument('--mac-address', type=str, help='mac address', required=False, default='')
    parser.add_argument('--other-info', type=str, help='other info', required=False, default='')
    parser.add_argument('--serial-number', type=str, help='serial number', required=False, default='')
    parser.add_argument('--board-id', type=int, help='board id, check docs to get a list of supported boards',
                        required=True)
    parser.add_argument('--file', type=str, help='file', required=False, default='')
    parser.add_argument('--master-board', type=int, help='master board id for streaming and playback boards',
                        required=False, default=BoardIds.NO_BOARD)
    parser.add_argument('--preset', type=int, help='preset for streaming and playback boards',
                        required=False, default=BrainFlowPresets.DEFAULT_PRESET)
    args = parser.parse_args()

    params = BrainFlowInputParams()
    params.ip_port = args.ip_port
    params.serial_port = args.serial_port
    params.mac_address = args.mac_address
    params.other_info = args.other_info
    params.serial_number = args.serial_number
    params.ip_address = args.ip_address
    params.ip_protocol = args.ip_protocol
    params.timeout = args.timeout
    params.file = args.file
    params.master_board = args.master_board
    params.preset = args.preset

    #record 1 time
    board = BoardShim(args.board_id, params)
    board.prepare_session()
    board.start_stream()
    for i in range(10):
        time.sleep(1)
        board.insert_marker(1)
    # data = board.get_current_board_data (256) # get latest 256 packages or less, doesnt remove them from internal buffer
    print("Data")
    data = board.get_board_data()
    # get all data and remove it from internal buffer
    board.stop_stream()
    board.release_session()
    
    #MNE process
    getdata(data,args.board_id,n_samples = 250)
    #getEpoch(eeg_data,eeg_channels,args.board_id)

if __name__ == "__main__":
    main()
    
    
    
    
'''    
    
  #marker
    print("Marker")
    # get row index which holds markers
    marker_channel = board.get_marker_channel(args.board_id)
    print(marker_channel)
    marker_data = data[marker_channel]
    print('Marker Data')
    print(data.shape)
    print(marker_data.shape)
    print(marker_data) 
    # demo how to convert it to pandas DF and plot data
    eeg_channels = BoardShim.get_eeg_channels(args.board_id)
    print(eeg_channels)
    eeg_data = data[eeg_channels, :]
    eeg_data = eeg_data / 1000000  # BrainFlow returns uV, convert to V for MNE
    
    # demo for data serialization using brainflow API, we recommend to use it instead pandas.to_csv()
    DataFilter.write_file(data, 'test.csv', 'w')  # use 'a' for append mode
    restored_data = DataFilter.read_file('test.csv')
    restored_df = pd.DataFrame(np.transpose(restored_data))
    print('Data From the File')
    print(restored_df.head(10))
    
    ch_names = BoardShim.get_eeg_names(args.board_id)
    print(ch_names)'''