'''from turtle import left
from psychopy import visual, core, event,monitors
from psychopy.visual import vlcmoviestim
from config import *
import vlc
file = 'video/left/left.avi'
mywin = visual.Window(SCREEN_SIZE,monitor="Experiment Monitor") 
video = vlcmoviestim.VlcMovieStim(mywin,file)
video.loadMovie(file)
video.setVolume(0)
video.play()

while True:
    video.draw(mywin)
    mywin.flip()
    print(video.frameTime)
    if video.frameTime >= 4:
        break
    if video.isFinished:
        break
        
     '''
     
from data_utils import randomStimuli

randomStimuli()
