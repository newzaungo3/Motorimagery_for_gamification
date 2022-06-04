import torch 
from torch import nn  
import torch.nn.functional as F  

class CNN2D(nn.Module):
    def __init__(self):
        super(CNN2D, self).__init__()
        self.layer1 = nn.Sequential(
            #in_channel = 1
            #out_channel = 25
            #padding = (kernel_size - 1) / 2 = 2
            nn.Conv2d(1,25,kernel_size = 3,stride = 1, padding = 1),
            nn.LeakyReLU(),
            nn.Dropout2d(0.5)  
            )
        self.layer2 = nn.Sequential(
            #in_channel = 1
            #out_channel = 16
            #padding = (kernel_size - 1) / 2 = 2
            nn.Conv2d(25,25,kernel_size = 4, stride = 1, padding = 1),
            nn.BatchNorm2d(25,False),
            nn.LeakyReLU()
        )
        self.layer3 = nn.Sequential(
            nn.Conv2d(25,50,kernel_size=3,stride=1,padding=1),
            nn.LeakyReLU(),
            nn.Dropout2d(0.5)
        )
        self.layer4 = nn.Sequential(
            nn.Conv2d(50,100,kernel_size=3,stride=1,padding=1),
            nn.BatchNorm2d(100,False),
            nn.LeakyReLU(),
            nn.Dropout2d(0.5)
        )
        self.layer5 = nn.Sequential(
            nn.Conv2d(100,200,kernel_size=3,stride=1,padding=1),
            nn.BatchNorm2d(200,False),
            nn.LeakyReLU(),
            nn.Dropout2d(0.5)
        )
        
        self.fully = nn.Sequential(
            nn.Flatten(),
            nn.Linear(2400,2)
        )
        
        self.maxpooling1 = nn.MaxPool2d(kernel_size=1,stride = 3)
        self.maxpooling2 = nn.MaxPool2d(kernel_size=1,stride = 2)
        
    def forward(self,x):
        out = self.layer1(x)
        #print("layer1: " + str(out.shape))
        out = self.layer2(out)
        #print("layer2: " + str(out.shape))
        out = self.maxpooling1(out)
        #print("Maxpooling: " + str(out.shape))
        out = self.layer3(out)
        #print("layer3: " + str(out.shape))
        out = self.maxpooling1(out)
        #print("Maxpooling: " + str(out.shape))
        out = self.layer4(out)
        #print("layer4: " + str(out.shape))
        out = self.maxpooling1(out)
        #print("Maxpooling: " + str(out.shape))
        out = self.layer5(out)
        #print("layer5: " + str(out.shape))
        out = self.maxpooling2(out)
        #print("Maxpooling: " + str(out.shape))
        out = self.fully(out)
        #print(out.shape)
        return out