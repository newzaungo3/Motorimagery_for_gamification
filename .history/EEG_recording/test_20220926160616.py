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
        
import time, vlc
 
# method to play video
def video(source):
     
    # creating a vlc instance
    vlc_instance = vlc.Instance()
     
    # creating a media player
    player = vlc_instance.media_player_new()
     
    # creating a media
    media = vlc_instance.media_new(source)
     
    # setting media to the player
    player.set_media(media)
     
    # play the video
    player.play()
     
    # wait time
    time.sleep(0.5)
     
    # getting the duration of the video
    duration = player.get_length()
     
    # printing the duration of the video
    print("Duration : " + str(duration))
     
# call the video method
video(file)