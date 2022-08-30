#Image config
from array import array

FOLDER:str = 'EEG_recording/'
CATEGORIES:list[str] = ['left','right']
IMAGE_FOLDER:str = 'images/'

#Application config
#==============================================
# experiment parameters
#==============================================
SCREEN_SIZE:array = [1920, 1000]
TOTAL_IMAGE:int = 2
NUM_TRIAL:int = 3 #12
NUM_BLOCK:int = 4 #4
NUM_SESSION:int = 3 #3
# baseline run
BASELINE_EYEOPEN:int = 1 #60second
BASELINE_EYECLOSE:int = 1 #60second
ALERT_TIME:int = 800 #8second 
INSTRUCTION_TIME:int = 2 
#stimuli time (left arrow and right arrow)
STIM_TIME:int = 1 #5second
STIM_BLINK_TIME:int = 0 #0second
FIXATION_TIME:int = 3 #10 "+" inter trial interval
BLOCK_COUNT:int = 1
EXECUTE_NO:array=[3,5,7,9]
IMAGINE_NO:array[4,6,8,10]

#EEG config
TIME_OUT = 0
IP_PORT = 0
IP_PROTOCOL = 0
IP_ADDRESS =''
BOARD_ID = 0
SERIAL_PORT = 'COM3'
MAC_ADDRESS = ''
OTHER = ''
STREAMER_PARAMS = ''
SERIAL_NUMBER = ''
FILE = ''
MASTER_BOARD = 0
PRESET = 0

#Marker config
BLOCK_DICT:dict[int,str] = {1:'execute_left',2:'executed_right',3:'imagine_left',4:'imagine_right' }
BLOCK_MARKER:dict = {1:1.0 , 2:2.0 , 3:1.0 , 4:2.0 }


#Record config
NAME:str = 'PONGKORN'
PARTICIPANT_ID:str = 'S001'
RECORDING_DIR:str = 'record/'
CSV_DIR:str = 'csv/'
