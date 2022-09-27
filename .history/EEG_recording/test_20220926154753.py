from psychopy import visual, core, event,monitors
from config import *
file = 'left.avi'
mywin = visual.Window(SCREEN_SIZE, color="black",monitor="Experiment Monitor" , units='norm') 
video = visual.VlcMovieStim(mywin,file,pos = (0, 100) ,loop = False,volume = 0)
video.loadMovie(file)
video.setVolume(0)
video.play()
while True:
    video.draw(mywin)
    if video.isFinished:
        break