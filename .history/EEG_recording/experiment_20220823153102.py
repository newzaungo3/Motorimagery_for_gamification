import argparse
import logging
import keyboard
import pyqtgraph as pg
import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds, BrainFlowPresets
from brainflow.data_filter import DataFilter, FilterTypes,DetrendOperations,WindowOperations
from pyqtgraph.Qt import QtGui, QtCore,QtWidgets
from unicodedata import category
from beeply.notes import *
import pylsl
import time
import itertools
import math
import psychopy
from psychopy import visual, core, event,monitors
from datetime import datetime
from IPython.display import clear_output
import random
from numpy.random import default_rng
import sys


from utils import get_filenames_in_path

#==============================================
# Image setup
#==============================================
folder = 'EEG_recording/'
image = 'images/'
categories = ['left','right']
stimuli = []

#ubuntu, delete folder
for cat in categories:
    l = get_filenames_in_path(f"{image}{cat}")
    stimuli.append(f'{image}{cat}{"/"}{l[0]}')

print(stimuli)
#==============================================
# experiment parameters
#==============================================
#Widowsetting

screen_size = [1920, 1000]
#screen_size = [800,600]
#category
a = beeps(800)

#left and right image
total_image = 2
num_trial = 3 #12
num_block = 4 #4
num_session = 1 #3

# baseline run
baseline_eyeopen = 5 #60second
baseline_eyeclose = 5 #60second
alert_time = 800 #8second 
instruction_time = 2 
#stimuli time (left arrow and right arrow)
stim_time = 1 #5second
stim_blink_time = 0 #0second
fixation_time = 3 #10 "+" inter trial interval

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
    a.hear('A_')
    drawFixation(fixation_time)

    #close
    drawTextOnScreen("Baseline run 2: Close eyes (estimated time: 60 second)")
    core.wait(3)
    drawTextOnScreen('')
    eegMarking("Baseline_closeeye")
    core.wait(closeTime)
    #alert
    mywin.flip()
    a.hear('A_')
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
# Setup EEG board
BoardShim.enable_dev_board_logger()
logging.basicConfig(level=logging.DEBUG)

parser = argparse.ArgumentParser()
# use docs to check which parameters are required for specific board, e.g. for Cyton - set serial port
parser.add_argument('--timeout', type=int, help='timeout for device discovery or connection', required=False,
                        default=0)
parser.add_argument('--ip-port', type=int, help='ip port', required=False, default=0)
parser.add_argument('--ip-protocol', type=int, help='ip protocol, check IpProtocolType enum', required=False,
                        default=0)
parser.add_argument('--ip-address', type=str, help='ip address', required=False, default='')
parser.add_argument('--serial-port', type=str, help='serial port', required=False, default='')
parser.add_argument('--mac-address', type=str, help='mac address', required=False, default='')
parser.add_argument('--other-info', type=str, help='other info', required=False, default='')
parser.add_argument('--streamer-params', type=str, help='streamer params', required=False, default='')
parser.add_argument('--serial-number', type=str, help='serial number', required=False, default='')
parser.add_argument('--board-id', type=int, help='board id, check docs to get a list of supported boards',
                        required=False, default=BoardIds.SYNTHETIC_BOARD)
parser.add_argument('--file', type=str, help='file', required=False, default='')
parser.add_argument('--master-board', type=int, help='master board id for streaming and playback boards',
                        required=False, default=BoardIds.NO_BOARD)
parser.add_argument('--preset', type=int, help='preset for streaming and playback boards',
                        required=False, default=BrainFlowPresets.DEFAULT_PRESET)
args = parser.parse_args()

#brainflow initialization 
params = BrainFlowInputParams()
params.ip_port = args.ip_port
params.serial_port = args.serial_port
params.mac_address = args.mac_address
params.other_info = args.other_info
params.serial_number = args.serial_number
params.ip_address = args.ip_address
params.ip_protocol = args.ip_protocol
params.timeout = args.timeout
params.file = args.file
params.master_board = args.master_board
params.preset = args.preset
board_shim = BoardShim(args.board_id, params)

#board prepare
try:
    board_shim.prepare_session()
except brainflow.board_shim.BrainFlowError as e:
    print(f"Error: {e}")
    print("The end")
    time.sleep(1)
    sys.exit()
#board start streaming
board_shim.start_stream(450000, "file://brainflow_data.csv:w")
#draw start screen
mywin = visual.Window(screen_size, color="black",monitor="testMonitor" , units='norm') 

##############################################
# Experiment session
##############################################
#begin experiment and collect data with brainflow(while loop)
logging.info("Begin experiment")
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
                    core.wait(1)
                    drawTextOnScreen("")
                    core.wait(0.5)
                    if block+1 == 1 or block+1 == 2 :
                        stim = stimuli[0]
                    else:
                        stim = stimuli[1]
                    print(stim)
                    drawTrial(f"{stim}",f"{block_dict[block+1]}_{trials+1}_{session+1}",stim_time)
                    a.hear('A_')
                    drawFixation(fixation_time)
        drawTextOnScreen('End of experiment, Thank you')
        
        stop  = time.time()
        print(f"Total experiment time = {(stop-start)/60} ")
        core.wait(10)
        break
logging.info('End')
if board_shim.is_prepared():
        logging.info('Releasing session')
        data = board.get_board_data()  # get all data and remove it from internal buffer
        board_shim.stop_stream()
        board_shim.release_session()
        print("data")
        print(data.shape)
mywin.close()