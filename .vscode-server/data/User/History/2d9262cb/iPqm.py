from tokenize import Double
from typing import Union,List
from fastapi import FastAPI,Body
from pydantic import BaseModel
import numpy as np
import requests
import random
from data_utils import *
from model import ConvNet
import torch
app = FastAPI()
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
    train_epochs,epochs_raw_data,labels = getepoch(raw,4,10)
    print(train_epochs)
    #Predict
    path = '/root/EEG_Model/save_weight/ourdata_CNN_2ch_2class_cross'
    model = ConvNet()
    model.load_state_dict(torch.load(path))

    #Send to unity
    if item.data != None:
        rand = random.randint(1,3)
        if rand == 1:
            condition = 'left'
        if rand == 2:
            condition = 'right'
        if rand == 3:
            condition = '0'
        print(f"sending: {condition}")
        #requests.get(f"http://host.docker.internal:8001/JoyController?msg={condition}")
    return {"result":1}