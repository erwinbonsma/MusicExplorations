import math
import wave
import struct
from functools import partial

sampwidth = 1
duration = 3 # in seconds
fname = "WaveTest.wav"
frate = 11025.0  # framerate as a float
output_steps = 256 # 1024
stepsize = int(256**sampwidth / output_steps)
input_max = 3 # Maximum value of input (it will be clipped when it exceeds these bounds)
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

def make_discrete(fval):
    clipped_val = min(max(fval, -input_max), input_max)
    return stepsize * math.floor(0.5 * (clipped_val / input_max) * output_steps)

funs = [
    partial(sine_wave, freq=freq) for freq in freqs
]

raw = []
for x in range(data_size):
    summed = sum([fun(x) for fun in funs])
    stepped = make_discrete(summed)
    print("%f -> %d" % (summed, stepped))
    raw.append(stepped)

wav_file = wave.open(fname, "w")

nchannels = 1
framerate = int(frate)
nframes = data_size
comptype = "NONE"
compname = "not compressed"

wav_file.setparams((nchannels, sampwidth, framerate, nframes, comptype, compname))

for output in raw:
    # write the audio frames to file
    if sampwidth == 1:
        wav_file.writeframes(struct.pack('B', 128 + output))
    else:
        wav_file.writeframes(struct.pack('h', output))

wav_file.close()