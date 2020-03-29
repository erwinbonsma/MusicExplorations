import math
import wave
import struct
from functools import partial

sampwidth = 2
duration = 3 # in seconds
fname = "WaveTest.wav"
frate = 11025.0  # framerate as a float
amp = 84 * 256**(sampwidth - 1) # multiplier for amplitude
data_size = int(frate * duration)

freqs = [
    261.63, # C
    329.63, # E
    392.00  # G
]

# Normalized frequency such that period is an integer-number of samples
nfreqs = [
    frate / round(frate / freq) for freq in freqs
]

def sine_wave(x, freq):
    return math.sin(2 * math.pi * freq * (x/frate))

def square_wave(x, freq):
    return math.copysign(1, sine_wave(x, freq))

funs = [
    partial(sine_wave, freq=freq) for freq in nfreqs
]

sine_list_x = []
for x in range(data_size):
    s = sum([fun(x) for fun in funs])
    sine_list_x.append(s)

wav_file = wave.open(fname, "w")

nchannels = 1
framerate = int(frate)
nframes = data_size
comptype = "NONE"
compname = "not compressed"

wav_file.setparams((nchannels, sampwidth, framerate, nframes, comptype, compname))

for s in sine_list_x:
    # write the audio frames to file
    if sampwidth == 1:
        wav_file.writeframes(struct.pack('B', 128 + int(s*amp/2)))
    else:
        wav_file.writeframes(struct.pack('h', int(s*amp/2)))

wav_file.close()