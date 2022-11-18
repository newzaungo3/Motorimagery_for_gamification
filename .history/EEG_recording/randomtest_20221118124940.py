from utils import *
from data_utils import *
import psychtoolbox as ptb
from psychopy import sound, visual


sound_file = './sound/Left.mp3'


mySound = sound.Sound(sound_file)

win = visual.Window()
win.flip()
nextFlip = win.getFutureFlipTime(clock='ptb')

mySound.play(when=nextFlip)  # sync with screen refresh
randomStimuli(20)