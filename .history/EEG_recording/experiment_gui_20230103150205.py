import psychopy
from psychopy import visual, core, event,monitors
from data_utils import *
from utils import get_filenames_in_path
import logging
from turtle import color
from config import *
from psychopy.visual import vlcmoviestim
from beeply.notes import *
import sounddevice as sd
import soundfile as sf
import random
from database import Database
import concurrent.futures 
#Stimuli
stimuli = []
a = beeps(800)

logging.basicConfig(filename=NAME,filemode='a')
logging.getLogger('PIL').setLevel(logging.WARNING)
logging.getLogger().setLevel(logging.DEBUG)
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

def draw_Selection(ex_type,stim,num_list,board_shim,mywin):
    mywin.flip()
    a.hear('A_')
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        for trials in range(NUM_TRIAL):
            drawFixation(FIXATION_TIME,board_shim,mywin)     
            if PLAY_SOUND == True:
                    data, fs = sf.read(SOUND_DICT[num_list[trials]])
                    sd.play(data, fs)
                    sd.wait()
            if ex_type == 2:
                drawTrial(f"{stim[num_list[trials]]}",BLOCK_MARKER[num_list[trials]],STIM_TIME,board_shim,mywin)
            elif ex_type == 3:
                playVideo(f"{stim[num_list[trials]]}",BLOCK_MARKER[num_list[trials]],STIM_TIME,board_shim,mywin)
            drawFixation(FIXATION_TIME,board_shim,mywin)
            
            #Online
            if IS_ONLINE == True:
                print("save and send") 
                drawTextOnScreen('Save & Send',mywin)
                #Get data from board
                data = board_shim.get_board_data()
                data_copy = data.copy()
                #sending and predict
                raw = getdata(data_copy,0,n_samples=250,dropEnable=DROPENABLE)
                file_name = f'{ONLINE_ID}R{trials+1:02d}'
                save_raw(raw,file_name,ONLINE_FOLDER)
                drawTextOnScreen('Sending',mywin)
                temp:ndarray = data_copy.copy()
                database = Database(values=temp,names=file_name)
                print(database.value.shape)
                                        
                #thread 1 pack
                executor.submit(database.locked_update,1)
                core.wait(0.1)
                                        
                #thread 2 send                
                drawTextOnScreen('Sending',mywin)
                executor.submit(send_raw,database)
                                        
                core.wait(7)
                drawTextOnScreen('',mywin)
                a.hear('A_')
                throw_data = board_shim.get_board_data()        
                
def startExperiment(ex_type,board,mywin):
    global IS_FINISH
    data = board.get_board_data()
    if NO_RANDOM ==  True:
        numIm_list = STIMULIT_SEQUENCE
        numVi_list = STIMULIT_SEQUENCE
    else: 
        image_list,numIm_list,video_list,numVi_list = randomStimuli(NUM_TRIAL)
    #basesline
    if ex_type == 1:
        drawBaselinerun(BASELINE_EYEOPEN,BASELINE_EYECLOSE,board,BOARD_ID,mywin)
        IS_FINISH = True
    #executed
    elif ex_type == 2:
        logging.info(f"Execute: {numIm_list}")
        print(f"execute{numIm_list}")
        PLAY_VIDEO = False
        stim = IMAGE_DICT
        draw_Selection(ex_type,stim,numIm_list,board,mywin)
        if IS_ONLINE == False:
            #saving
            block_name = f'{PARTICIPANT_ID}R{ORDER_NUM:02d}' 
            data = board.get_board_data()
            data_copy = data.copy()
            raw = getdata(data_copy,BOARD_ID,n_samples = 250,dropEnable = DROPENABLE)
            save_raw(raw,block_name,RECORDING_DIR)
            IS_FINISH = True
            
    #Imagine
    elif ex_type == 3:
        logging.info(f"Imagined: {numVi_list}")
        print(f"imagine{numVi_list}")
        PLAY_VIDEO = True
        stim = VIDEO_DICT[VIDEO_ORDER]
        draw_Selection(ex_type,stim,numVi_list,board,mywin)
        if IS_ONLINE == False:
            #saving
            block_name = f'{PARTICIPANT_ID}R{ORDER_NUM:02d}' 
            data = board.get_board_data()
            data_copy = data.copy()
            raw = getdata(data_copy,BOARD_ID,n_samples = 250,dropEnable = DROPENABLE)
            save_raw(raw,block_name,RECORDING_DIR)
            IS_FINISH = True
    
    return IS_FINISH