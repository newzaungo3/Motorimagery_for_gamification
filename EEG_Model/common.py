import copy

import numpy as np

from tqdm import tqdm
from IPython.display import clear_output
import torch
import torch.nn.functional as F
from torch.utils.data import Dataset
from torch.utils.data.dataset import ConcatDataset as _ConcatDataset  # noqa
from torch.autograd import Variable
import torch.cuda as cuda
from mne.datasets import eegbci
import os
import mne
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from torch.utils.data import TensorDataset
from torch.utils.data import DataLoader,SubsetRandomSampler
from scipy import signal
from matplotlib.colors import TwoSlopeNorm
from mne.time_frequency import tfr_multitaper
import pandas as pd
import seaborn as sns
from live_detection.config import *


class ConcatDataset(_ConcatDataset):
    """
    Same as torch.utils.data.dataset.ConcatDataset, but exposes an extra
    method for querying the group structure (index if dataset
    each sample comes from)
    """
    def get_groups(self):
        """Return the group index of each sample
        Returns
        -------
        groups : array of int, shape (n_samples,)
            The group indices.
        """
        groups = [k * np.ones(len(d)) for k, d in enumerate(self.datasets)]
        return np.concatenate(groups)


class EpochsDataset(Dataset):
    """Class to expose an MNE Epochs object as PyTorch dataset
    Parameters
    ----------
    epochs_data : 3d array, shape (n_epochs, n_channels, n_times)
        The epochs data.
    epochs_labels : array of int, shape (n_epochs,)
        The epochs labels.
    transform : callable | None
        The function to eventually apply to each epoch
        for preprocessing (e.g. scaling). Defaults to None.
    """
    def __init__(self, epochs_data, epochs_labels, transform=None):
        assert len(epochs_data) == len(epochs_labels)
        self.epochs_data = epochs_data
        self.epochs_labels = epochs_labels
        self.transform = transform

    def __len__(self):
        return len(self.epochs_labels)

    def __getitem__(self, idx):
        X, y = self.epochs_data[idx], self.epochs_labels[idx]
        if self.transform is not None:
            X = self.transform(X)
        X = torch.as_tensor(X[None, ...])
        return X, y

def train(model, loader_train, loader_test, optimizer,criterion,device,wand,vail_loader= None,
          cross = False):
    # put model on cuda if not already
    device = torch.device(device)
    config = wand.config
    
    weights_name = config.weightname
    best_val_loss = + np.infty
    best_model = copy.deepcopy(model)
    train_loss = []
    valid_loss = [10,11]
    train_accuracy = []
    valid_accuracy = []
    
    old_loss = 100
    old_acc = 0
    valid_loss_vail = []
    
    for epoch in range(config.epochs):
        iter_loss = 0.0
        correct = 0
        iterations = 0

        model.train()

        for i, (items, classes) in enumerate(loader_train):
            items = Variable(items)
            classes = classes.type(torch.LongTensor)
            classes = Variable(classes)

            if cuda.is_available():
                items = items.to(device=device)
                classes = classes.to(device=device)

            optimizer.zero_grad()
            outputs = model(items)
            loss = criterion(outputs, classes)

            iter_loss += loss.item()
            loss.backward()
            optimizer.step()
            
            metrics = {"train/train_loss": loss}
            if i + 1 < config.num_step_per_epoch:
                # 🐝 Log train metrics to wandb 
                wand.log(metrics)
            
            #print(loss)
            _, predicted = torch.max(outputs.data, 1)
            correct += (predicted == classes.data).sum()
            iterations += 1

        train_loss.append(iter_loss/iterations)
        

        train_accuracy.append((100 * correct.float() / len(loader_train.dataset)))
        train_metrics = {"train/train_loss": iter_loss/iterations, 
                       "train/train_accuracy": (100 * correct.float() / len(loader_train.dataset))}
        
        wand.log({**metrics, **train_metrics})

        loss = 0.0
        correct = 0
        iterations = 0
        model.eval()
        
        for i, (items, classes) in enumerate(loader_test):
            items = Variable(items)
            classes = Variable(classes)
            
            if cuda.is_available():
                items = items.to(device=device)
                classes = classes.to(device=device)
            
            outputs = model(items)
            loss += criterion(outputs, classes).item()
            
            _, predicted = torch.max(outputs.data, 1)
            correct += (predicted == classes.data).sum()
            
            iterations += 1
        
        valid_loss.append(loss/iterations)
        correct_scalar = np.array([correct.clone().cpu()])[0]
        valid_accuracy.append(correct_scalar / len(loader_test.dataset) * 100.0)
        
        val_metrics = {"val/val_loss": loss/iterations, 
                       "val/val_accuracy": correct_scalar / len(loader_test.dataset) * 100.0}
        wand.log({**metrics, **val_metrics})

        epoch_acc = correct.double()/len(loader_test.dataset)
        if epoch+1 > 2 and valid_loss[-1] < old_loss and old_acc <= valid_accuracy[-1] :
                newpath = r'./save_weight/{}'.format(weights_name) 
                if not os.path.exists(newpath):
                    os.makedirs(newpath)
                torch.save(model.state_dict(),'./save_weight/{}/{:.4f}_{}_{:.4f}_{:.4f}'.format(weights_name,valid_loss[-1],weights_name,valid_loss[-1],valid_accuracy[-1]))
                old_loss = valid_loss[-1]  
                old_acc = valid_accuracy[-1]
        if (epoch % 100) ==0:
            print ('Epoch %d/%d, Tr Loss: %.4f, Tr Acc: %.4f, Val Loss: %.4f, Val Acc: %.4f'
                       %(epoch+1, config.epochs, train_loss[-1], train_accuracy[-1], valid_loss[-1], valid_accuracy[-1]))
         
        if cross :
                loss_vail = 0.0
                correct_vail = 0
                iterations_vail = 0
                model.eval()

                for i, (items, classes) in enumerate(vail_loader):
                    classes = classes.type(torch.LongTensor)
                    items = Variable(items)
                    classes = Variable(classes)

                    if cuda.is_available():
                        items = items.to(device=device)
                        classes = classes.to(device=device)


                    outputs = model(items)
                    loss_vail += criterion(outputs, classes).item()

                    _, predicted = torch.max(outputs.data, 1)

                    correct_vail += (predicted == classes.data).sum()
                    #print("correct : {}".format(classes.data))
                    #print("predicted : {}".format(predicted))
                    iterations_vail += 1

                valid_loss_vail.append(loss_vail/iterations_vail)
                correct_scalar = np.array([correct_vail.clone().cpu()])[0]
                valid_accuracy.append(correct_scalar / len(vail_loader.dataset) * 100.0)
                vali_metrics = {"val/val_loss": loss_vail/iterations, 
                        "val/val_accuracy": correct_scalar / len(loader_test.dataset) * 100.0}
                wand.log({**metrics, **vali_metrics})
                if (epoch % 100) ==0:
                    print ('Val Loss: {0}, Val Acc: {1}'.format(valid_loss_vail[-1], valid_accuracy[-1]))

    return train_loss,valid_loss,train_accuracy,valid_accuracy


class EEG:
    def __init__(self, path, subjects, runs):
        self.subpath = ''
        self.path = path
        print(path)
        self.subjects = subjects
        self.runs = runs
        
        # download data if does not exist in path.
        # self.load_data()
        self.data_to_raw()
    def filter(self, freq):
        raw = self.raw
        low, high = freq
        print(f">>> Apply filter.")
        self.raw.filter(low, high, fir_design='firwin', verbose=20)
        #self.raw.notch_filter(50,filter_length='auto', phase='zero')
        return  raw
    def raw_ica(self):
        raw = self.raw
        ica = mne.preprocessing.ICA(n_components=1, max_iter=100)
        ica.fit(raw)
        ica.exclude = [1, 2]  # details on how we picked these are omitted here
        ica.plot_properties(raw, picks=ica.exclude)
        ica.apply(raw)
        print('ICA DONE ????')
        return  raw
        
    def data_to_raw(self):
        fullpath = os.path.join(self.path, *self.subpath.split(sep='/'))
        #print(f">>> Extract all subjects from: {fullpath}.")
        extension = "fif"
        raws = []
        count = 1
        for i, subject in enumerate(self.subjects):
            sname = f"S{str(subject).zfill(3)}".upper()
            
            for j, run in enumerate(self.runs):
                rname = f"{sname}R{str(run).zfill(2)}".upper()
                path_file = os.path.join(fullpath, sname, f'{rname}.{extension}')
                #print(path_file)
                #print(f"Loading file #{count}/{len(self.subjects)*len(self.runs)}: {f'{rname}.{extension}'}")
                raw = mne.io.read_raw_fif( path_file , preload=True, verbose='WARNING' )
                raws.append(raw)
                count += 1

        raw = mne.io.concatenate_raws(raws)
        eegbci.standardize(raw)
        montage = mne.channels.make_standard_montage('standard_1020')
        raw.set_montage(montage)
        print(raw.info['ch_names'])
        print(raw.info['sfreq'])
        raw.pick_channels(['C3','C4','STIM MARKERS'])
        print(raw.info['ch_names'])
        self.raw = raw
        return self.raw

    def get_X_y(self,epochs,tmin=0,tmax=4):
        
        #epochs=epochs.resample(160)
            #events , event_id=self.create_epochs()
        self.X = epochs.get_data()
        self.y = epochs.events[:, -1]-1
        return self.X, self.y 
    
    def epochs(self,raw,tmin,tmax,baseline):
        events = mne.find_events(raw, stim_channel='STIM MARKERS')
        epochs = mne.Epochs(
        raw,
        events,
        event_id=[1,2,3],
        tmin=tmin,
        tmax=tmax,
        picks="data",
        on_missing='warn',
        baseline=baseline,
        preload=True
            )
        return epochs


class Physionet:
    def __init__(self, path, base_url, subjects, runs):
        self.subpath = ''
        self.path = path
        print(path)
        self.base_url = base_url
        self.subjects = subjects
        self.runs = runs
        
        # download data if does not exist in path.
        # self.load_data()
        self.data_to_raw()
    
    def load_data(self):
        print(f">>> Start download from: {self.base_url}.")
        print(f"Downloading files to: {self.path}.")
        for subject in self.subjects:
            eegbci.load_data(subject,self.runs,path=self.path,base_url=self.base_url)
        print("Done.")
        return self.raw
    def filter(self, freq):
        raw = self.raw
        low, high = freq
        print(f">>> Apply filter.")
        self.raw.filter(low, high, fir_design='firwin', verbose=20)
        #self.raw.notch_filter(50,filter_length='auto', phase='zero')
        return  raw
    def raw_ica(self):
        raw = self.raw
        ica = mne.preprocessing.ICA(n_components=1, max_iter=100)
        ica.fit(raw)
        ica.exclude = [1, 2]  # details on how we picked these are omitted here
        ica.plot_properties(raw, picks=ica.exclude)
        ica.apply(raw)
        print('ICA DONE ????')
        return  raw
        
    def get_events(self):
        event_id = dict(T1=0, T2=1) # the events we want to extract
        events, event_id = mne.events_from_annotations(self.raw, event_id=event_id)
        return events, event_id
    
    def get_epochs(self, events, event_id):
        picks = mne.pick_types(self.raw.info, eeg=True, exclude='bads')
        tmin = 0
        tmax = 4
        epochs = mne.Epochs(self.raw, events, event_id, tmin, tmax, proj=True, 
                            picks=picks, baseline=None, preload=True)
        return epochs
    
    def data_to_raw(self):
        fullpath = os.path.join(self.path, *self.subpath.split(sep='/'))
        #print(f">>> Extract all subjects from: {fullpath}.")
        extension = "fif"
        raws = []
        count = 1
        for i, subject in enumerate(self.subjects):
            sname = f"S{str(subject).zfill(3)}".upper()
            
            for j, run in enumerate(self.runs):
                rname = f"{sname}R{str(run).zfill(2)}".upper()
                path_file = os.path.join(fullpath, sname, f'{rname}.{extension}')
                #print(path_file)
                #print(f"Loading file #{count}/{len(self.subjects)*len(self.runs)}: {f'{rname}.{extension}'}")
                raw = mne.io.read_raw_fif( path_file , preload=True, verbose='WARNING' )
                raws.append(raw)
                count += 1

        raw = mne.io.concatenate_raws(raws)
        eegbci.standardize(raw)
        montage = mne.channels.make_standard_montage('standard_1005')
        raw.set_montage(montage)
        print(raw.info['ch_names'])
        print(raw.info['sfreq'])
        self.raw = raw
    
    def create_epochs(self):
        print(">>> Create Epochs.")
        
        events, event_id = self.get_events()
        self.epochs = self.get_epochs(events, event_id)
        print("Done.")
        return events , event_id
    
    def get_X_y(self):
        if self.epochs is None:
            events , event_id ,epochs=self.create_epochs()
        self.X = self.epochs.get_data()
        self.y = self.epochs.events[:, -1]
        return self.X, self.y
    
    
           
def getepoch(raws,trial_duration, calibration_duration,reject_bad=False,on_missing='warn'):
    #reject_criteria = dict(eeg=100e-6)  # 100 µV
    #flat_criteria = dict(eeg=1e-6)  # 1 µV
    epochs_list = []
    raws = [raws]
    print(len(raws))
    for raw in raws:
        print(raw)
        events = mne.find_events(raw)
        epochs = mne.Epochs(
            raw,
            events,
            event_id=[1,2,3],
            tmin=-calibration_duration,
            tmax=trial_duration,
            picks="data",
            on_missing=on_missing,
            baseline=None,
            preload=True
        )
        
        epochs_list.append(epochs)
    epochs = mne.concatenate_epochs(epochs_list)
    labels = epochs.events[:,-1]
    
    print(f'Found {len(labels)} epochs')
    print(epochs)
    print(labels)

    return epochs.get_data(),epochs,labels

        
        
def do_plot(train_loss, valid_loss,ty):
    if ty == "loss":
        plt.figure(figsize=(10,10))
        
        plt.plot(train_loss, label='train_loss')
        plt.plot(valid_loss, label='valid_loss')
        plt.title('loss {}'.format(iter))
        plt.legend()
        plt.show()
    if ty == "acc":
        plt.figure(figsize=(10,10))
        
        plot_ty=torch.tensor(train_loss, device = 'cpu')
        plat_va=torch.tensor(valid_loss, device = 'cpu')
        plt.plot(plot_ty, label='train_acc')
        plt.plot(plat_va, label='valid_acc')
        plt.title('acc {}'.format(iter))
        plt.legend()
        plt.show()
        
        
def setup_dataflow(X_tensor,y_tensor, train_idx, val_idx):
    #train_sampler = SubsetRandomSampler(train_idx)
    #val_sampler = SubsetRandomSampler(val_idx)
    train_datasets = TensorDataset(X_tensor[train_idx], y_tensor[train_idx])
    val_datasets = TensorDataset(X_tensor[val_idx], y_tensor[val_idx])
    
    train_loader = DataLoader(train_datasets, batch_size=32)
    val_loader = DataLoader(val_datasets, batch_size=32)

    return train_loader, val_loader

def create_dataloader(X, y, batch_size):
    X_tensor = torch.tensor(X).float()
    y_tensor = torch.tensor(y).long()
    dataset_tensor = TensorDataset(X_tensor, y_tensor)
    dl = torch.utils.data.DataLoader(dataset_tensor, batch_size=batch_size, shuffle=True)
    return dl

def Erd_indi_Plot(epochs,trial):
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
    
    newpath = r'./save_weight/{}'.format(PARTICIPANT_ID) 
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    g.savefig(f'./ERD/{PARTICIPANT_ID}/{NAME}_{trial}.png')
    
    plt.title('ERD PLOT')
 
    plt.show()

