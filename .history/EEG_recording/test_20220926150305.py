from psychopy import visual, core, event,monitors
from config import *
file = 'left.avi'
mywin = visual.Window(SCREEN_SIZE, color="black",monitor="Experiment Monitor" , units='norm') 
video = visual.MovieStim(mywin,file, loop = False)
video.loadMovie(file)
video.play()
#mywin.flip()

while  True:
    