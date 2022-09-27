from psychopy import visual, core, event,monitors
from config import *
file = 'left.avi'
mywin = visual.Window(SCREEN_SIZE, color="black",monitor="Experiment Monitor" , units='norm') 
video = visual.MovieStim(mywin,file,volume=0,loop=True)
video.play()
mywin.flip()
