import torch   
from torch import nn  
import torch.nn.functional as F  

class hopefullnet(nn.Module):
    def __init__(self):
        super(hopefullnet,self).__init__()
        
        self.L1 = nn.Sequential(
            #in_channel = 2
            #out_channel or Filter size = 32
            #kernel size = 20
            #stride = 1
            #padding = Same
            #Relu
            nn.Conv1d(2,32, kernel_size = 20, stride = 1 , padding = 'same'),
            nn.ReLU(),
            nn.BatchNorm1d(32)
        )
        self.L2 = nn.Sequential(
            #in_channel = 32
            #out_channel or Filter size = 32
            #kernel_size =20
            #stride = 1
            #padding = valid
            #Relu
            nn.Conv1d(32,32,kernel_size=20,stride = 1, padding = 'valid'),
            nn.ReLU(),
            nn.BatchNorm1d(32)
        )
        self.L3 = nn.Conv1d(32,32,kernel_size=6,stride = 1, padding='valid')
        self.pooling = nn.AvgPool1d(kernel_size=2,stride = 2)
        self.L4 = nn.Sequential(
            #in_channel = 32
            #out_channel = 32
            #kernel_size = 6
            #stride = 1
            #padding = 'valid'
            #relu
            nn.Conv1d(32,32,kernel_size = 6, stride = 1 , padding = 'valid'),
        )
        
        self.fully = nn.Sequential(
            nn.Flatten(),
            nn.ReLU(nn.Linear(9696,2)),
            nn.Dropout(0.5),
            nn.ReLU(nn.Linear(296,148)),
            nn.Dropout(0.5),
            nn.ReLU(nn.Linear(148,74)),
            nn.Dropout(0.5),
            nn.Linear(74,2)
        )
        self.fully1 = nn.Linear(9696,296)
        self.fully2 = nn.Linear(296,148)
        self.fully3 = nn.Linear(148,74)
        self.fully4 = nn.Linear(74,2)
        self.flatten = nn.Flatten()
        self.drop_out = nn.Dropout(0.5)
    def forward(self,x):
        
        out = self.L1(x)
        out = self.L2(out)
        out = self.drop_out(out)
        out = self.L3(out)
        out = self.pooling(out)
        out = self.L4(out)
        out = self.drop_out(out)
        out = self.flatten(out)
        
        out = F.relu(self.fully1(out))
        out = self.drop_out(out)
        out = F.relu(self.fully2(out))
        out = self.drop_out(out)
        out = F.relu(self.fully3(out))
        out = self.drop_out(out)
        out = F.softmax(self.fully4(out))
        #out = self.fully(out)
        
        return out