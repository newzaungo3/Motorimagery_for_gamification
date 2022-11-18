from utils import *
from data_utils import *
import psychtoolbox as ptb
from psychopy import sound, visual


sound_file = './sound/Left.mp3'
mySound = sound.Sound('A')
now = ptb.GetSecs()
mySound.play(when=now)  # play in EXACTLY 0.5s

randomStimuli(20)