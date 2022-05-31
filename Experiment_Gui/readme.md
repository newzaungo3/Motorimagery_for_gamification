On Linux and Mac

import os
duration = 1  # seconds
freq = 440  # Hz
os.system('play -nq -t alsa synth {} sine {}'.format(duration, freq))


In order to use this example, you must install sox.

On Debian / Ubuntu / Linux Mint, run this in your terminal:

sudo apt install sox

sudo apt install speech-dispatcher