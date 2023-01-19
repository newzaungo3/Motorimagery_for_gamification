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

def train(model, loader_train, loader_valid, optimizer,criterion,device,wand):
    # put model on cuda if not already
    device = torch.device(device)
    config = wand.config
    
    weights_name = config.weightname
    best_val_loss = + np.infty
    best_model = copy.deepcopy(model)
    best_accracy = 0
    train_loss = []
    valid_loss = []
    train_accuracy = []
    valid_accuracy = []
    
    for epoch in range(config.epochs):
        print("\nStarting epoch {} / {}".format(epoch + 1, config.epochs))
        #train_loss,train_acc = _do_train(model, loader_train, optimizer, criterion, device)
        #val_loss,val_acc = _validate(model, loader_valid, criterion, device)
        iter_loss = 0.0
        correct = 0
        iterations = 0
        example_ct = 0
        model.train()
        
        for i, (items, classes) in enumerate(loader_train):
            items = Variable(items)
            classes = Variable(classes)
            
            if cuda.is_available():
                items = items.to(device=device)
                classes = classes.to(device=device)
            
            optimizer.zero_grad()
            outputs = model(items)
            loss = criterion(outputs, classes)
            #print(outputs)
            iter_loss += loss.item()
            loss.backward()
            optimizer.step()
            #print(loss)
            
            example_ct += len(items)
            metrics = {"train/train_loss": loss}
            if i + 1 < config.num_step_per_epoch:
                # 🐝 Log train metrics to wandb 
                wand.log(metrics)
             
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
        
        for i, (items, classes) in enumerate(loader_valid):
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
        valid_accuracy.append(correct_scalar / len(loader_valid.dataset) * 100.0)
        
        val_metrics = {"val/val_loss": loss/iterations, 
                       "val/val_accuracy": correct_scalar / len(loader_valid.dataset) * 100.0}
        wand.log({**metrics, **val_metrics})

        epoch_acc = correct.double()/len(loader_valid.dataset)
        if valid_loss[-1] < best_val_loss and epoch_acc > best_accracy:
            best_val_loss = valid_loss[-1]
            best_accracy = epoch_acc
            best_model_wts = copy.deepcopy(model.state_dict())
            model.load_state_dict(best_model_wts)
            torch.save(model.state_dict(), f"./save_weight/{weights_name}-{epoch}-bestacc{best_accracy * 100:.2f}.pth")
        
        '''# model saving
        if (np.mean(val_loss) < best_val_loss) and (val_acc > best_accracy):
            print("\nbest val loss {:.4f} -> {:.4f}".format(
                best_val_loss, np.mean(val_loss)))
            best_val_loss = np.mean(val_loss)
            best_model = copy.deepcopy(model)
            best_accracy = val_acc
            torch.save(best_model.state_dict(), f"./save_weight/{weights_name}-{epoch}-bestacc{best_accracy:.2f}.pth")
            waiting = 0
        else:
            print("Waiting += 1")
            waiting += 1

        # model early stopping
        if waiting >= patience:
            print("Stop training at epoch {}".format(epoch + 1))
            print("Best val loss : {:.4f}".format(best_val_loss))
            break'''
        print ('Epoch %d/%d, Tr Loss: %.4f, Tr Acc: %.4f, Val Loss: %.4f, Val Acc: %.4f'
               %(epoch+1, config.epochs, train_loss[-1], train_accuracy[-1], valid_loss[-1], valid_accuracy[-1]))
         
    return best_model,train_loss,valid_loss,train_accuracy,valid_accuracy


class EEG:
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
        raw.pick_channels(['C3','C4'])
        print(raw.info['ch_names'])
        self.raw = raw
    
    def get_X_y_cross(self):
        raw = self.raw
        baseline = (0,2)
        events = mne.find_events(raw)
        
        epochs = mne.Epochs(
        raw,
        events,
        event_id=[1,2,3],
        tmin=0,
        tmax=4,
        picks="data",
        on_missing='warn',
        baseline=baseline,
            preload=True
    )
        #epochs=epochs.resample(160)
        self.X = epochs.get_data()
        self.y = epochs.events[:, -1]
        return self.X, self.y 

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