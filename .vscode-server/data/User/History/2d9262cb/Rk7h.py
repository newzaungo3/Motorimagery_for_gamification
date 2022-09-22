from tokenize import Double
from typing import Union,List
from fastapi import FastAPI,Body
from pydantic import BaseModel
import numpy as np
import requests
import random
from data_utils import *
from model import ConvNet,gamenet
import torch
import logging

app = FastAPI()
logging.getLogger().setLevel(logging.DEBUG)
class Item(BaseModel):
    name: str
    data: List[List[float]]

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.post("/items/")
async def create_item(item: Item):
    #print(item.data)
    print(type(item.data))
    print(np.array(item.data).shape)
    data = np.array(item.data)
    #Convert to mne data
    raw = getdata(data,0,n_samples=250)
    train_epochs,epochs_raw_data,labels = getepoch(raw,4,0)
    print(epochs_raw_data)
    print(epochs_raw_data.event_id)
    
    #Predict
    path = '/root/EEG_Model/save_weight/0.02273804508149624_OurData_S004_CNN_2ch_2class_IM_0.0227_100.0000'
    model = ConvNet()
    model.load_state_dict(torch.load(path))
    X_tensor = torch.from_numpy(train_epochs).float()
    y_tensor = torch.from_numpy(labels).long()
    print(X_tensor.shape)
    print(y_tensor)
    output = model(X_tensor)
    print("Actual:{}".format(str(y_tensor)))

    _, predicted = torch.max(output, 1)
    print("Predicted:{}".format(str(predicted)))
    unity_output = predicted[0].item()
    
    #Send to unity
    if unity_output != None:
        
        if unity_output == 0:
            condition = 'left'
        elif unity_output == 1:
            condition = 'right'
        else:
            condition = '0'
        print(f"sending: {condition}")
        requests.get(f"http://host.docker.internal:4200/JoyController?msg={condition}")
        
    return {"result":1}