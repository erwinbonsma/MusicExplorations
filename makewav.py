import math
import wave
import struct
from functools import partial

data_size = 40000
fname = "WaveTest.wav"
frate = 11025.0  # framerate as a float
amp = 16000.0    # multiplier for amplitude

freqs = [
    261.63, # C
    329.63, # E
    392.00  # G
]

def sine_wave(x, freq):
    return math.sin(2 * math.pi * freq * (x/frate))

funs = [
    partial(sine_wave, freq=freq) for freq in freqs
]

print("#funs = %d" % (len(funs)))

sine_list_x = []
for x in range(data_size):
    s = sum([fun(x) for fun in funs])
    sine_list_x.append(s)

wav_file = wave.open(fname, "w")

nchannels = 1
sampwidth = 2
framerate = int(frate)
nframes = data_size
comptype = "NONE"
compname = "not compressed"

wav_file.setparams((nchannels, sampwidth, framerate, nframes,
    comptype, compname))

for s in sine_list_x:
    # write the audio frames to file
    wav_file.writeframes(struct.pack('h', int(s*amp/2)))

wav_file.close()