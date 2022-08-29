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
from mne import Epochs, pick_types, events_from_annotations
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
    events, event_id = events_from_annotations(raw_data,event_id='auto')
    print(events)
    print(event_id)
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
    board.start_stream ()
    for i in range(10):
        time.sleep(1)
        board.insert_marker(1)
    # data = board.get_current_board_data (256) # get latest 256 packages or less, doesnt remove them from internal buffer
    print("Data")
    data = board.get_board_data()  # get all data and remove it from internal buffer
    board.stop_stream()
    board.release_session()

    print(data)
    print(type(data))
    df = pd.DataFrame(np.transpose(data))
    print('Data From the Board')
    print(df.head(10))
    
    # demo for data serialization using brainflow API, we recommend to use it instead pandas.to_csv()
    DataFilter.write_file(data, 'test.csv', 'w')  # use 'a' for append mode
    restored_data = DataFilter.read_file('test.csv')
    restored_df = pd.DataFrame(np.transpose(restored_data))
    print('Data From the File')
    print(restored_df.head(10))
    
    
    #get marker
    marker_list = board.get_marker_channel(args.board_id)
    print("Marker")
    print(marker_list)
    
    # demo how to convert it to pandas DF and plot data
    eeg_channels = BoardShim.get_eeg_channels(args.board_id)
    print(eeg_channels)
    eeg_data = data[eeg_channels, :]
    eeg_data = eeg_data / 1000000  # BrainFlow returns uV, convert to V for MNE
    df = pd.DataFrame(np.transpose(data))
    plt.figure()
    df[eeg_channels].plot(subplots=True)
    plt.savefig('before_processing.png')
    print(df.index)
    print(df.columns)
    #MNE process
    getEpoch(eeg_data,eeg_channels,args.board_id)

    
    

if __name__ == "__main__":
    main()