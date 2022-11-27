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
NUM_TRIAL:int = 20 #20
NUM_BLOCK:int = 4 #4
NUM_SESSION:int = 2 #3
STIM_CHECK = 0
# baseline run
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

#EXECUTE_NO:array=[7,9,11,13]
#IMAGINE_NO:array=[8,10,12,14]
BLOCK_BREAK = 120 #120 second, 2  min
SESSION_BREAK = 300 #300 second, 5 min

#EEG config
TIME_OUT = 0
IP_PORT = 0
IP_PROTOCOL = 0
IP_ADDRESS =''
BOARD_ID =  0 #0
SERIAL_PORT = 'COM7' #COM6
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
BLOCK_MARKER:dict = {0:1.0 , 1:2.0}
SOUND_DICT:dict[int,str] = {0:'./sound/Left.wav',1:'./sound/Right.wav'}
IMAGE_DICT:dict[int,str] = {0:'./images/left/left.png',1:'./images/right/right.png'}
VIDEO_DICT = [
 { 0:'./video/left/left.avi', 1: './video/right/right.avi' },
 { 0: './video/left/left2.avi', 1: './video/right/right2.avi' },
 ]
IS_VIDEO:bool = True
PLAY_VIDEO:bool = False
PLAY_SOUND:bool = False

CALIBRATION:bool = False
DROPENABLE:bool = False

IS_BASELINE:bool = False

#Record config
NAME:str = 'new'
PARTICIPANT_ID:str = 'S036_35000000'
RECORDING_DIR:str = 'record/'
CSV_DIR:str = 'csv/'
TYPE_OF_FILE ='.fif'
FIG_FILE = '.png'
FOLDER:str = 'EEG_recording/'
CATEGORIES:list[str] = ['left','right']
IMAGE_FOLDER:str = 'images/'
VIDEO_FOLDER:str = 'video/'
ERD_FOLDER:str = 'erd/'
ONLINE_FOLDER:str = 'online/'



