from torchsummary import summary
from model import gamenet
import torch
device = 'cuda'
#model = CNN()
#model = CNN2D()
#model = ConvNet()
#model = hopefullnet()
path = '/root/EEG_Model/save_weight/0.6255_OurData_CNN_2ch_2class_S15_0.6255_77.7778'
model = gamenet()
model.load_state_dict(torch.load(path))
#print(model)

#summary(model.cuda(), ( 2 , 641),32)
summary(model.cuda(), ( 2,1, 1001),1)