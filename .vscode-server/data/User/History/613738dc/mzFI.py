from torchsummary import summary
from model import gamenet
import torch
device = 'cuda'
#model = CNN()
#model = CNN2D()
#model = ConvNet()
#model = hopefullnet()
path = '/root/EEG_Model/save_weight/0.33522388339042664_OurData_S004_GAMENET_2ch_2class_IM_0.3352_100.0000'
model = gamenet()
model.load_state_dict(torch.load(path))
#print(model)

#summary(model.cuda(), ( 2 , 641),32)
summary(model.cuda(), ( 1,2, 1001),1)