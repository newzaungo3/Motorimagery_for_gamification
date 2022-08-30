from config import *
import os 
from pathlib import Path
if os.path.isdir(os.path.join(RECORDING_DIR, PARTICIPANT_ID)):
    Path(os.path.join(RECORDING_DIR, PARTICIPANT_ID)).mkdir(exist_ok=True)