from psychopy import visual, core, event,monitors
from config import *
file = 'left.avi'
mywin = visual.Window(SCREEN_SIZE, color="black",monitor="Experiment Monitor" , units='norm') 
video = visual.VlcMovieStim(mywin,file,pos = (0, 100) ,loop = False,volume = 0)
video.loadMovie(file)
print(video.volume)
video.play()
while True:
    video.draw()
    if video.isFinished:
        break