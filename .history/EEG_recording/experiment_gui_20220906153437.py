import psychopy
from psychopy import visual, core, event,monitors
from data_utils import save_raw,getdata,getepoch,save_raw_to_dataframe
from utils import get_filenames_in_path
import logging
from turtle import color
logging.getLogger('PIL').setLevel(logging.WARNING)
from config import *
from beeply.notes import *
#Stimuli
stimuli = []
a = beeps(800)

def get_stimuli():
    #ubuntu, delete folder
    for cat in CATEGORIES:
        l = get_filenames_in_path(f"{IMAGE_FOLDER}{cat}")
        stimuli.append(f'{IMAGE_FOLDER}{cat}{"/"}{l[0]}')
    return stimuli


#==============================================
# Configuration
#==============================================
def drawTextOnScreen(massage,mywin) :
    message = visual.TextStim( mywin, text=massage, languageStyle='LTR',bold=True,color=[89, 206, 143],colorSpace='rgb')
    message.contrast =  0.3
    message.height= 0.10
    message.width = 0.10
    message.draw() # draw on screen
    mywin.flip()   # refresh to show what we have draw

def drawTrial(imgPath, mark, stimTime,board,mywin) :
    drawTextOnScreen('') 
    core.wait(STIM_BLINK_TIME)
    img = visual.ImageStim( mywin,  image=imgPath )
    img.size *= 1.5
    img.draw()
    mywin.flip()
    eegMarking(board,mark)
    core.wait(stimTime)
    
def drawFixation(fixationTime,board,mywin):
    fixation = visual.ShapeStim(mywin,
                                vertices=((0, -0.5), (0, 0.5), (0,0), (-0.5,0), (0.5, 0)),
                                lineWidth=5,
                                closeShape=False,
                                lineColor="white"
            )
    fixation.draw()      
    mywin.flip()   # refresh to show what we have draw
    eegMarking(board,4.0)
    core.wait(fixationTime-0.5)
    drawTextOnScreen('')
    core.wait(0.5)

def eegMarking(board,marker):   # use trial variable from main
    if marker == 0:
        print("Marker string Left")
    elif marker == 1.0:
        print("Marker string Right" )
    elif marker == 2.0:
        print("Marker string Idle")
    elif marker == 3.0:
        print("Marker string Fixation")
    board.insert_marker(marker)