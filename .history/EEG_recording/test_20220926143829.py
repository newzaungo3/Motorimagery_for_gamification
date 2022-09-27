from psychopy import visual, core, event,monitors
from config import *
file = 'left.mp4'
mywin = visual.Window(SCREEN_SIZE, color="black",monitor="Experiment Monitor" , units='norm') 
core.wait(STIM_BLINK_TIME)
video = visual.MovieStim(mywin,file,volume=0)
video.draw()
mywin.flip()
core.wait(STIM_BLINK_TIME)