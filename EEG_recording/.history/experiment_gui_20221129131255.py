import psychopy
from psychopy import visual, core, event,monitors
from data_utils import save_raw,getdata,getepoch,save_raw_to_dataframe,randomStimuli
from utils import get_filenames_in_path
import logging
from turtle import color
logging.getLogger('PIL').setLevel(logging.WARNING)
from config import *
from psychopy.visual import vlcmoviestim
from beeply.notes import *
import sounddevice as sd
import soundfile as sf
import random
#Stimuli
stimuli = []
a = beeps(800)

def get_stimuli():
    #ubuntu, delete folder
    for cat in CATEGORIES:
        l = get_filenames_in_path(f"{IMAGE_FOLDER}{cat}")
        v = get_filenames_in_path(f"{VIDEO_FOLDER}{cat}")
        stimuli.append(f'{IMAGE_FOLDER}{cat}{"/"}{l[0]}')
        stimuli.append(f'{VIDEO_FOLDER}{cat}{"/"}{v[0]}')
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
    drawTextOnScreen('',mywin) 
    core.wait(STIM_BLINK_TIME)
    img = visual.ImageStim( mywin,  image=imgPath )
    img.size *= 1.5
    img.draw()
    mywin.flip()
    eegMarking(board,mark)
    core.wait(stimTime)

def drawERD(imgPath,mywin):
    drawTextOnScreen('Drawing',mywin)
    core.wait(1)
    img = visual.ImageStim( mywin,  image=imgPath )
    img.size *= 1.5
    img.draw()
    mywin.flip()
    
    
def drawFixation(fixationTime,board,mywin):
    mywin.flip()
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
    drawTextOnScreen('',mywin)
    core.wait(0.5)

def eegMarking(board,marker):   # use trial variable from main
    if marker == 1.0:
        print("Marker string Left")
    elif marker == 2.0:
        print("Marker string Right" )
    elif marker == 3.0:
        print("Marker string Idle")
    elif marker == 4.0:
        print("Marker string Fixation")
    board.insert_marker(marker)
    
def drawBaselinerun(openTime,closeTime,board,board_id,mywin):
    baseline_open_name = f'{PARTICIPANT_ID}R{1:02d}'
    #throw data
    data = board.get_board_data() 
    #Baseline run
    #open
    drawTextOnScreen("Baseline run 1: Open eyes (estimated time: 60 second)",mywin)
    core.wait(3)
    drawTextOnScreen('',mywin)
    eegMarking(board,3.0)
    core.wait(openTime)
    #alert
    mywin.flip()
    a.hear('A_')
    drawFixation(FIXATION_TIME,board,mywin)
    
    #save baselinefile to mne and .fif
    #remove buffer
    #next experiment will no have baseline signal
    data = board.get_board_data()
    data_copy = data.copy()
    raw = getdata(data_copy,board_id,n_samples = 250)
    save_raw(raw,baseline_open_name,RECORDING_DIR)   
    
    #close
    baseline_close_name = f'{PARTICIPANT_ID}R{2:02d}'
    drawTextOnScreen("Baseline run 2: Close eyes (estimated time: 60 second)",mywin)
    core.wait(3)
    drawTextOnScreen('',mywin)
    eegMarking(board,3.0)
    core.wait(closeTime)
    #alert
    mywin.flip()
    a.hear('A_')
    drawFixation(FIXATION_TIME,board,mywin)
    
    #save baselinefile to mne and .fif
    #remove buffer
    #next experiment will have no baseline signal
    data = board.get_board_data()
    data_copy = data.copy()
    raw = getdata(data_copy,board_id,n_samples = 250)
    save_raw(raw,baseline_close_name,RECORDING_DIR)
    

def playVideo(videoPath, mark, stimTime,board,mywin):
    mywin.flip()
    video = vlcmoviestim.VlcMovieStim(mywin,videoPath)
    video.loadMovie(videoPath)
    video.setVolume(0)
    video.play()
    eegMarking(board,mark)
    while True:
        video.draw(mywin)
        mywin.flip()
        if video.frameTime >= STIM_TIME:
            break

def draw_Selection(ex_type,num_list,board_shim,mywin):
    for trials in range(NUM_TRIAL):
        drawFixation(FIXATION_TIME,board_shim,mywin)     
        if PLAY_VIDEO == True:
            if PLAY_SOUND == True:
                data, fs = sf.read(SOUND_DICT[numVi_list[trials]])
                sd.play(data, fs)
                sd.wait()
            #playVideo(f"{stim}",Marker,STIM_TIME,board_shim,mywin)
            print(f"{stim[numVi_list[trials]]}")
                            
            playVideo(f"{stim[numVi_list[trials]]}",BLOCK_MARKER[numVi_list[trials]],STIM_TIME,board_shim,mywin)
            
            drawFixation(FIXATION_TIME,board_shim,mywin)
            STIM_CHECK += 1
            print(STIM_CHECK)
        else:
            if PLAY_SOUND == True:
                data, fs = sf.read(SOUND_DICT[numIm_list[trials]])
                sd.play(data, fs)
                sd.wait()
            print(BLOCK_MARKER[numIm_list[trials]])
            drawTrial(f"{stim[trials]}",BLOCK_MARKER[numIm_list[trials]],STIM_TIME,board_shim,mywin)
            drawFixation(FIXATION_TIME,board_shim,mywin)
            STIM_CHECK += 1
            print(STIM_CHECK)
        #new
        if PLAY_SOUND == True:
                data, fs = sf.read(SOUND_DICT[numIm_list[trials]])
                sd.play(data, fs)
                sd.wait()
        print(BLOCK_MARKER[num_list[trials]])
        if ex_type == 2:
            drawTrial(f"{stim[trials]}",BLOCK_MARKER[num_list[trials]],STIM_TIME,board_shim,mywin)
        elif ex_type == 3:
            playVideo(f"{stim[num_list[trials]]}",BLOCK_MARKER[num_list[trials]],STIM_TIME,board_shim,mywin)
        drawFixation(FIXATION_TIME,board_shim,mywin)        
                
def startExperiment(ex_type,board,mywin):
    print('hello')
    image_list,numIm_list,video_list,numVi_list = randomStimuli(NUM_TRIAL)
    #basesline
    if ex_type == 1:
        drawBaselinerun(BASELINE_EYEOPEN,BASELINE_EYECLOSE,board,BOARD_ID,mywin)
        
    #executed
    elif ex_type == 2:
        PLAY_VIDEO = False
        stim = image_list
        print("execute")
    #Imagine
    elif ex_type == 3:
        PLAY_VIDEO = True
        num = random.randint(0,1)
        stim = image_list
        print("imagine")
    
    