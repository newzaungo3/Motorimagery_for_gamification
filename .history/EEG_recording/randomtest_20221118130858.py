from utils import *
from data_utils import *
import psychtoolbox as ptb
from psychopy import sound, visual,core
import pygame
sound_file = './sound/Left.wav'

import sounddevice as sd
import soundfile as sf

data, fs = sf.read('sound_file')
sd.play(data, fs)
sd.wait()

randomStimuli(20)