from utils import *
from data_utils import *

image_list,numIm_list,video_list,numVi_list = randomStimuli(20)
print(video_list)
print(numVi_list)

dicts = [
 { "left1":'video/left/left.avi', "right1": 'video/right/right.avi' },
 { "left2": 'video/left/left2.avi', "right2": 'video/right/right2.avi' },
 ]

print(dicts[0]["left1"])
print(4/2)