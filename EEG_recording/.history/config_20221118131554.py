#Image config
from array import array


#Application config
#==============================================
# experiment parameters
#==============================================
#[1366,768]
#[1536,864]
SCREEN_SIZE:array = [1536,864]
TOTAL_IMAGE:int = 2
NUM_TRIAL:int = 6 #30
NUM_BLOCK:int = 4 #4
NUM_SESSION:int = 2 #3
STIM_CHECK = 0
# baseline run
IS_BASELINE:bool = False
BASELINE_EYEOPEN:int = 60 #60second
BASELINE_EYECLOSE:int = 60 #60second
ALERT_TIME:int = 800 #8second 
INSTRUCTION_TIME:int = 2 
#stimuli time (left arrow and right arrow)
STIM_TIME:int = 3 #4second
STIM_BLINK_TIME:int = 0 #0second
FIXATION_TIME:int = 2 #10 "+" inter trial interval
EXE_COUNT:int = 0
IMAGINE_COUNT:int = 0
EXECUTE_NO:array=[3,5,7,9,11,13]
IMAGINE_NO:array=[4,6,8,10,12,14]
BLOCK_BREAK = 1#240 second, 4  min
SESSION_BREAK = 300 #600 second, 10 min

#EEG config
TIME_OUT = 0
IP_PORT = 0
IP_PROTOCOL = 0
IP_ADDRESS =''
BOARD_ID =  -1 #0
SERIAL_PORT = '' #COM3
MAC_ADDRESS = ''
OTHER = ''
STREAMER_PARAMS = ''
SERIAL_NUMBER = ''
FILE = ''
MASTER_BOARD = 0
PRESET = 0

#Marker config
#BLOCK_DICT:dict[int,str] = {1:'execute_left',2:'executed_right',3:'imagine_left',4:'imagine_right' }
BLOCK_DICT:dict[int,str] = {1:'execute',2:'imagine',3:'executed',4:'imagine' }
#BLOCK_MARKER:dict = {1:1.0 , 2:2.0}
BLOCK_MARKER:dict = {0:1.0 , 1:2.0}
SOUND_DICT:dict[int,str] = {0:'./sound/Left.wav',1:'./sound/Right.wav'}
IS_VIDEO = True
PLAY_VIDEO = False
PLAY_SOUND = False

#Record config
NAME:str = 'New'
PARTICIPANT_ID:str = 'S027'
RECORDING_DIR:str = 'record/'
CSV_DIR:str = 'csv/'
TYPE_OF_FILE ='.fif'
FIG_FILE = '.png'
FOLDER:str = 'EEG_recording/'
CATEGORIES:list[str] = ['left','right']
IMAGE_FOLDER:str = 'images/'
VIDEO_FOLDER:str = 'video/'
ERD_FOLDER:str = 'erd/'


CALIBRATION = True
