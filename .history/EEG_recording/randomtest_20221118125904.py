from utils import *
from data_utils import *
import psychtoolbox as ptb
from psychopy import sound, visual,core
from psychopy.sound import soundPTB


sound_file = './sound/Left.mp3'
'''pygame.mixer.init()
pygame.mixer.music.load(sound_file)
pygame.mixer.music.play()'''
s = sound.Sound(value=sound_file, secs=1) 
s = soundPTB(value= sound_file)
 
s.play()


randomStimuli(20)