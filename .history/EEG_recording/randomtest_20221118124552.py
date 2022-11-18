from utils import *
from data_utils import *
from psychopy import sound

sound_file = './sound/Left.mp3'
hello = sound.Sound(sound_file)
hello.play()
randomStimuli(20)