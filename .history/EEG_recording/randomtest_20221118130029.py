from utils import *
from data_utils import *
import psychtoolbox as ptb
from psychopy import sound, visual,core
import pygame
sound_file = './sound/Left.mp3'
pygame.mixer.init()
pygame.mixer.music.load(sound_file)
pygame.mixer.music.play()

'''s = sound.Sound(value=sound_file, secs=1) 
s.play()'''

randomStimuli(20)