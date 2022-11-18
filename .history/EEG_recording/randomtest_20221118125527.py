from utils import *
from data_utils import *
import psychtoolbox as ptb
from psychopy import sound, visual,core


sound_file = './sound/Left.mp3'
'''pygame.mixer.init()
pygame.mixer.music.load(sound_file)
pygame.mixer.music.play()'''
s = sound.Sound(value="C", secs=0.5) 
 
s.play()
core.wait(4.0)

randomStimuli(20)