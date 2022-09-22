import psychopy
from psychopy import visual, core, event,monitors
from data_utils import save_raw,getdata,getepoch,save_raw_to_dataframe
from utils import get_filenames_in_path
import logging
from turtle import color
logging.getLogger('PIL').setLevel(logging.WARNING)
from config import *
#==============================================
# Configuration
#==============================================
def drawTextOnScreen(massage) :
    message = visual.TextStim( mywin, text=massage, languageStyle='LTR',bold=True,color=[89, 206, 143],colorSpace='rgb')
    message.contrast =  0.3
    message.height= 0.10
    message.width = 0.10
    message.draw() # draw on screen
    mywin.flip()   # refresh to show what we have draw

def drawTrial(imgPath, mark, stimTime,board) :
    drawTextOnScreen('') 
    core.wait(STIM_BLINK_TIME)
    img = visual.ImageStim( mywin,  image=imgPath )
    img.size *= 1.5
    img.draw()
    mywin.flip()
    eegMarking(board,mark)
    core.wait(stimTime)
    
def drawFixation(fixationTime,board):
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