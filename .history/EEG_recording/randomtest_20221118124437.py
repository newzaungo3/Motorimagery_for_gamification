from utils import *
from data_utils import *
from psychopy import sound
import psychtoolbox as ptb
sound_file = '\sound\Left.mp3'
hello = sound.Sound(sound_file)
now = ptb.GetSecs()
hello.play(when=now+0.5)  # play in EXACTLY 0.5s
randomStimuli(20)