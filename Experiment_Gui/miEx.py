import random
from unicodedata import category
import pylsl
import numpy as np
import pandas as pd
import time
import itertools
import math
import psychopy 
from psychopy import visual, core, event,monitors
from datetime import datetime
from IPython.display import clear_output
import random
from numpy.random import default_rng
import statistics
import csv
import os.path
import winsound

from utils import get_filenames_in_path

#==============================================
# Image setup
#==============================================
folder = 'experiment/'
image = 'images/'
categories = ['left','right']
stimuli = []

for cat in categories:
    l = get_filenames_in_path(f"{folder}{image}{cat}")
    stimuli.append(f'{folder}{image}{cat}{"/"}{l[0]}')

print(stimuli)
#==============================================
# experiment parameters
#==============================================
#Widowsetting

screen_size = [1920, 1000]
#screen_size = [800,600]
#category

#left and right image
total_image = 2
num_trial = 12 #12
num_block = 4 #4
num_session = 3 #3

# baseline run
baseline_eyeopen = 60 #60second
baseline_eyeclose = 60 #60second
alert_time = 800 #8second 
instruction_time = 10 
#stimuli time (left arrow and right arrow)
stim_time = 5 #5second
stim_blink_time = 0 #0second
fixation_time = 8 #10 "+" inter trial interval

#เวลาทั้งหมด = (4 block * 12 trials * 3 session * 5 second) + (10 second(instruction))+(120 second(baseline))+(50 second(fixation)*3session)
experiment_time = (num_block*num_trial*num_session*stim_time)+(instruction_time)+(baseline_eyeclose+baseline_eyeopen)+(fixation_time*5*3)
print(f"Total experiment time = {'{:.2f}'.format(math.ceil(experiment_time/60))} Minute" )

#==============================================
# Configuration
#==============================================

#name, type, channel_count, sampling rate, channel format, source_id
#info = StreamInfo('CytonMarkers', 'Markers', 1, 0.0, 'int32', 'CytonMarkerID')#make an outlet
info = pylsl.StreamInfo('CytonMarkers', 'Markers', 1, 0.0, 'string', 'CytonMarkerID')#make an outlet
outlet = pylsl.StreamOutlet(info)
# %whos

def drawTextOnScreen(massage) :
    message = visual.TextStim( mywin, text=massage, languageStyle='LTR')
    message.contrast =  0.3
    message.height= 0.07
    message.draw() # draw on screen
    mywin.flip()   # refresh to show what we have draw

def drawTrial( imgPath, mark, stimTime ) :
    drawTextOnScreen('') 
    core.wait(stim_blink_time)
    img = visual.ImageStim( mywin,  image=imgPath )
    img.size *= 1.5
    img.draw()
    mywin.flip()
    eegMarking(mark)
    core.wait(stimTime)
    
def drawFixation(fixationTime):
    fixation = visual.ShapeStim(mywin,
                                vertices=((0, -0.5), (0, 0.5), (0,0), (-0.5,0), (0.5, 0)),
                                lineWidth=5,
                                closeShape=False,
                                lineColor="white"
            )
    fixation.draw()
    # if not(isTrianing) :
    # text = f"Block {block+1} / {len(blocks_imgs)}"
    # message = visual.TextStim( mywin, text=text, languageStyle='LTR' )
    # message.contrast =  0.3
    # message.pos = (0, -0.6)
    # message.draw() # draw on screen
        
    mywin.flip()   # refresh to show what we have draw
    eegMarking('-1')
    core.wait(fixationTime-0.5)
    drawTextOnScreen('')
    core.wait(0.5)
def drawBaselinerun(openTime,closeTime):
    #Baseline run
    #open
    drawTextOnScreen("Baseline run 1: Open eyes (estimated time: 60 second)")
    core.wait(3)
    drawTextOnScreen('')
    eegMarking("Baseline_openeye")
    core.wait(openTime)
    #alert
    mywin.flip()
    winsound.Beep(440, alert_time)
    drawFixation(fixation_time)

    #close
    drawTextOnScreen("Baseline run 2: Close eyes (estimated time: 60 second)")
    core.wait(3)
    drawTextOnScreen('')
    eegMarking("Baseline_closeeye")
    core.wait(closeTime)
    #alert
    mywin.flip()
    winsound.Beep(440, alert_time)
    drawFixation(fixation_time)
    
def eegMarking(markerString):   # use trial variable from main
    # if not isTrianing :
    # if stampType == "img_stim" :
    #     markerString = str(block+1) + "," + str(trial) + ","  + str(img)
    # elif stampType == "fixation" :
    #     markerString = str((block+1)*-1) + "," +str("Fixation") + "," + str("Fixation")
    # else:
    #     markerString = 'Training'
    # markerString= str(markerString)                              
    print("Marker string {}".format(markerString))
    outlet.push_sample([markerString])
    

mywin = visual.Window(screen_size, color="black",monitor="testMonitor" , units='norm') 

##############################################
# Experiment session
##############################################

while True:
    # how to start an experiment
    drawTextOnScreen('Experiment session : Press space bar to start')
    keys = event.getKeys()
    if 'space' in keys:      # If space has been pushed
        start = time.time()
        drawTextOnScreen('') 
        drawBaselinerun(baseline_eyeopen,baseline_eyeclose)
        #experiment      
        #3 session
        for session in range(num_session):
            # 4 block
            for block in range(num_block):
                block_dict = {1:'execute_left',2:'imagine_left',3:'executed_right',4:'imagine_right'}
                #12 trials
                for trials in range(num_trial):
                    drawTextOnScreen(f"Session:{session+1}_Block:{block+1}({block_dict[block+1]})_Trials:{trials+1}")
                    core.wait(5)
                    drawTextOnScreen("")
                    core.wait(0.5)
                    if block+1 == 1 or block+1 == 2 :
                        stim = stimuli[0]
                    else:
                        stim = stimuli[1]
                    print(stim)
                    drawTrial(f"{stim}",f"{block_dict[block+1]}_{trials+1}_{session+1}",stim_time)
                    winsound.Beep(440, alert_time)
                    drawFixation(fixation_time)
        drawTextOnScreen('End of experiment, Thank you')
        
        stop  = time.time()
        print(f"Total experiment time = {(stop-start)/60} ")
        core.wait(10)
        break

mywin.close()