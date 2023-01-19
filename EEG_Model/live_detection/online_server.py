from tokenize import Double
from typing import Union,List,Dict
from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import requests
import random
from data_utils import NAME,getdata,getepoch
from model import ConvNet,gamenet
import torch
import logging
import time 
from config import *

app = FastAPI()
logging.basicConfig(filename=NAME)
logging.getLogger().setLevel(logging.DEBUG)
class Item(BaseModel):
    name: str
    data: List[List[float]]

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.post("/items/")
async def create_item(item: Dict): 
    #Receive Epoch data from LSL
    train_epochs = np.array(item['X'])
    labels = np.array(item['y'])
    print(train_epochs.shape)
    print(labels.shape)
    
    #Predict
    path = '/root/EEG_Model/save_weight/Faye_S10_Finetune_MI/0.7203_Faye_S10_Finetune_MI_0.7203_43.4783'
    model = ConvNet()
    model.load_state_dict(torch.load(path))
    model.eval()
    X_t,y_train= train_epochs.copy(),labels
    
    #add new dimension
    #X_train = X_t[:,:,np.newaxis,:]
    #X_t=X_t[:,:,int(0.25*250):int(1750-(250*1))]
    #X_t=X_t[:,:,:]
    #X = X[:, np.newaxis,:,:]


    X_tensor = torch.from_numpy(X_t).float()
    y_tensor = torch.from_numpy(y_train).long()


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
    logging.info(f"Filename: {item['name']}")
    logging.info(f"Actual: {y_tensor[0].item()}")
    logging.info(f"Predicted: {unity_output}")
    logging.info(f"Condition: {condition}")
    return {"result":1}