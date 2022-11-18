from utils import *
from data_utils import *
import psychtoolbox as ptb
from psychopy import sound, visual,core
import pygame
sound_file = './sound/Left.wav'

from playsound import playsound
playsound(sound_file)
'''s = sound.Sound(value=sound_file, secs=1) 
s.play()'''

randomStimuli(20)