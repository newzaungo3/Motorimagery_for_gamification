import copy

import numpy as np

from tqdm import tqdm

import torch
import torch.nn.functional as F
from torch.utils.data import Dataset
from torch.utils.data.dataset import ConcatDataset as _ConcatDataset  # noqa


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


def _do_train(model, loader, optimizer, criterion, device):
    iter_loss = 0.0
    train_acc = 0.0
    # training loop
    model.train()
    pbar = tqdm(loader)
    train_loss = np.zeros(len(loader))
    accuracy = 0.
    for idx_batch, (batch_x, batch_y) in enumerate(pbar):
        
        optimizer.zero_grad()
        batch_x = batch_x.to(device=device, dtype=torch.float32)
        batch_y = batch_y.to(device=device, dtype=torch.int64)

        output = model(batch_x)
        loss = criterion(output, batch_y)
        iter_loss += loss.item()
        loss.backward()
        optimizer.step()
        
        #accuracy
        _, top_class = output.topk(1, dim=1)
        top_class = top_class.flatten()
        accuracy += \
                torch.sum((batch_y == top_class).to(torch.float32))
        
        train_loss[idx_batch] = loss.item()
        pbar.set_description(
            desc="avg train loss: {:.2f}".format(
                np.mean(train_loss[:idx_batch + 1])))
    accuracy = accuracy / len(loader.dataset) *100
    print("---  Accuracy Training set : %.2f %%" % accuracy.item(), "\n")
    return train_loss,accuracy


def _validate(model, loader, criterion, device):
    # validation loop
    pbar = tqdm(loader)
    val_loss = np.zeros(len(loader))
    accuracy = 0.
    with torch.no_grad():
        model.eval()

        for idx_batch, (batch_x, batch_y) in enumerate(pbar):
            batch_x = batch_x.to(device=device, dtype=torch.float32)
            batch_y = batch_y.to(device=device, dtype=torch.int64)
            output = model.forward(batch_x)

            loss = criterion(output, batch_y)
            val_loss[idx_batch] = loss.item()

            _, top_class = output.topk(1, dim=1)
            top_class = top_class.flatten()
            # print(top_class.shape, batch_y.shape)
            accuracy += \
                torch.sum((batch_y == top_class).to(torch.float32))

            pbar.set_description(
                desc="avg val loss: {:.2f}".format(
                    np.mean(val_loss[:idx_batch + 1])))

    accuracy = accuracy / len(loader.dataset) * 100
    print("---  Accuracy Validation set: %.2f %%" % accuracy.item(), "\n")
    return np.mean(val_loss),accuracy


def train(model, loader_train, loader_valid, optimizer,criterion, n_epochs, patience,
          device,wname):
    """Training function
    Parameters
    ----------
    model : instance of nn.Module
        The model.
    loader_train : instance of Sampler
        The generator of EEG samples the model has to train on.
        It contains n_train samples
    loader_valid : instance of Sampler
        The generator of EEG samples the model has to validate on.
        It contains n_val samples. The validation samples are used to
        monitor the training process and to perform early stopping
    optimizer : instance of optimizer
        The optimizer to use for training.
    criterion : instance of loss function
    n_epochs : int
        The maximum of epochs to run.
    patience : int
        The patience parameter, i.e. how long to wait for the
        validation error to go down.
    device : str | instance of torch.device
        The device to train the model on.
    wname : str | weights to save model.
    Returns
    -------
    best_model : instance of nn.Module
        The model that lead to the best prediction on the validation
        dataset.
    """
    # put model on cuda if not already
    device = torch.device(device)
    # model.to(device)
    
    # define criterion
    #criterion = F.nll_loss
    #criterion = torch.nn.CrossEntropyLoss()
    weights_name = wname
    best_val_loss = + np.infty
    best_model = copy.deepcopy(model)
    best_accracy = 0
    waiting = 0
    train_arr = []
    valid_arr = []

    for epoch in range(n_epochs):
        print("\nStarting epoch {} / {}".format(epoch + 1, n_epochs))
        train_loss,train_acc = _do_train(model, loader_train, optimizer, criterion, device)
        val_loss,val_acc = _validate(model, loader_valid, criterion, device)
        train_arr.append(train_loss[0])
        valid_arr.append(val_loss)
        
        
        # model saving
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
            break

    return best_model,train_arr,valid_arr