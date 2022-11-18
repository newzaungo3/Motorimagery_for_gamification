from utils import *
from data_utils import *
import psychtoolbox as ptb
from psychopy import sound, visual,core
import pygame
sound_file = './sound/Left.wav'

import sounddevice as sd
sd.play(sound_file, 44100)

randomStimuli(20)