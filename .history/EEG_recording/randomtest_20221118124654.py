from utils import *
from data_utils import *
from psychopy.sound import sound
import psychtoolbox as ptb

sound_file = './sound/Left.mp3'
mySound = sound.Sound('A')
now = ptb.GetSecs()
mySound.play(when=now+0.5)  # play in EXACTLY 0.5s
randomStimuli(20)