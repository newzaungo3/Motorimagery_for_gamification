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