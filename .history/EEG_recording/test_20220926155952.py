from turtle import left
from psychopy import visual, core, event,monitors
from psychopy.visual import VlcMovieStim
from config import *
import vlc
file = 'left.avi'
'''mywin = visual.Window(SCREEN_SIZE, color="black",monitor="Experiment Monitor" , units='norm') 
video = visual.VlcMovieStim(mywin,file)
video.loadMovie(file)
video.setVolume(0)
video.play()
while True:
    video.draw(mywin)
    if video.isFinished:
        break'''
        
# creating vlc media player object
media = vlc.MediaPlayer(file)
 
# start playing video
media.play()